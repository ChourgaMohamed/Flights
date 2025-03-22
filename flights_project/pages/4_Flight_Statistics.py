import streamlit as st
from part3 import flight_statistics3
from part3 import flight_analysis
from db import get_db_connection
import pandas as pd
import plotly.graph_objects as go
from flights_project import utils 

db_conn = get_db_connection()

col1, col2 = st.columns([2, 3])
total = flight_statistics3.get_total_flights(conn=db_conn)
busiest = flight_statistics3.get_busiest_airports(conn=db_conn)
busiest_df = pd.DataFrame(busiest, columns=["Airport", "Flights"])
with col1:
     st.title("Flight statistics")
     total = flight_statistics3.get_total_flights(conn=db_conn)
     st.dataframe(busiest_df.set_index("Airport"))
     st.write(f"Total flights: {total}")
with col2:
    #Pie chart
    pie_colors = [
    utils.COLOR_PALETTE["pakistan_green"],
    utils.COLOR_PALETTE["light_green"],
    utils.COLOR_PALETTE["nyanza"]
]
    fig = go.Figure(data=[go.Pie(labels=busiest_df["Airport"], values=busiest_df["Flights"], hole=0.4,
            marker=dict(colors=pie_colors))])
    fig.update_layout(title_text="Busiest airports by flight volume")
    # Render the chart
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Distance verification analysis")
fig, text1, text2 = flight_analysis.verify_distance_computation(conn=db_conn)
st.plotly_chart(fig)
st.write(text1)
st.write(text2)
    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')