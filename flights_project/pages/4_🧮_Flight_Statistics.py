import streamlit as st
from part3 import flight_statistics3, flight_analysis
from db import get_db_connection
import pandas as pd
from features import geo_heatmap

db_conn = get_db_connection()

# utils.load_airports_data()

# Create the departure airport selectbox and date range picker
st.sidebar.header("Select Flight Route")

# Departure airport is JFK, LGA, EWR, or all 3 airports
all_dept_airports = ["All Airports", "JFK - John F Kennedy International Airport", "LGA - La Guardia Airport", "EWR - Newark Liberty International Airport"]
dep_airport = st.sidebar.selectbox("Departure airport", options=all_dept_airports, index=0)
start_date = st.sidebar.date_input("Start date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End date", value=pd.to_datetime("2023-12-31"))

# Convert dates to string format
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

st.subheader("Geo Heatmap of Flights")

if dep_airport != "All Airports":
    dep_airport_code = dep_airport.split(" - ")[0]
    fig = geo_heatmap.plot_flights_geo_heatmap(dept_airport=dep_airport_code, start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig)
else:
    dep_airport_code = ["JFK", "LGA", "EWR"]
    fig = geo_heatmap.plot_flights_geo_heatmap(dept_airport=dep_airport_code, start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig)

st.subheader("Statistics for the selected departure airport")

if dep_airport != "All Airports":
    dep_airport_code = [dep_airport.split(" - ")[0]]
else:
    dep_airport_code = ["JFK", "LGA", "EWR"]

stats_df = flight_statistics3.get_flight_statistics(dep_airport_code, start_date_str, end_date_str, conn=db_conn)

# Rewrite the column names
stats_df = stats_df.rename(columns={
    "origin": "Airport",
    "total_flights": "Total Flights",
    "avg_departure_delay": "Avg Departure Delay (min)",
    "avg_air_time": "Avg Air Time (min)",
    "avg_arrival_delay": "Avg Arrival Delay (min)"
})

if len(dep_airport_code) == 1:
    st.write(f"Flight statistics for {dep_airport}")
else:
    st.write(f"Flight statistics for the selected airports: {', '.join(dep_airport_code)}")

# Display the statistics in a DataFrame, adjust for 2 decimals
st.dataframe(stats_df.set_index(stats_df.columns[0]).round(2))

# Display the flights that occurred from the selected departure airport(s) in the selected date range
st.subheader("Flights from the selected departure airport(s)")
flights_df = flight_analysis.get_flights_from_airport(dep_airport_code, start_date_str, end_date_str, conn=db_conn)

# Make the sched_dep_time and sched_arr_time only hour and minute
flights_df['sched_dep_time'] = pd.to_datetime(flights_df['sched_dep_time'], format='%H:%M:%S').dt.strftime('%H:%M')
flights_df['sched_arr_time'] = pd.to_datetime(flights_df['sched_arr_time'], format='%H:%M:%S').dt.strftime('%H:%M')

# Drop the year from the date column
flights_df['date'] = pd.to_datetime(flights_df['date']).dt.strftime('%Y-%m-%d')

# If the orgin are the same drop the column
if len(dep_airport_code) == 1:
    flights_df = flights_df.drop(columns='origin')

# Make dep_delay and arr_delay integers
flights_df['dep_delay'] = flights_df['dep_delay'].astype(int)
flights_df['arr_delay'] = flights_df['arr_delay'].astype(int)

# Rename the columns
flights_df = flights_df.rename(columns={
    "date": "Date",
    "sched_dep_time": "Dep Time",
    "sched_arr_time": "Arr Time",
    "dep_delay": "Delay Dep",
    "arr_delay": "Delay Arr",
    "carrier_name": "Carrier",
    "dest_name": "Destination Airport",
    "tailnum": "Tail Number",
    "model": "Model"
})

# Create function for to color departure delay and arrival delay red if they are below 0 else green
def color_negative_red(val):
    color = 'red' if val < 0 else 'green'
    return 'color: %s' % color

# If the dataframe has more than 262144 cells it will be to big to display and we cut it off
if flights_df.size > 262144:
    flights_df = flights_df.head(20000)

# Apply the function to the columns
flights_df = flights_df.style.map(color_negative_red, subset=['Delay Dep', 'Delay Arr'])

st.dataframe(flights_df, hide_index=True)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')