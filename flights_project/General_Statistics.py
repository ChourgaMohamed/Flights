"""
Streamlit dashboard for the Flights Project.
Imports functions from Part 1 and Part 3 to display interactive visualizations.
Uses a single database connection (opened once and passed to subfunctions).
"""

import streamlit as st
from flights_project import utils
from part1 import plot_routes, compute_distances
from part4 import flight_statistics
from db import get_db_connection
import pandas as pd

# Initialize (or reuse) a persistent database connection in session_state
db_conn = get_db_connection()

# Set page layout to wide
st.set_page_config(layout="wide")

# Load airports data and create options for selectboxes
airports_df = utils.load_airports_data()
airport_options = [f"{row['faa']} - {row['name']}" for _, row in airports_df.iterrows()]
placeholder = "Select an airport (FAA - Name)"
airport_options_with_placeholder = [placeholder] + airport_options

st.sidebar.header("Select Flight Route")
dep_airport = st.sidebar.selectbox("Departure airport", ["JFK", "LGA", "EWR"])
st.sidebar.text("Select destination airport", )
arr_airport = st.sidebar.selectbox("You can type in the box", options=airport_options_with_placeholder, index=0)

st.title("Project Flights Dashboard")
st.write("Interactive dashboard to explore flight data.")

# Make two columns for the main content and make it 40% and 60% width for the first and second column respectively
col1, col2 = st.columns((2, 3))


############################
# NYC Flights in 2023
############################
with col1:
    st.subheader("NYC Flights in 2023")
    total_flights, flights_per_airport = flight_statistics.get_nyc_flight_statistics(db_conn)

    # Show total flights as a metric
    st.metric("Total Flights from NYC (2023)", value=f"{total_flights:,}")  # add commas for readability
    st.write("Flights per Airport:")
    flights_per_airport = flights_per_airport.rename(columns={"origin": "Airport", "num_flights": "Flights"})

    st.dataframe(flights_per_airport.set_index(flights_per_airport.columns[0]))

############################
# Route Statistics
############################
with col2:
    st.subheader("Flight Statistics by Route")
    if arr_airport != placeholder:
        # Extract just the FAA code (e.g., "LAX" from "LAX - Los Angeles International")
        arr_airport_code = arr_airport.split(" - ")[0]
        
        # Get flight statistics for the selected route
        text, result = flight_statistics.get_flight_statistics(dep_airport, arr_airport_code, db_conn)
        
        # Convert the raw result (list of tuples/dicts) into a pandas DataFrame
        # Here we assume your SQL query returns exactly one row of data. If it can return multiple rows,
        # you can remove the [0] indexing or adjust accordingly.
        df = pd.DataFrame(
            result,
            columns=[
                "total_flights",
                "avg_departure_delay",
                "avg_air_time",
                "avg_arrival_delay"
            ]
        )
        
        # Rename columns to more descriptive names
        df = df.rename(columns={
            "total_flights": "Total Flights",
            "avg_departure_delay": "Avg Departure Delay (min)",
            "avg_air_time": "Avg Air Time (min)",
            "avg_arrival_delay": "Avg Arrival Delay (min)"
        })
        
        st.write(text)  # "Flight statistics for JFK → LAX", for example
        st.dataframe(df.set_index(df.columns[0]))

        # Give the distance between the two airports, rounded to integer miles
        distance = int(compute_distances.compute_distance(dep_airport, arr_airport_code))
        st.write(f"Distance between {dep_airport} and {arr_airport}: {distance} miles")



    else:
        st.write("Please select a valid destination airport.")


if arr_airport != placeholder:
    faa_code = arr_airport.split(" - ")[0]
    fig = plot_routes.plot_flight_route(dep_airport, faa_code)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))  # optional
    st.plotly_chart(fig, use_container_width=True)



st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')