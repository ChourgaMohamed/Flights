# analyze_timezones.py
import pandas as pd
import matplotlib.pyplot as plt
from flights_project import utils

def analyze_timezones():
    """Analyze the number of airports in each time zone and visualize the distribution."""
    df = utils.load_airports_data()

    # Ensure 'tz' is treated as a string and replace NaN values properly
    df["tz"] = df["tz"].astype(str).fillna("Unknown")

    # Count airports per time zone
    time_zone_counts = df[df["tz"] != "Unknown"]["tz"].value_counts().sort_values(ascending=True)

    # Plot the distribution
    plt.figure(figsize=(12, 6))
    plt.barh(time_zone_counts.index, time_zone_counts.values, color="royalblue")
    plt.xlabel("Number of Airports")
    plt.ylabel("Time Zone")
    plt.title("Distribution of Airports Across Time Zones")
    plt.show()

    # Print top 10 time zones with most airports
    print("Top 10 busiest time zones:\n", time_zone_counts.tail(10))

if __name__ == "__main__":
    analyze_timezones()