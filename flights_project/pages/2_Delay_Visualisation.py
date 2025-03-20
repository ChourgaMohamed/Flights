import streamlit as st
from part3 import delays_analysis
from features import heatmap_analysis
from db import get_db_connection
import pandas as pd

db_conn = get_db_connection()

st.title("Delay Analysis")
st.subheader("Flight Delay Analysis")

# Sidebar for date range selection
st.sidebar.header("Select Date Range")
start_date = st.sidebar.date_input("Start date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End date", value=pd.to_datetime("2023-12-31"))

# Convert dates to string format
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Plot delay histogram
st.write("Delay histogram")
fig_delay_histogram = delays_analysis.plot_delay_histogram(start_date=start_date_str, end_date=end_date_str, conn=db_conn)
st.plotly_chart(fig_delay_histogram)

# Plot heatmaps side by side
st.header("Heatmap Analysis")
col1, col2 = st.columns(2)

with col1:
    fig_flights_heatmap = heatmap_analysis.plot_flights_heatmap(start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    st.plotly_chart(fig_flights_heatmap)

with col2:
    fig_delays_heatmap = heatmap_analysis.plot_delays_heatmap(start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    st.plotly_chart(fig_delays_heatmap)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')