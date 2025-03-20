import streamlit as st
from part1 import plot_airports
from features import exploratory_analysis
from db import get_db_connection

db_conn = get_db_connection()  # Persistent connection

#Plot the exploratory analysis
st.subheader("Exploring Altitude vs Distance from NYC")
fig = exploratory_analysis.exploratory_analysis()
st.plotly_chart(fig)
# st.subheader("Density of Airports by Latitude")
# st.plotly_chart(hist_fig)

fig = plot_airports.plot_airports()
st.plotly_chart(fig)

st.subheader("Northern America Airports Map")
fig = plot_airports.plot_us_airports()
st.plotly_chart(fig)

st.subheader("Non-Northern American Airports Map")
fig = plot_airports.plot_non_us_airports()
st.plotly_chart(fig)

st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')