#PART 3
import pandas as pd
import plotly.express as px
import numpy as np
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3


# Function to calculate distance between two lat/lon points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


# Path to the database
db_path = "flights_database.db"

# Establish connection
conn = sqlite3.connect(db_path)

# Updated SQL query with correct column names
query = """
SELECT f.distance, a1.lat AS dep_lat, a1.lon AS dep_lon, 
       a2.lat AS arr_lat, a2.lon AS arr_lon
FROM flights f
JOIN airports a1 ON f.origin = a1.faa
JOIN airports a2 ON f.dest = a2.faa
LIMIT 5;
"""

df = pd.read_sql(query, conn)

# Print DataFrame to check results
print(df)

# Close the database connection
conn.close()


# Connect to the database
conn = sqlite3.connect(db_path)


query_nyc_airports = """
SELECT faa, name, tzone
FROM airports
WHERE faa IN ('JFK', 'LGA', 'EWR');
"""

df_nyc_airports = pd.read_sql(query_nyc_airports, conn)

# Print the result
print("NYC Airports:")
print(df_nyc_airports)

# Close connection
conn.close()




# Connect to the database
conn = sqlite3.connect(db_path)

# Query only JFK, LGA, and EWR airports
query_nyc_airports = """
SELECT faa, name, tzone
FROM airports
WHERE faa IN ('JFK', 'LGA', 'EWR');
"""

df_nyc_airports = pd.read_sql(query_nyc_airports, conn)

# Print the result
print("NYC Airports:")
print(df_nyc_airports)

# Close connection
conn.close()


# Connect to the database
conn = sqlite3.connect(db_path)

# Query flights departing from NYC airports
query_nyc_flights = """
SELECT *
FROM flights
WHERE origin IN ('JFK', 'LGA', 'EWR');
"""

df_nyc_flights = pd.read_sql(query_nyc_flights, conn)

# Print first few rows
print("Flights Departing from NYC:")
print(df_nyc_flights.head())

# Close connection
conn.close()

# Connect to the database
conn = sqlite3.connect(db_path)

# Query to get the number of flights per destination
query_nyc_destinations = """
SELECT dest, COUNT(*) AS flight_count
FROM flights
WHERE origin IN ('JFK', 'LGA', 'EWR')
GROUP BY dest
ORDER BY flight_count DESC;
"""

df_nyc_destinations = pd.read_sql(query_nyc_destinations, conn)

# Print the result
print("Top Flight Destinations from NYC:")
print(df_nyc_destinations.head(10))  # Show top 10 destinations

# Close connection
conn.close()


# Plot the top 10 destinations
plt.figure(figsize=(10, 6))
plt.bar(df_nyc_destinations["dest"][:10], df_nyc_destinations["flight_count"][:10], color="royalblue")

# Add labels and title
plt.xlabel("Destination Airport")
plt.ylabel("Number of Flights")
plt.title("Top 10 Flight Destinations from NYC")
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# Show the plot
plt.show()

def plot_flight_destinations(db_path, origin, month, day):
    # Connect to database
    conn = sqlite3.connect(db_path)

    # SQL Query to get destinations for given date and origin
    query = """
    SELECT f.dest, a.lat, a.lon
    FROM flights f
    JOIN airports a ON f.dest = a.faa
    WHERE f.origin = ? AND f.month = ? AND f.day = ?;
    """

    # Fetch data
    df_flights = pd.read_sql(query, conn, params=(origin, month, day))

    # Close connection
    conn.close()

    # Plot results
    fig = px.scatter_geo(df_flights, lat="lat", lon="lon",
                         hover_name="dest",
                         title=f"Flight Destinations from {origin} on {month}/{day}",
                         projection="natural earth")

    fig.show()


# Example usage:
plot_flight_destinations(db_path, "JFK", 1, 1)  # Example: Flights from JFK on January 1st

def get_flight_stats(db_path, origin, month, day):
    # Connect to database
    conn = sqlite3.connect(db_path)

    # SQL Query to get statistics for the given date
    query = """
    SELECT COUNT(*) AS total_flights,
           COUNT(DISTINCT dest) AS unique_destinations,
           dest AS most_visited,
           COUNT(dest) AS visit_count
    FROM flights
    WHERE origin = ? AND month = ? AND day = ?
    GROUP BY dest
    ORDER BY visit_count DESC
    LIMIT 1;
    """

    # Fetch data
    df_stats = pd.read_sql(query, conn, params=(origin, month, day))

    # Close connection
    conn.close()

    # Print statistics
    if not df_stats.empty:
        print(f"📅 Flight Statistics for {origin} on {month}/{day}:")
        print(f"✈️ Total Flights: {df_stats['total_flights'].values[0]}")
        print(f"🌍 Unique Destinations: {df_stats['unique_destinations'].values[0]}")
        print(f"🏆 Most Visited Destination: {df_stats['most_visited'].values[0]} ({df_stats['visit_count'].values[0]} flights)")
    else:
        print(f"No flights found for {origin} on {month}/{day}.")

