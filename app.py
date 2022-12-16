import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time

st.set_page_config(layout="wide")

DATA_URL = (
"Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York City 🗽")
st.markdown("This application is a Streamlit dashboard that can be used "
"to analyze motor vehicle collisions in NYC  \n"
"*Data Provided by Police Department (NYPD)* 👮🏼")


with st.expander('About this dataset'):
  st.write('The Motor Vehicle Collisions crash table contains details on the '
  'crash event. Each row represents a crash event. The Motor Vehicle Collisions '
  'data tables contain information from all police reported motor vehicle '
  'collisions in NYC. The police report (MV104-AN) is required to be filled out '
  'for collisions where someone is injured or killed, or where there is at least '
  '$1000 worth of damage.')


@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data


my_bar = st.progress(0)

for percent_complete in range(100):
     time.sleep(0.01)
     my_bar.progress(percent_complete + 1)


st.header("Where are the most people injured in NYC?")
st.sidebar.header("Settings")
injured_people = st.sidebar.slider("🧍 Number of people injured in vechicle collisions:", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


st.header("How many collisions occur during a given time of day?")
hours = st.sidebar.slider("⌚ Hour to look at:", 0, 23, (3,6))
data = data[
    (data['date/time'].dt.hour >= hours[0]) & (data['date/time'].dt.hour <= hours[1])
]

st.markdown("Vehicle collisions between %i:00 and %i:00 🚗💥" % (hours[0], hours[1] % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ]
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hours[0], hours[1] % 24))

filtered = data
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
st.bar_chart(chart_data, x = 'minute', height=400, use_container_width=True)
st.write("Note: looks like the police tend to record accidents rounding the time to the nearest five minutes.")

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people:', ['Pedestrians 🚶', 'Cyclists 🚴', 'Motorists 👨‍🦽'])

if select == 'Pedestrians 🚶':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists 🚴':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])




if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
