# PART 1
from flights_project import utils
import pandas as pd
import plotly.express as px
import numpy as np
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

# Load the dataset
df = utils.load_airports_data()

# Display the first few rows
print(df.head())


# Create an improved scatter_geo plot
fig = px.scatter_geo(df, lat="lat", lon="lon",
                     hover_name="name",  # Shows the airport name on hover
                     title="Airports Worldwide",
                     size_max=5,  # Keeps marker size reasonable
                     opacity=0.6)  # Makes overlapping markers slightly transparent

fig.show()

# Ensure the 'tz' column is treated as a string and replace NaN values with an empty string
df["tz"] = df["tz"].astype(str).fillna("")

# US airports (time zone contains 'America/')
us_airports = df[df["tz"].str.contains("America")]

# Non-US airports (time zone does NOT contain 'America/')
non_us_airports = df[~df["tz"].str.contains("America")]


# Plot US airports only
fig_us = px.scatter_geo(us_airports, lat="lat", lon="lon",
                        hover_name="name",  # Shows airport name on hover
                        title="US Airports",
                        size_max=5,
                        opacity=0.6)

fig_us.show()

# Plot Non-US airports only
fig_non_us = px.scatter_geo(non_us_airports, lat="lat", lon="lon",
                            hover_name="name",
                            title="Non-US Airports",
                            size_max=5,
                            opacity=0.6)

fig_non_us.show()


def plot_flight_route(faa_code):
    # NYC airport locations (JFK, LGA, EWR)
    nyc_airports = df[df["faa"].isin(["JFK", "LGA", "EWR"])]

    # Find the target airport
    target_airport = df[df["faa"] == faa_code]

    if target_airport.empty:
        print(f"Airport with FAA code {faa_code} not found!")
        return

    # Combine NYC airports and the target airport
    plot_data = pd.concat([nyc_airports, target_airport])

    # Plot the airports
    fig = px.scatter_geo(plot_data, lat="lat", lon="lon", text="name",
                         hover_name="name", title=f"Route from NYC to {faa_code}",
                         size_max=5, opacity=0.6)

    # Add a line from NYC to the target airport
    fig.add_trace(px.line_geo(plot_data, lat="lat", lon="lon").data[0])

    fig.show()


# Example usage
plot_flight_route("LAX")  # Replace "LAX" with any FAA code

def plot_multiple_routes(faa_codes):
    nyc_airports = df[df["faa"].isin(["JFK", "LGA", "EWR"])]
    target_airports = df[df["faa"].isin(faa_codes)]

    if target_airports.empty:
        print("No valid airports found!")
        return

    # Combine NYC airports and target airports
    plot_data = pd.concat([nyc_airports, target_airports])

    # Plot all airports
    fig = px.scatter_geo(plot_data, lat="lat", lon="lon", text="name",
                         hover_name="name", title="Routes from NYC to Selected Airports",
                         size_max=5, opacity=0.6)

    # Add lines from NYC to each airport in the list
    for faa in faa_codes:
        target_airport = df[df["faa"] == faa]
        if not target_airport.empty:
            plot_data_line = pd.concat([nyc_airports, target_airport])
            fig.add_trace(px.line_geo(plot_data_line, lat="lat", lon="lon").data[0])

    fig.show()

# Example usage
plot_multiple_routes(["LAX", "ORD", "MIA"])  # Replace with desired FAA codes


# Get JFK coordinates
jfk = df[df["faa"] == "JFK"].iloc[0]
jfk_lat, jfk_lon = jfk["lat"], jfk["lon"]

# Compute Euclidean distance for each airport
df["euclidean_dist"] = np.sqrt((df["lat"] - jfk_lat)**2 + (df["lon"] - jfk_lon)**2)

# Display the first few computed distances
print(df[["faa", "name", "euclidean_dist"]].head())




# Function to compute geodesic distance
def compute_geodesic(lat, lon):
    return geodesic((jfk_lat, jfk_lon), (lat, lon)).km  # Convert to kilometers

# Apply function to all airports
df["geodesic_dist"] = df.apply(lambda row: compute_geodesic(row["lat"], row["lon"]), axis=1)


# Create a figure with two subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Plot Euclidean distance histogram
axes[0].hist(df["euclidean_dist"], bins=30, edgecolor="black")
axes[0].set_xlabel("Euclidean Distance from JFK")
axes[0].set_ylabel("Number of Airports")
axes[0].set_title("Euclidean Distance Distribution")

# Plot Geodesic distance histogram
axes[1].hist(df["geodesic_dist"], bins=30, edgecolor="black")
axes[1].set_xlabel("Geodesic Distance from JFK (km)")
axes[1].set_ylabel("Number of Airports")
axes[1].set_title("Geodesic Distance Distribution")

# Adjust layout for clarity
plt.tight_layout()
plt.show()

# Display computed distances
print(df[["faa", "name", "geodesic_dist"]].head())

# Count number of airports per time zone
time_zone_counts = df["tz"].value_counts()

# Display the top time zones
print(time_zone_counts.head(10))  # Show the 10 most common time zones


# Remove NaN values before converting to string
df["tz"] = df["tz"].fillna("Unknown").astype(str)  # Ensure NaNs are replaced before converting

# Drop "Unknown" time zones from the count
time_zone_counts = df[df["tz"] != "Unknown"]["tz"].value_counts()

# Sort values for better visualization
time_zone_counts = time_zone_counts.sort_values(ascending=True)

# Create a horizontal bar chart
plt.figure(figsize=(12, 6))
plt.barh(time_zone_counts.index, time_zone_counts.values, color="royalblue")
plt.xlabel("Number of Airports")
plt.ylabel("Time Zone")
plt.title("Distribution of Airports Across Time Zones")
plt.show()



# Create scatter plot of altitude vs. geodesic distance
plt.figure(figsize=(10, 5))
sns.scatterplot(x=df["geodesic_dist"], y=df["alt"], alpha=0.5, color="red")

plt.xlabel("Geodesic Distance from JFK (km)")
plt.ylabel("Altitude (m)")
plt.title("Altitude vs. Distance from JFK")
plt.show()

# Get the top 10 highest airports
top_highest_airports = df.nlargest(10, "alt")

# Increase figure size for better label visibility
plt.figure(figsize=(12, 6))

# Plot the bar chart
plt.barh(top_highest_airports["name"], top_highest_airports["alt"], color="darkgreen")

# Improve readability
plt.xlabel("Altitude (m)", fontsize=12)
plt.ylabel("Airport Name", fontsize=12)
plt.title("Top 10 Highest Airports in the World", fontsize=14)
plt.gca().invert_yaxis()  # Highest airport at the top
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)

plt.subplots_adjust(left=0.3)  # Adjusts left margin

plt.show()