# Example usage:
get_flight_stats(db_path, "JFK", 1, 1)  # Example: Flights from JFK on January 1st


def get_plane_type_counts(db_path, origin, dest):
    # Connect to database
    conn = sqlite3.connect(db_path)

    # SQL Query to count plane types on the given route
    query = """
    SELECT p.type, COUNT(*) AS count
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.origin = ? AND f.dest = ?
    GROUP BY p.type
    ORDER BY count DESC;
    """

    # Fetch data
    df_plane_types = pd.read_sql(query, conn, params=(origin, dest))

    # Close connection
    conn.close()

    # Convert to dictionary
    plane_type_counts = dict(zip(df_plane_types["type"], df_plane_types["count"]))

    # Print results
    print(f"🛫 Plane Types Used from {origin} to {dest}:")
    for plane, count in plane_type_counts.items():
        print(f"✈️ {plane}: {count} flights")

    return plane_type_counts

# Example usage:
get_plane_type_counts(db_path, "JFK", "LAX")  # Example: Flights from JFK to LAX

def plot_avg_dep_delay(db_path):
    # Connect to database
    conn = sqlite3.connect(db_path)

    # SQL Query to get avg departure delay per airline
    query = """
    SELECT a.name AS airline, AVG(f.dep_delay) AS avg_delay
    FROM flights f
    JOIN airlines a ON f.carrier = a.carrier
    GROUP BY a.name
    ORDER BY avg_delay DESC;
    """

    # Fetch data
    df_delays = pd.read_sql(query, conn)

    # Close connection
    conn.close()

    # Plot
    plt.figure(figsize=(12, 6))
    plt.bar(df_delays["airline"], df_delays["avg_delay"], color="red")
    plt.xlabel("Airline")
    plt.ylabel("Avg Departure Delay (minutes)")
    plt.title("Average Departure Delay per Airline")
    plt.xticks(rotation=90)  # Rotate x-axis labels for readability
    plt.show()

# usage:
plot_avg_dep_delay(db_path)

# Write a function that takes as input a range of months and a destination and returns the amount of delayed flights to that destination.


def count_delayed_flights(db_path, start_month, end_month, destination):
    """Returns the number of delayed flights to a given destination within a specified range of months."""

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to count delayed flights
    query = """
    SELECT COUNT(*) AS delayed_flights
    FROM flights
    WHERE dest = ? 
    AND month BETWEEN ? AND ? 
    AND dep_delay > 0;
    """

    # Execute query with parameters
    cursor.execute(query, (destination, start_month, end_month))

    # Fetch result
    result = cursor.fetchone()[0]

    # Close connection
    conn.close()

    # Print the result
    print(f"🛫 Delayed flights to {destination} from month {start_month} to {end_month}: {result}")

    return result


# usage
count_delayed_flights(db_path, 1, 3, "LAX")  # Example: Count delayed flights to LAX from Jan to March

# Write a function that takes a destination airport as input and returns the top 5
# airplane manufacturers with planes departing to this destination. For this task,
# you have to combine data from flights and planes

