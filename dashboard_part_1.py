import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Airports Dashboard", layout="wide")

# ---------------------------
# Data Loading & Preprocessing
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("airports.csv")
    df["tz"] = df["tz"].fillna("Unknown").astype(str)
    return df


df = load_data()

# ---------------------------
# Global & US Maps
# ---------------------------
def get_global_map():
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="name",
        opacity=0.6
    )

    fig.update_layout(
        autosize=True,
        margin=dict(l=2, r=2, t=2, b=2)  # Reduce margins for a bigger map area
    )

    return fig

def get_us_map():
    us_airports = df[df["tz"].str.contains("America")]
    fig = px.scatter_geo(
        us_airports,
        lat="lat",
        lon="lon",
        hover_name="name",
        opacity=0.6
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=2, r=2, t=2, b=2)  # Reduce margins for a bigger map area
    )
    
    return fig

# ---------------------------
# Flight Route Functions
# ---------------------------
def get_flight_route_fig(faa_code):
    nyc_airports = df[df["faa"].isin(["JFK", "LGA", "EWR"])]
    target_airport = df[df["faa"] == faa_code]
    if target_airport.empty:
        return None
    # Combine NYC airports with the target
    plot_data = pd.concat([nyc_airports, target_airport])
    fig = px.scatter_geo(
        plot_data,
        lat="lat",
        lon="lon",
        text="name",
        hover_name="name",
        title=f"Route from NYC to {faa_code}",
        opacity=0.6
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=20)  # Reduce margins for a bigger map area
    )

    # Add a line connecting NYC and the target airport
    fig.add_trace(px.line_geo(plot_data, lat="lat", lon="lon").data[0])
    return fig

def get_multiple_routes_fig(faa_codes):
    nyc_airports = df[df["faa"].isin(["JFK", "LGA", "EWR"])]
    target_airports = df[df["faa"].isin(faa_codes)]
    if target_airports.empty:
        return None
    plot_data = pd.concat([nyc_airports, target_airports])
    fig = px.scatter_geo(
        plot_data,
        lat="lat",
        lon="lon",
        text="name",
        hover_name="name",
        title="Routes from NYC to Selected Airports",
        opacity=0.6
    )
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=20)  # Reduce margins for a bigger map area
    )    
    # Add a line for each selected airport
    for faa in faa_codes:
        target_airport = df[df["faa"] == faa]
        if not target_airport.empty:
            plot_line = pd.concat([nyc_airports, target_airport])
            fig.add_trace(px.line_geo(plot_line, lat="lat", lon="lon").data[0])
    return fig

# ---------------------------
# Distance Computations
# ---------------------------
@st.cache_data
def compute_distances(data):
    # Get JFK coordinates
    jfk = data[data["faa"] == "JFK"].iloc[0]
    jfk_lat, jfk_lon = jfk["lat"], jfk["lon"]
    data["euclidean_dist"] = np.sqrt((data["lat"] - jfk_lat)**2 + (data["lon"] - jfk_lon)**2)
    data["geodesic_dist"] = data.apply(
        lambda row: geodesic((jfk_lat, jfk_lon), (row["lat"], row["lon"])).km, axis=1
    )
    return data

df = compute_distances(df)

# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Global Airports Map",
    "US Airports Map",
    "Flight Route (Single)",
    "Flight Route (Multiple)",
    "Distance Analysis",
    "Time Zone Distribution",
    "Altitude Analysis"
])

# ---------------------------
# Page: Global Airports Map
# ---------------------------
if page == "Global Airports Map":
    st.header("Global Airports Map")
    fig = get_global_map()
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Page: US Airports Map
# ---------------------------
elif page == "US Airports Map":
    st.header("US Airports Map")
    fig = get_us_map()
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Page: Flight Route (Single)
# ---------------------------
elif page == "Flight Route (Single)":
    st.header("Flight Route from NYC to a Selected Airport")
    faa_code = st.text_input("Enter FAA code (e.g., LAX)", value="LAX")
    if st.button("Plot Route"):
        fig = get_flight_route_fig(faa_code)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Airport with FAA code {faa_code} not found.")

# ---------------------------
# Page: Flight Route (Multiple)
# ---------------------------
elif page == "Flight Route (Multiple)":
    st.header("Flight Routes from NYC to Multiple Airports")
    available_airports = sorted(df["faa"].unique().tolist())
    faa_codes = st.multiselect("Select FAA codes", options=available_airports, default=["LAX", "ORD", "MIA"])
    if st.button("Plot Multiple Routes"):
        fig = get_multiple_routes_fig(faa_codes)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No valid airports selected.")

# ---------------------------
# Page: Distance Analysis
# ---------------------------
elif page == "Distance Analysis":
    st.header("Distance Analysis from JFK")
    st.subheader("Histograms of Euclidean and Geodesic Distances")
    fig, axes = plt.subplots(1, 2)
    axes[0].hist(df["euclidean_dist"], bins=30, edgecolor="black")
    axes[0].set_xlabel("Euclidean Distance from JFK")
    axes[0].set_ylabel("Number of Airports")
    axes[0].set_title("Euclidean Distance Distribution")
    axes[1].hist(df["geodesic_dist"], bins=30, edgecolor="black")
    axes[1].set_xlabel("Geodesic Distance from JFK (km)")
    axes[1].set_ylabel("Number of Airports")
    axes[1].set_title("Geodesic Distance Distribution")
    st.pyplot(fig)

# ---------------------------
# Page: Time Zone Distribution
# ---------------------------
elif page == "Time Zone Distribution":
    st.header("Time Zone Distribution of Airports")
    # Exclude "Unknown" time zones for clarity
    tz_counts = df[df["tz"] != "Unknown"]["tz"].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots()
    ax.barh(tz_counts.index, tz_counts.values, color="royalblue")
    ax.set_xlabel("Number of Airports")
    ax.set_ylabel("Time Zone")
    ax.set_title("Distribution of Airports Across Time Zones")
    st.pyplot(fig)

# ---------------------------
# Page: Altitude Analysis
# ---------------------------
elif page == "Altitude Analysis":
    st.header("Altitude Analysis")
    
    # Scatter plot: Altitude vs. Geodesic Distance
    st.subheader("Scatter Plot: Altitude vs. Geodesic Distance from JFK")
    fig1, ax1 = plt.subplots()
    sns.scatterplot(x="geodesic_dist", y="alt", data=df, alpha=0.5, color="red", ax=ax1)
    ax1.set_xlabel("Geodesic Distance from JFK (km)")
    ax1.set_ylabel("Altitude (m)")
    ax1.set_title("Altitude vs. Distance from JFK")
    st.pyplot(fig1)
    
    # Bar chart: Top 10 Highest Airports
    st.subheader("Top 10 Highest Airports")
    top_highest = df.nlargest(10, "alt")
    fig2, ax2 = plt.subplots()
    ax2.barh(top_highest["name"], top_highest["alt"], color="darkgreen")
    ax2.set_xlabel("Altitude (m)", fontsize=12)
    ax2.set_ylabel("Airport Name", fontsize=12)
    ax2.set_title("Top 10 Highest Airports in the World", fontsize=14)
    ax2.invert_yaxis()  # Highest at the top
    plt.subplots_adjust(left=0.3)
    st.pyplot(fig2)
