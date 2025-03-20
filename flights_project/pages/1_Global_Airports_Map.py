import streamlit as st
from part1 import plot_airports
from db import get_db_connection

db_conn = get_db_connection()  # Persistent connection

st.title("Global Airports Map")
st.subheader("Global Airports Map")
fig = plot_airports.plot_airports()
st.plotly_chart(fig)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')