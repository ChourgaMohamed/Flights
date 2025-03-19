# analyze_altitudes.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from geopy.distance import geodesic
from flights_project import utils

def analyze_altitudes():
    """Analyze altitude distribution of airports in relation to distance from JFK."""
    df = utils.load_airports_data()

    # Get JFK coordinates
    jfk = df[df["faa"] == "JFK"].iloc[0]
    jfk_lat, jfk_lon = jfk["lat"], jfk["lon"]

    # Compute Geodesic distance if not already present
    if "geodesic_dist" not in df.columns:
        df["geodesic_dist"] = df.apply(lambda row: geodesic((jfk_lat, jfk_lon), (row["lat"], row["lon"])).km, axis=1)

    # Scatter plot: Altitude vs. Distance from JFK
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=df["geodesic_dist"], y=df["alt"], alpha=0.5, color="red")
    plt.xlabel("Geodesic Distance from JFK (km)")
    plt.ylabel("Altitude (m)")
    plt.title("Altitude vs. Distance from JFK")
    plt.show()

    # Get top 10 highest airports
    top_highest_airports = df.nlargest(10, "alt")

    # Bar chart for top 10 highest airports
    plt.figure(figsize=(12, 6))
    plt.barh(top_highest_airports["name"], top_highest_airports["alt"], color="darkgreen")
    plt.xlabel("Altitude (m)", fontsize=12)
    plt.ylabel("Airport Name", fontsize=12)
    plt.title("Top 10 Highest Airports in the World", fontsize=14)
    plt.gca().invert_yaxis()  # Highest airport at the top
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.subplots_adjust(left=0.3)  # Adjust margin for visibility
    plt.show()

if __name__ == "__main__":
    analyze_altitudes()