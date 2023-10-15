import streamlit as st 
import plotly.express as px
import pandas as pd 
import os 
import warnings
from search import VectorSearch
warnings.filterwarnings('ignore')
import SentenceTransformer
import torch

MODEL_PATH = 'intfloat/multilingual-e5-large'
embedder =  SentenceTransformer(MODEL_PATH)

st.set_page_config(page_title="jobinja Dashboard", page_icon=":bar_chart", layout="wide")

    

st.write(unsafe_allow_html=True)
# Specify the text direction as RTL
st.write('<style>body {direction: ltr;}</style>', unsafe_allow_html=True)
# st.title(" :bar_chart: JoBInja EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    os.chdir(r"/home/maryam/Desktop/Personal_projects/jobinja_dashboard/")
    df = pd.read_csv("jobinja_with_date_embeddings.csv")

col1, col2 = st.columns((2))
df["Date Posted"] = pd.to_datetime(df["Date Posted"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Date Posted"]).min()
endDate = pd.to_datetime(df["Date Posted"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Date Posted"] >= date1) & (df["Date Posted"] <= date2)].copy()

st.sidebar.header("Choose your Job Category: ")
# Create for Region
region = st.sidebar.multiselect("Pick your Region", df["Job Location"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Job Location"].isin(region)]

# Create for Employment Type
type = st.sidebar.multiselect("Employment Type", df2["Employment Type"].unique())
if not type:
    df3 = df2.copy()
else:
    df3 = df2[df2["Employment Type"].isin(type)]


# Create for Job Category
category = st.sidebar.multiselect("Job Category",df3["Job Category"].unique())



# Filter the data based on Region, State and City

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

# category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()
category_df = filtered_df.groupby('Job Category').size().reset_index()
category_df.columns = ['Job Category', 'UniqueRecordCount']


# st.subheader("Category wise Jon Positions")
# fig = px.bar(category_df, x = "Job Category", y = "UniqueRecordCount",
#                 template = "seaborn")

# st.plotly_chart(fig,use_container_width=True, height = 1500)

st.subheader("Category-wise Job Positions")

# Count the occurrences of each category
category_counts = df['Job Category'].value_counts().reset_index()
category_counts.columns = ['Job Category', 'Count']

# Create the bar chart without specifying x
fig = px.bar(category_counts, x='Count', y='Job Category', orientation='h', template='seaborn')

fig.update_layout(
    width=800,
    height=400,  # Adjust the height as needed
    margin=dict(l=300, r=50, t=50, b=50),
    xaxis_tickangle=0,  # Rotate x-axis labels if needed
)

st.plotly_chart(fig, use_container_width=True)
st.subheader("Region wise Sales")
fig = px.pie(filtered_df, names="Job Location", hole=0.2)  # Adjust the hole size
fig.update_traces(text=filtered_df["Job Location"], textposition="inside")  # Change textposition
fig.update_xaxes(ticks="outside", tickfont=dict(size=8, color='black'))  # Adjust font size
fig.update_layout(
    width=700,
    height=600,  # Adjust the height to fit the page
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

# Filter the DataFrame to include only job locations in Tehran
tehran_filtered_df = filtered_df[filtered_df["Job Location"] == "تهران"]

# Group and count the records based on Job Location and Job Category
records_count = tehran_filtered_df.groupby(["Job Location", "Job Category"]).size().reset_index(name="RecordCount")

# Create a treemap based on Job Location, Job Category, and the count of records
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


import streamlit as st

# Title
st.title("What You are Searching For?")

# Input box for user text input
user_query = st.text_input("Enter your desired job position:")

st.write("Your query:", user_query)

# Create an instance of VectorSearch
vector_search = VectorSearch(embedder, threshold_percentage=0.02)

corpus = df['Job Position']
embeddings = df['embeddings']

# Call the search method with your data and queries
results = vector_search.search(corpus, embeddings, user_query)

# Print or process the results as needed
for query_results in results:
    for result in query_results:
        st.write(f"Query: {result['Query']}")
        st.write(f"Job Position: {result['Job Position']}\n(Score: {result['Score']:.4f})\n")

