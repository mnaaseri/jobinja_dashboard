import streamlit as st 
import plotly.express as px
import pandas as pd 
import os 
import warnings
import arabic_reshaper
from bidi.algorithm import get_display
warnings.filterwarnings('ignore')

st.set_page_config(page_title="jobinja Dashboard", page_icon=":bar_chart", layout="wide")
# Set the font to "Noto Sans" or the system font you prefer

st.write(unsafe_allow_html=True)
# Specify the text direction as RTL
st.write('<style>body {direction: rtl;}</style>', unsafe_allow_html=True)
st.title("عنوان")
# st.title(" :bar_chart: JoBInja EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    # os.chdir(r"/home/maryam/Desktop/Personal_projects/jobinja_dashboard/")
    df = pd.read_csv("Jobinja - Processed.csv")

col1, col2 = st.columns((2))
# df["Date Posted"] = pd.to_datetime(df["Date Posted"])

# # Getting the min and max date 
# startDate = pd.to_datetime(df["Date Posted"]).min()
# endDate = pd.to_datetime(df["Date Posted"]).max()

# with col1:
#     date1 = pd.to_datetime(st.date_input("Start Date", startDate))

# with col2:
#     date2 = pd.to_datetime(st.date_input("End Date", endDate))

# df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

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


with col1:
    st.subheader("Category wise Jon Positions")
    fig = px.bar(category_df, x = "Job Category", y = "UniqueRecordCount",
                 template = "seaborn")

    st.plotly_chart(fig,use_container_width=True, height = 1500)


with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, names = "Job Location", hole = 0.5)

    # fig.update_traces(text = filtered_df["Job Location"], textposition = "outside")
    fig.update_xaxes(ticks="outside",tickfont=dict(family='Arial', size=20, color='black'))
    st.plotly_chart(fig, use_container_width=True,height = 1500)



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

