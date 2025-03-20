import streamlit as st
from part3 import manufacturers_analysis
from flights_project import utils
from db import get_db_connection

db_conn = get_db_connection()

# Load airports data and prepare selectbox options
airports_df = utils.load_airports_data()
airport_options = [f"{row['faa']} - {row['name']}" for _, row in airports_df.iterrows()]
placeholder = "Select an airport (FAA - Name)"
airport_options_with_placeholder = [placeholder] + airport_options

st.title("Manufacturer Analysis")
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
    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')