import streamlit as st
from part3 import manufacturers_analysis
from features import plane_type_analyses
from flights_project import utils
from db import get_db_connection

db_conn = get_db_connection()

# Load airports data and prepare selectbox options
airports_df = utils.load_airports_data()
airport_options = [f"{row['faa']} - {row['name']}" for _, row in airports_df.iterrows()]
placeholder = "Select an airport (FAA - Name)"
airport_options_with_placeholder = [placeholder] + airport_options

# Create two columns for the main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Aircraft Manufacturer Analysis")
    selected_destination = st.selectbox("Select destination airport", options=airport_options_with_placeholder, index=0)
    if selected_destination != placeholder:
        destination = selected_destination.split(" - ")[0]
        result = manufacturers_analysis.plot_manufacturer_data(destination, conn=db_conn)
        if isinstance(result, str):
            st.write(result)
        else:
            st.plotly_chart(result)

with col2:
    st.subheader("Aircraft Engine Type Analysis")
    fig = plane_type_analyses.plot_violin_distance_by_engine(conn=db_conn)
    st.plotly_chart(fig)

# Load full flight-plane dataset
df = plane_type_analyses.get_plane_flight_data(conn=db_conn)

# Correlation heatmap
st.plotly_chart(plane_type_analyses.analyze_correlations(df))

# 2x2 scatter plots
st.plotly_chart(plane_type_analyses.plot_scatter_plots(df))

# Final max distance vs air time chart (only show 2 labels)
st.subheader("Plane Models: Max Distance vs Max Air Time")
fig_model_summary = plane_type_analyses.plot_model_distance_year(df)
st.plotly_chart(fig_model_summary, use_container_width=True)
st.markdown("✈️ **A321-271NX** has the **longest flight time**, and **767-432ER** has the **longest flight distance**.")

# Sidebar credit
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')