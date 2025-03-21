import streamlit as st
import pandas as pd
from part3 import flight_statistics, flight_analysis
from db import get_db_connection

# Establish a database connection
db_conn = get_db_connection()

st.title("Flight Statistics")
st.subheader("General Flight Statistics")

# Display total flights as a metric
total_flights = flight_statistics.get_total_flights(conn=db_conn)
st.metric("Total Flights", value=f"{total_flights:,}")

# Get busiest airports and format as a DataFrame
busiest_airports = flight_statistics.get_busiest_airports(conn=db_conn)
busiest_airports["Flights"] = busiest_airports["Flights"].apply(lambda x: f"{x:,}")  # Format with commas

st.subheader("Busiest Airports")
st.dataframe(busiest_airports.set_index("Airport"))  # Display as a clean table

# Distance verification analysis
st.subheader("Distance Verification Analysis")
fig, text1, text2 = flight_analysis.verify_distance_computation(conn=db_conn)
st.plotly_chart(fig)
st.write(text1)
st.write(text2)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')