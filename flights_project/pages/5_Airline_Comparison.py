import streamlit as st
from features import airline_comparison
from db import get_db_connection

db_conn = get_db_connection()

st.title("Airline Comparison")
st.subheader("Airline Performance Comparison - Spider Chart")

# 1. Get all carriers
all_carriers = airline_comparison.get_all_carriers(conn=db_conn)

# 2. Let the user pick carriers; default is a few popular ones
selected_carriers = st.multiselect(
    "Select carriers to display",
    all_carriers,
    default=["Allegiant Air", "Alaska Airlines Inc.", "Frontier Airlines Inc."]
)

if selected_carriers:
    fig = airline_comparison.plot_airline_performance_spider(conn=db_conn, carriers=selected_carriers)
    if fig:
        st.plotly_chart(fig)
    else:
        st.write("No data for the selected carriers.")
else:
    st.write("No carriers selected.")
    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')