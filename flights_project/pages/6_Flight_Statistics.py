import streamlit as st
from part3 import flight_statistics, flight_analysis
from db import get_db_connection

db_conn = get_db_connection()

st.title("Flight Statistics")
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
    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')