import streamlit as st
import pandas as pd
import plotly.express as px #for using comparison seasonal bar chart and peak hours bar chart


#Adding page title to the browser tab and setting the layot as wide so content is not centralized and cramped
st.set_page_config(page_title="Fremont Bridge Bicycle Traffic", layout="wide")

st.title("🚲 Fremont Bridge Bicycle Traffic")

#Adding dashboard overview
st.markdown("""
### Overview  
The Fremont Bridge Bicycle Counter has been recording hourly bicycle traffic since October 2012.  
It tracks cyclists crossing the bridge on the east (Toward Fremont) and west (Toward Seattle) sidewalks.  
This dashboard provides:

📊 Summary metrics  
📅 Year‑based filtering  
☀ Seasonal comparison  
⏰ Peak‑hour analysis  
""")

#Importing dataset
DATE_COLUMN = "date"
DATA_URL = "Fremont_Bridge_Bicycle_Counter.csv"

#To keep raw data stored in cache and to organize the date format for using later on the bar charts
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN], format="mixed")

    data["year"] = data[DATE_COLUMN].dt.year
    data["hour"] = data[DATE_COLUMN].dt.hour
    data["month"] = data[DATE_COLUMN].dt.month
    return data

data = load_data()

#checkbox to show/hide raw data
if st.checkbox("🔍 Show Raw Data"):
    st.subheader("Raw Data")
    st.write(data)

#creating a dropdown/date picker to filter the data by year 
years = sorted(data["year"].unique())

#defauting to year 2018 since year 2012 doesn't have all months in the dataset and therefore visualization looks incorrect.
default_year = 2018

if 2018 in years:
    default_year = 2018
else:
    default_year = years[0]    

selected_year = st.selectbox(
    "📅 Select a Year", years, index=years.index(default_year)
)

filtered = data[data["year"] == selected_year]

#assigning names for NEast, West and Total columns and adding the total for East, West and total traffic
East = "fremont bridge sidewalks, south of n 34th st cyclist east sidewalk"
West = "fremont bridge sidewalks, south of n 34th st cyclist west sidewalk"
TOTAL = "fremont bridge sidewalks, south of n 34th st total"

st.subheader("📊 Summary Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Total East (Toward Fremont) Traffic", int(filtered[East].sum()))
col2.metric("Total West (Toward Seattle) Traffic", int(filtered[West].sum()))
col3.metric("Total Traffic", int(filtered[TOTAL].sum()))

#defining seasons by months of the year to filter it
st.subheader("☀️ Seasonal Comparison (➡️Fremont vs Seattle ⬅️)")

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"
    
#passing function as a parameter to a function
filtered["season"] = filtered[DATE_COLUMN].dt.month.apply(get_season)

seasonal = filtered.groupby("season")[[East, West]].sum().reset_index()

#bar chart comparing trafic East and West by season
season = px.bar( seasonal,
    x="season",
    y=[East, West],
    barmode="group",
    labels={"value": "Cyclists", "variable": "Direction"},
    title=f"☀️Seasonal Traffic Comparison ({selected_year})",
    color_discrete_sequence=["#2AB7CA","#FE4A49"]
)

st.plotly_chart(season, use_container_width=True)

#creating a hourly bar chart to find out the overall yearly trend for trafic peak hours
st.subheader("⏰ Peak Hours")

hourly = filtered.groupby("hour")[[East, West]].sum()
hourly["total"] = hourly[East] + hourly[West]

peak = px.bar(
    hourly, x=hourly.index, y="total",
    title=f"Peak Hours in {selected_year}",
    labels={"x": "Hour of Day", "total": "Total Cyclists"},
    color="total",
    color_continuous_scale=["#A8E6CF", "#2AB7CA", "#2A4D9B"] 
)

st.plotly_chart(peak, use_container_width=True)
