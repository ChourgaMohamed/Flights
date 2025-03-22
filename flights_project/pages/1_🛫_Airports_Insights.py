import streamlit as st
from part1 import plot_airports
from part3 import flight_analysis
from features import exploratory_analysis
from db import get_db_connection

db_conn = get_db_connection()  # Persistent connection

#Plot altitude vs distance from NYC
st.subheader("Exploring Altitude vs Distance from NYC")
fig = exploratory_analysis.exploratory_analysis()
st.plotly_chart(fig)

fig = plot_airports.plot_airports()
fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig)

# st.subheader("Northern America Airports Map")
# fig = plot_airports.plot_us_airports()
# st.plotly_chart(fig)

# st.subheader("Non-Northern American Airports Map")
# fig = plot_airports.plot_non_us_airports()
# st.plotly_chart(fig)

# Distance verification analysis
st.subheader("Distance verification analysis")
st.write("The below plot shows the difference between the distance computed by the Haversine formula and the distance provided in the dataset.")
fig, text1, text2 = flight_analysis.verify_distance_computation(conn=db_conn)
st.plotly_chart(fig)
st.write(text1)
st.write(text2)

# Conculsion
st.write("The plot shows that the distance computed by the Haversine formula is very close to the distance provided in the dataset.")



st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')