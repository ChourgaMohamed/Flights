import streamlit as st
from part3 import delays_analysis
from features import heatmap_analysis
from db import get_db_connection
import pandas as pd

db_conn = get_db_connection()

st.title("Delay analysis")
st.subheader("Departure delays in 2023")

# Sidebar for date range selection
st.sidebar.header("Select date range")
start_date = st.sidebar.date_input("Start date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End date", value=pd.to_datetime("2023-12-31"))

#Sidebar one day delay analysis
st.sidebar.header("Select a day in 2023")
delay_date = st.sidebar.date_input("Day", value=pd.to_datetime("2023-01-01"))

# Convert dates to string format
delay_date_str = delay_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

col1, col2 = st.columns(2)
with col1:
    # Plot delay histogram
    fig_delay_histogram = delays_analysis.plot_delay_histogram(start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    st.plotly_chart(fig_delay_histogram)

with col2:
    fig_delay_histogram = delays_analysis. plot_day_delay(day=delay_date_str, conn=db_conn)
    st.plotly_chart(fig_delay_histogram)


# Plot heatmaps side by side
st.markdown("<h2 style='text-align: center;'>Heatmap analysis</h2>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    fig_flights_heatmap = heatmap_analysis.plot_flights_heatmap(start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    st.plotly_chart(fig_flights_heatmap)

with col4:
    fig_delays_heatmap = heatmap_analysis.plot_delays_heatmap(start_date=start_date_str, end_date=end_date_str, conn=db_conn)
    st.plotly_chart(fig_delays_heatmap)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')