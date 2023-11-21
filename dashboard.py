import streamlit as st 
import plotly.express as px
import pandas as pd 
import os 
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="jobinja Dashboard", page_icon=":bar_chart", layout="wide")

st.write(unsafe_allow_html=True)
st.write('<style>body {direction: ltr;}</style>', unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    os.chdir(r"/home/maryam/Desktop/git-projects/jobinja_dashboard/")
    df = pd.read_csv("jobinja_with_date_embeddings.csv")

col1, col2 = st.columns((2))
df["Date Posted"] = pd.to_datetime(df["Date Posted"])

startDate = pd.to_datetime(df["Date Posted"]).min()
endDate = pd.to_datetime(df["Date Posted"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Date Posted"] >= date1) & (df["Date Posted"] <= date2)].copy()

st.sidebar.header("Choose your Job Category: ")
region = st.sidebar.multiselect("Pick your Region", df["Job Location"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Job Location"].isin(region)]

type = st.sidebar.multiselect("Employment Type", df2["Employment Type"].unique())
if not type:
    df3 = df2.copy()
else:
    df3 = df2[df2["Employment Type"].isin(type)]

category = st.sidebar.multiselect("Job Category",df3["Job Category"].unique())

if not region and not type and not category:
    filtered_df = df
elif not type and not category:
    filtered_df = df[df["Job Location"].isin(region)]
elif not region and not type:
    filtered_df = df[df["Job Category"].isin(category)]
elif type and category:
    filtered_df = df3[df["Employment Type"].isin(type) & df3["Job Category"].isin(category)]
elif region and category:
    filtered_df = df3[df["Job Location"].isin(region) & df3["Job Category"].isin(category)]
elif region and type:
    filtered_df = df3[df["Job Location"].isin(region) & df3["Employment Type"].isin(type)]
elif category:
    filtered_df = df3[df3["Job Category"].isin(category)]
else:
    filtered_df = df3[df3["Job Location"].isin(region) & df3["Employment Type"].isin(type) & df3["Job Category"].isin(category)]

category_df = filtered_df.groupby('Job Category').size().reset_index()
category_df.columns = ['Job Category', 'UniqueRecordCount']

st.subheader("Category-wise Job Positions")

category_counts = df['Job Category'].value_counts().reset_index()
category_counts.columns = ['Job Category', 'Count']

fig = px.bar(category_counts, x='Count', y='Job Category', orientation='h', template='seaborn')

fig.update_layout(
    width=800,
    height=400, 
    margin=dict(l=300, r=50, t=50, b=50),
    xaxis_tickangle=0, 
)

st.plotly_chart(fig, use_container_width=True)
st.subheader("Region wise Sales")
fig = px.pie(filtered_df, names="Job Location", hole=0.2)  
fig.update_traces(text=filtered_df["Job Location"], textposition="inside")  
fig.update_xaxes(ticks="outside", tickfont=dict(size=8, color='black'))  
fig.update_layout(
    width=700,
    height=600,  
)

st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')
        

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby('Job Category').size().reset_index()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')

filtered_df["month_year"] = filtered_df["Date Posted"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Job Category"].size()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Job Category", labels = {"Job Category": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

tehran_filtered_df = filtered_df[filtered_df["Job Location"] == "تهران"]

records_count = tehran_filtered_df.groupby(["Job Location", "Job Category"]).size().reset_index(name="RecordCount")

st.subheader("Hierarchical view of Records using TreeMap (Tehran)")
fig3 = px.treemap(records_count, path=["Job Location", "Job Category"], values="RecordCount", hover_data=["RecordCount"],
                color="Job Category")
fig3.update_layout(width=800, height=650)
fig3.update_traces(textposition="middle center")
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2= st.columns((2))
with chart1:
    st.subheader('Gender')
    fig = px.pie(filtered_df, names = "Gender", template = "plotly_dark")
    fig.update_traces(text = filtered_df["Gender"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Salary')
    fig = px.pie(filtered_df, names = "Salary", template = "gridon")
    fig.update_traces(text = filtered_df["Salary"], textposition = "inside")
    st.plotly_chart(fig, use_container_width=True)


st.subheader('Company Category')
fig = px.pie(filtered_df, names="Company Category", template="gridon")
fig.update_traces(text=filtered_df["Company Category"], textposition="inside")
fig.update_layout(width=800, height=650)
st.plotly_chart(fig, use_container_width=True)
