"""
Streamlit dashboard for the Flights Project.
Imports functions from Part 1 and Part 3 to display interactive visualizations.
Uses a single database connection (opened once and passed to subfunctions).
"""

import streamlit as st
import pandas as pd
from flights_project import utils
from part1 import global_and_US_maps, flight_route_functions, distance_analysis
from part3 import delays_analysis, manufacturers_analysis, flight_statistics

# Initialize (or reuse) a persistent database connection in session_state
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = utils.open_connection()
db_conn = st.session_state.db_conn

# Load airports data and create options for selectboxes
airports_df = utils.load_airports_data()
airport_options = [f"{row['faa']} - {row['name']}" for _, row in airports_df.iterrows()]
placeholder = "Select an airport (FAA - Name)"
airport_options_with_placeholder = [placeholder] + airport_options

st.title("Flights Project Dashboard")
st.write("Interactive dashboard to explore flight data.")

# Sidebar navigation
option = st.sidebar.selectbox("Select Analysis", 
                              ("Global Airports Map", "US Airports Map", 
                               "Flight Route", "Delay Analysis", 
                               "Manufacturer Analysis", "Flight Statistics"))

if option == "Global Airports Map":
    st.subheader("Global Airports Map")
    fig = global_and_US_maps.plot_global_airports()
    st.plotly_chart(fig)

elif option == "US Airports Map":
    st.subheader("US Airports Map")
    fig = global_and_US_maps.plot_us_airports()
    st.plotly_chart(fig)

elif option == "Flight Route":
    st.subheader("Flight Route from NYC")
    selected_airport = st.selectbox("Type or select target airport", options=airport_options_with_placeholder, index=0)
    if selected_airport != placeholder:
        faa_code = selected_airport.split(" - ")[0]
        if st.button("Plot Route"):
            fig = flight_route_functions.plot_flight_route(faa_code)
            st.plotly_chart(fig)

elif option == "Delay Analysis":
    st.subheader("Flight Delay Analysis")
    st.write("Delay histogram")
    fig = delays_analysis.plot_delay_histogram(conn=db_conn)
    st.pyplot(fig)

elif option == "Manufacturer Analysis":
    st.subheader("Aircraft Manufacturer Analysis")
    selected_destination = st.selectbox("Select destination airport", options=airport_options_with_placeholder, index=0)
    if selected_destination != placeholder:
        destination = selected_destination.split(" - ")[0]
        if st.button("Show Manufacturer Data"):
            result = manufacturers_analysis.plot_manufacturer_data(destination, conn=db_conn)
            if isinstance(result, str):
                st.write(result)
            else:
                st.pyplot(result)


elif option == "Flight Statistics":
    st.subheader("General Flight Statistics")
    total = flight_statistics.get_total_flights(conn=db_conn)
    st.write(f"Total Flights: {total}")
    busiest = flight_statistics.get_busiest_airports(conn=db_conn)
    st.write("Busiest Airports:")
    for row in busiest:
        st.write(f"Airport: {row[0]}, Flights: {row[1]}")
    st.subheader("Distance Analysis")
    fig = distance_analysis.plot_distance_histograms()
    st.pyplot(fig)
