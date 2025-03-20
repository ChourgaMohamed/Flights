import streamlit as st
from part1 import plot_routes
from flights_project import utils
from db import get_db_connection

db_conn = get_db_connection()

# Load airports data and prepare options for the selectbox
airports_df = utils.load_airports_data()
airport_options = [f"{row['faa']} - {row['name']}" for _, row in airports_df.iterrows()]
placeholder = "Select an airport (FAA - Name)"
airport_options_with_placeholder = [placeholder] + airport_options

st.title("Flight Route from NYC")
selected_airport = st.selectbox("Type or select target airport", options=airport_options_with_placeholder, index=0)
if selected_airport != placeholder:
    faa_code = selected_airport.split(" - ")[0]
    if st.button("Plot Route"):
        fig = plot_routes.plot_flight_route(faa_code)
        st.plotly_chart(fig)
    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')