"""
Streamlit dashboard for the Flights Project.
Imports functions from Part 1 and Part 3 to display interactive visualizations.
Uses a single database connection (opened once and passed to subfunctions).
"""

import streamlit as st
from flights_project import utils
from part3 import flight_analysis
from part4 import flight_statistics
from db import get_db_connection

import matplotlib.pyplot as plt
import seaborn as sns

# Initialize (or reuse) a persistent database connection in session_state
db_conn = get_db_connection()

# Load airports data and create options for selectboxes
airports_df = utils.load_airports_data()
airport_options = [f"{row['faa']} - {row['name']}" for _, row in airports_df.iterrows()]
placeholder = "Select an airport (FAA - Name)"
airport_options_with_placeholder = [placeholder] + airport_options

st.sidebar.header("Select Flight Route")
dep_airport = st.sidebar.selectbox("Departure airport", ["JFK", "LGA", "EWR"])
arr_airport = st.sidebar.selectbox("Select destination airport\n You can type in the box", options=airport_options_with_placeholder, index=0)

st.title("Project Flights Dashboard")
st.write("Interactive dashboard to explore flight data.")

total_flights, flights_per_airport = flight_statistics.get_nyc_flight_statistics(db_conn)

st.write("📊 Total Flights Departing from NYC Airports in 2023:", total_flights)
st.dataframe(flights_per_airport)

text, result = flight_statistics.get_flight_statistics(dep_airport, arr_airport, db_conn)
st.write(text)
st.dataframe(result)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')