def get_top_manufacturers(db_path, destination):
    """
    Returns the top 5 airplane manufacturers with planes departing to the given destination.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # SQL query to retrieve the top 5 manufacturers for flights to the given destination
    query = """
    SELECT p.manufacturer, COUNT(*) AS flight_count
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.dest = ?
    GROUP BY p.manufacturer
    ORDER BY flight_count DESC
    LIMIT 5;
    """

    # Execute query
    df = pd.read_sql(query, conn, params=(destination,))

    # Close connection
    conn.close()

    # Print results
    print(f"✈️ Top 5 Airplane Manufacturers for flights to {destination}:")
    print(df)

    return df

# Example usage
get_top_manufacturers(db_path, "LAX")  # Example: Flights to LAX

# Investigate whether there is a relationship between the distance of a flight and
# the arrival delay time.


# Connect to the database
conn = sqlite3.connect(db_path)

# SQL query to get distance and arrival delay
query = """
SELECT distance, arr_delay
FROM flights
WHERE arr_delay IS NOT NULL;
"""

# Fetch data
df = pd.read_sql(query, conn)

# Close the connection
conn.close()

# Drop any NaN values just in case
df = df.dropna()

# Compute correlation
correlation = df["distance"].corr(df["arr_delay"])
print(f"📊 Correlation between flight distance and arrival delay: {correlation:.3f}")

# Plot scatter plot with regression line
plt.figure(figsize=(10, 6))
sns.regplot(x=df["distance"], y=df["arr_delay"], scatter_kws={'alpha':0.5}, line_kws={"color":"red"})
plt.xlabel("Flight Distance (miles)")
plt.ylabel("Arrival Delay (minutes)")
plt.title("Relationship Between Flight Distance and Arrival Delay")
plt.grid()
plt.show()


# Group the table flights by plane model using the tailnum . For each model,
# compute the average speed by taking the average of the distance divided by flight
# time over all flights of that model. Use this information to fill the column speed
# in the table planes

# Connect to database
conn = sqlite3.connect(db_path)

# SQL query to calculate average speed per plane model
query = """
SELECT p.model, AVG(f.distance / (f.air_time / 60.0)) AS avg_speed
FROM flights f
JOIN planes p ON f.tailnum = p.tailnum
WHERE f.air_time IS NOT NULL
GROUP BY p.model;
"""

# Fetch data
df_speed = pd.read_sql(query, conn)

# Print result
print("✈️ Average Speed per Plane Model:")
print(df_speed)

# Close connection
conn.close()

# The wind direction is given in weather in degrees. Compute for each airport
# the direction the plane follows when flying there from New York.

# Function to calculate flight direction
def calculate_flight_direction(dep_lat, dep_lon, arr_lat, arr_lon):
    delta_lon = np.radians(arr_lon - dep_lon)
    dep_lat, arr_lat = np.radians(dep_lat), np.radians(arr_lat)

    x = np.sin(delta_lon) * np.cos(arr_lat)
    y = np.cos(dep_lat) * np.sin(arr_lat) - (np.sin(dep_lat) * np.cos(arr_lat) * np.cos(delta_lon))
    bearing = np.degrees(np.arctan2(x, y))

    return (bearing + 360) % 360  # Convert to 0-360 degrees


# Connect to database
conn = sqlite3.connect(db_path)

# SQL Query to get flight details & wind direction
query = """
SELECT f.origin, f.dest, a1.lat AS dep_lat, a1.lon AS dep_lon, 
       a2.lat AS arr_lat, a2.lon AS arr_lon, w.wind_dir
FROM flights f
JOIN airports a1 ON f.origin = a1.faa
JOIN airports a2 ON f.dest = a2.faa
LEFT JOIN weather w ON f.origin = w.origin AND f.year = w.year AND f.month = w.month AND f.day = w.day
WHERE f.origin IN ('JFK', 'LGA', 'EWR')
LIMIT 1000;
"""

df = pd.read_sql(query, conn)
print(df)

# Compute flight direction
df["flight_direction"] = df.apply(lambda row: calculate_flight_direction(
    row["dep_lat"], row["dep_lon"], row["arr_lat"], row["arr_lon"]), axis=1)

# Compute difference between wind direction & flight direction
df["wind_alignment"] = abs(df["flight_direction"] - df["wind_dir"])

# Print first few rows
print(df[["origin", "dest", "flight_direction", "wind_dir", "wind_alignment"]].head())

# Close database connection
conn.close()
# Write a function that computes the inner product between the flight direction
# and the wind speed of a given flight

# Connect to the database
conn = sqlite3.connect(db_path)

# Query flight direction and wind speed
query = """
SELECT f.origin, f.dest, 
       f.air_time, f.distance,
       w.wind_speed, w.wind_dir,
       (f.distance / f.air_time) AS flight_speed
FROM flights f
JOIN weather w ON f.origin = w.origin AND f.time_hour = w.time_hour
WHERE f.air_time IS NOT NULL AND f.distance IS NOT NULL
"""

df = pd.read_sql(query, conn)

# Close connection
conn.close()

# Compute the inner product
df["inner_product"] = df["flight_speed"] * df["wind_speed"] * np.cos(np.radians(df["wind_dir"]))

# Display result
print(df[["origin", "dest", "inner_product"]].head())

# Is there a relation between the sign of this inner product and the air time?


# Connect to the database
conn = sqlite3.connect(db_path)

# SQL Query to fetch necessary data
query = """
SELECT f.origin, f.dest, f.air_time, 
       (COS(RADIANS(f.air_time)) * w.wind_speed) AS inner_product
FROM flights f
JOIN weather w ON f.origin = w.origin
WHERE w.wind_speed IS NOT NULL AND f.air_time IS NOT NULL;
"""

# Read into a DataFrame
df = pd.read_sql(query, conn)

# Close connection
conn.close()

# Print first few rows to check if data is retrieved
print(df.head())


# Ensure there is data
if not df.empty:
    plt.scatter(df["inner_product"], df["air_time"], alpha=0.5, c=np.sign(df["inner_product"]), cmap='coolwarm')
    plt.xlabel("Inner Product (Wind Influence)")
    plt.ylabel("Air Time (minutes)")
    plt.title("Wind Influence vs Air Time")
    plt.show()
else:
    print("No data retrieved! Check the SQL query.")