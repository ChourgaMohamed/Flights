# exploratory_analysis.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from geopy.distance import geodesic
from flights_project import utils

def exploratory_analysis():
    """Perform additional analysis on airport data to uncover trends."""
    df = utils.load_airports_data()

    # Get JFK coordinates
    jfk = df[df["faa"] == "JFK"].iloc[0]
    jfk_lat, jfk_lon = jfk["lat"], jfk["lon"]

    # Compute Geodesic distance if missing
    if "geodesic_dist" not in df.columns:
        df["geodesic_dist"] = df.apply(lambda row: geodesic((jfk_lat, jfk_lon), (row["lat"], row["lon"])).km, axis=1)

    # Scatter plot: Altitude vs. Distance from JFK
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=df["geodesic_dist"], y=df["alt"], alpha=0.5, color="blue")
    plt.xlabel("Geodesic Distance from JFK (km)")
    plt.ylabel("Altitude (m)")
    plt.title("Exploring Altitude vs Distance from NYC")
    plt.show()

    # Investigate airport density by latitude
    plt.figure(figsize=(12, 6))
    sns.histplot(df["lat"], bins=50, kde=True)
    plt.xlabel("Latitude")
    plt.ylabel("Number of Airports")
    plt.title("Density of Airports by Latitude")
    plt.show()

if __name__ == "__main__":
    exploratory_analysis()