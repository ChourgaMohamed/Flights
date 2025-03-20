import streamlit as st
from part3 import delays_analysis
from db import get_db_connection

db_conn = get_db_connection()

st.title("Delay Analysis")
st.subheader("Flight Delay Analysis")
st.write("Delay histogram")
fig = delays_analysis.plot_delay_histogram(conn=db_conn)
st.plotly_chart(fig)


    
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')