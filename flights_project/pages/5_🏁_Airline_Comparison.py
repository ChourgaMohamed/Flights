import streamlit as st
from features import airline_comparison
from db import get_db_connection

db_conn = get_db_connection()

all_carriers = airline_comparison.get_all_carriers(conn=db_conn)
selected_carriers = st.multiselect(
    "Select carriers to display",
    all_carriers,
    default=["Allegiant Air", "Alaska Airlines Inc.", "Frontier Airlines Inc."]
)

col1, col2 = st.columns(2)
with col1:
    st.markdown("###### Airline Performance Comparison - Spider Chart")
    if selected_carriers:
        fig = airline_comparison.plot_airline_performance_spider(conn=db_conn, carriers=selected_carriers)
        if fig:
            st.plotly_chart(fig)
        else:
            st.write("No data for the selected carriers.")
    else:
        st.write("No carriers selected.")
with col2:
    st.markdown("###### Top Carriers by Flight Count")
    top_carriers = airline_comparison.get_top_carriers_by_flight_count(conn=db_conn, limit=100)
    if selected_carriers:
        st.dataframe(top_carriers.set_index(top_carriers.columns[0]))
    else:
        st.write("No data to display.")

# Display get_stats_per_airline
st.markdown("###### Airline Performance Metrics")

stats = airline_comparison.get_stats_per_airline(conn=db_conn).drop(columns=["Carrier"]).sort_values("Unique Planes",ascending=False)
st.dataframe(stats.set_index(stats.columns[0]).style.format({
    "Avg Departure Delay": "{:.2f}",
    "Avg Arrival Delay": "{:.2f}",
    "Avg Air Time": "{:.2f}"
}))
        
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')