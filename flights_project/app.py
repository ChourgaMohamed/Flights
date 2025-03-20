"""
Streamlit dashboard for the Flights Project.
Imports functions from Part 1 and Part 3 to display interactive visualizations.
Uses a single database connection (opened once and passed to subfunctions).
"""

import streamlit as st
from flights_project import utils
from part1 import plot_routes, plot_airports
from part3 import delays_analysis, manufacturers_analysis, flight_statistics, flight_analysis
from features import airline_comparison, heatmap_analysis

# Initialize (or reuse) a persistent database connection in session_state
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = utils.get_persistent_db_connection()
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
                              ("Global Airports Map", "Northern America Airports Map", 
                               "Flight Route", "Delay Analysis", 
                               "Manufacturer Analysis", "Flight Statistics", "Airline Comparison", "Heatmap Analysis"))

if option == "Global Airports Map":
    st.subheader("Global Airports Map")
    fig = plot_airports.plot_airports()
    st.plotly_chart(fig)

elif option == "Northern America Airports Map":
    st.subheader("Northern America Airports Map")
    fig = plot_airports.plot_us_airports()
    st.plotly_chart(fig)

if option == "Flight Route":
    st.subheader("Flight Route from NYC")
    selected_airport = st.selectbox("Type or select target airport", options=airport_options_with_placeholder, index=0)
    if selected_airport != placeholder:
        faa_code = selected_airport.split(" - ")[0]
        if st.button("Plot Route"):
            fig = plot_routes.plot_flight_route(faa_code)
            st.plotly_chart(fig)

elif option == "Delay Analysis":
    st.subheader("Flight Delay Analysis")
    st.write("Delay histogram")
    fig = delays_analysis.plot_delay_histogram(conn=db_conn)
    st.plotly_chart(fig)

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
                st.plotly_chart(result)


elif option == "Flight Statistics":
    st.subheader("General Flight Statistics")
    total = flight_statistics.get_total_flights(conn=db_conn)
    st.write(f"Total Flights: {total}")
    busiest = flight_statistics.get_busiest_airports(conn=db_conn)
    st.write("Busiest Airports:")
    for row in busiest:
        st.write(f"Airport: {row[0]}, Flights: {row[1]}")
    st.subheader("Distance Verification Analysis")
    fig, text1, text2 = flight_analysis.verify_distance_computation(conn=db_conn)
    st.plotly_chart(fig)
    st.write(text1)
    st.write(text2)

elif option == "Airline Comparison":
    st.subheader("Airline Performance Comparison - Spider Chart")

    # 1. Get all carriers (names or codes) from airline_comparison
    all_carriers = airline_comparison.get_all_carriers(conn=db_conn)

    # # 2. Get the top 3 carriers by total flights (for default selection)
    # top_3 = airline_comparison.get_top_carriers_by_flight_count(conn=db_conn, limit=3)

    # 3. Let the user pick carriers; default is top_3
    selected_carriers = st.multiselect(
        "Select carriers to display",
        all_carriers,
        default= ["Allegiant Air", "Alaska Airlines Inc.", "Frontier Airlines Inc."]
    )

    # 4. Plot only if user selected at least one
    if selected_carriers:
        fig = airline_comparison.plot_airline_performance_spider(
            conn=db_conn, carriers=selected_carriers
        )
        if fig:
            st.plotly_chart(fig)
        else:
            st.write("No data for the selected carriers.")
    else:
        st.write("No carriers selected.")

elif option == "Heatmap Analysis":
    st.subheader("Heatmap Analysis")
    # Let the user select the metric to display
    metric = st.radio("Select Metric", ("Flight Counts", "Average Departure Delays"))
    
    # Option to use all data or filter by week range
    all_data = st.checkbox("Use all data", value=True)
    week_range = None
    if not all_data:
        # Provide a slider to select a week range (ISO weeks: 1 to 53)
        week_range = st.slider("Select week range", 1, 53, (1, 53))
    
    # Generate the appropriate heatmap based on user selection
    if metric == "Flight Counts":
        fig = heatmap_analysis.plot_flights_heatmap(week_range=week_range, conn=db_conn)
    else:
        fig = heatmap_analysis.plot_delays_heatmap(week_range=week_range, conn=db_conn)
    
    st.plotly_chart(fig)

