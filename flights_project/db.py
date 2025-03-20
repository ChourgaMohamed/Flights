import streamlit as st
from flights_project import utils

@st.cache_resource
def get_db_connection():
    return utils.get_persistent_db_connection()
