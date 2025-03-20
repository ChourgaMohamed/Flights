# compute_distances.py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
from flights_project import utils


def compute_distances():
    """Compute Euclidean and Geodesic distances from JFK for each airport."""
    df = utils.load_airports_data()
    jfk = df[df["faa"] == "JFK"].iloc[0]
    jfk_lat, jfk_lon = jfk["lat"], jfk["lon"]

    df["euclidean_dist"] = np.sqrt((df["lat"] - jfk_lat) ** 2 + (df["lon"] - jfk_lon) ** 2)
    df["geodesic_dist"] = df.apply(
        lambda row: geodesic((jfk_lat, jfk_lon), (row["lat"], row["lon"])).km,
        axis=1
    )
    return df

def compute_distance(dept_airport, arr_airport):
    """Geodesic distances between two airports."""
    df = utils.load_airports_data()
    dept_airport_data = df[df["faa"] == dept_airport]
    arr_airport_data = df[df["faa"] == arr_airport]

    if dept_airport_data.empty or arr_airport_data.empty:
        print("One or both airports not found!")
        return

    dept_lat, dept_lon = dept_airport_data["lat"].values[0], dept_airport_data["lon"].values[0]
    arr_lat, arr_lon = arr_airport_data["lat"].values[0], arr_airport_data["lon"].values[0]

    geodesic_dist = geodesic((dept_lat, dept_lon), (arr_lat, arr_lon)).mi
    return geodesic_dist


def plot_distance_histograms():
    """Plot histograms of Euclidean and Geodesic distances from JFK."""
    df = compute_distances()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Use colors from utils.COLOR_PALETTE
    axes[0].hist(
        df["euclidean_dist"],
        bins=30,
        edgecolor="black",
        color=utils.COLOR_PALETTE.get("pakistan_green", "green")  # Default to green if missing
    )
    axes[0].set_xlabel("Euclidean Distance from JFK")
    axes[0].set_ylabel("Number of Airports")
    axes[0].set_title("Euclidean Distance Distribution")

    axes[1].hist(
        df["geodesic_dist"],
        bins=30,
        edgecolor="black",
        color=utils.COLOR_PALETTE.get("india_green", "darkgreen")  # Default to dark green if missing
    )
    axes[1].set_xlabel("Geodesic Distance from JFK (km)")
    axes[1].set_ylabel("Number of Airports")
    axes[1].set_title("Geodesic Distance Distribution")

    plt.tight_layout()
    return fig


def main():
    """Run distance analysis functions."""
    df = compute_distances()
    print(df[["faa", "name", "euclidean_dist", "geodesic_dist"]].head())
    fig = plot_distance_histograms()
    plt.show()


if __name__ == "__main__":
    main()