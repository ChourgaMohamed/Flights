import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Load data from the database
@st.cache_data
def load_data():
    conn = sqlite3.connect("flights_database.db")
    df = pd.read_sql_query("SELECT * FROM flights", conn)
    conn.close()
    return df


df = load_data()

# Set up Streamlit dashboard
st.title("NYC Flight Statistics Dashboard")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["General Statistics", "Flight Analysis", "Delay Analysis"])

if page == "General Statistics":
    st.header("General Flight Statistics")
    st.write(df.describe())

    fig, ax = plt.subplots()
    sns.histplot(df['air_time'], bins=30, kde=True, ax=ax)
    ax.set_title("Distribution of Air Time")
    st.pyplot(fig)

elif page == "Flight Analysis":
    st.header("Flight Analysis")
    origin = st.selectbox("Select Departure Airport", df["origin"].unique())
    dest = st.selectbox("Select Destination Airport", df["dest"].unique())

    filtered_df = df[(df["origin"] == origin) & (df["dest"] == dest)]
    st.write(filtered_df[["flight", "carrier", "dep_time", "arr_time"]])

    st.subheader("Flight Time Distribution")
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["air_time"], bins=20, kde=True, ax=ax)
    ax.set_title(f"Air Time Distribution for {origin} to {dest}")
    st.pyplot(fig)

elif page == "Delay Analysis":
    st.header("Flight Delay Analysis")
    fig, ax = plt.subplots()
    sns.histplot(df["dep_delay"], bins=30, kde=True, ax=ax)
    ax.set_title("Departure Delay Distribution")
    st.pyplot(fig)

# Run using: streamlit run part5.py