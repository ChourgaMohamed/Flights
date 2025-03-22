import streamlit as st
from part1 import plot_routes
from part3 import flight_analysis
from db import get_db_connection
import pandas as pd
import plotly.graph_objects as go
from flights_project import utils 

db_conn = get_db_connection()

# Load airports data
st.title("Flight statistics")
airports_df = utils.load_airports_data()
placeholder = "Select an airport"
st.sidebar.header("Select departure airport")
dep_airport = st.sidebar.selectbox("Departure airport", [placeholder]+["JFK", "LGA", "EWR"], index=0)
#Sidebar one day delay analysis
st.sidebar.header("Select a day")
flight_date = st.sidebar.date_input("Day", value=pd.to_datetime("2023-01-01"))

# Convert dates to string format
flight_date_str = flight_date.strftime("%Y-%m-%d")

if dep_airport != placeholder:
    fig, fig2 = plot_routes.plot_multiple_routes(dep_airport, flight_date_str, airports_df, conn= db_conn)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0)) 
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.write("Please select a valid departure airport.")

st.subheader("Distance verification analysis")
fig, text1, text2 = flight_analysis.verify_distance_computation(conn=db_conn)
st.plotly_chart(fig)
st.write(text1)
st.write(text2)
    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')