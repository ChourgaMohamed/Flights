import streamlit as st
from features import heatmap_analysis
from db import get_db_connection

db_conn = get_db_connection()

st.title("Heatmap Analysis")
st.subheader("Heatmap Analysis")

# Let the user select the metric to display
metric = st.radio("Select Metric", ("Flight Counts", "Average Departure Delays"))

# Option to use all data or filter by week range
all_data = st.checkbox("Use all data", value=True)
week_range = None
if not all_data:
    week_range = st.slider("Select week range", 1, 53, (1, 53))

if metric == "Flight Counts":
    fig = heatmap_analysis.plot_flights_heatmap(week_range=week_range, conn=db_conn)
else:
    fig = heatmap_analysis.plot_delays_heatmap(week_range=week_range, conn=db_conn)
st.plotly_chart(fig)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')