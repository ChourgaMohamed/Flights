"""
Flight Analysis Module

This module provides various flight analysis functions using the flights database.
Includes functions for distance calculation, querying NYC flights and airports,
plotting top destinations, flight statistics, and delay analysis.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from flights_project import utils

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the Earth specified in decimal degrees.
    """
    R = 3959  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def get_departure_origins(conn=None):
    """
    Retrieve unique departure origins from the flights table and return as a DataFrame with airport names.
    """
    query_origins = "SELECT DISTINCT origin FROM flights;"
    query_airports = "SELECT faa, name FROM airports;"
    if conn is None:
        with utils.get_db_connection() as conn:
            df_origins = pd.read_sql(query_origins, conn)
            df_airports = pd.read_sql(query_airports, conn)
    else:
        df_origins = pd.read_sql(query_origins, conn)
        df_airports = pd.read_sql(query_airports, conn)
    df_origins = df_origins.rename(columns={"origin": "faa"})
    df_origins = df_origins.merge(df_airports, on="faa", how="left")
    return df_origins

def print_sample_flights(conn=None):
    """
    Print sample flight data including distance and coordinates.
    """
    query = """
    SELECT f.distance, a1.lat AS dep_lat, a1.lon AS dep_lon, 
           a2.lat AS arr_lat, a2.lon AS arr_lon
    FROM flights f
    JOIN airports a1 ON f.origin = a1.faa
    JOIN airports a2 ON f.dest = a2.faa
    LIMIT 5;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    print(df)
    return df

def get_nyc_flights(conn=None):
    """
    Retrieve flights departing from NYC airports.
    """
    query = "SELECT * FROM flights WHERE origin IN ('JFK', 'LGA', 'EWR');"
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    return df

def plot_top_nyc_destinations(conn=None):
    """
    Plot top 10 flight destinations from NYC airports using a Plotly Express bar chart.
    """
    query = """
    SELECT dest, COUNT(*) AS flight_count
    FROM flights
    WHERE origin IN ('JFK', 'LGA', 'EWR')
    GROUP BY dest
    ORDER BY flight_count DESC;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    top10 = df.head(10)
    fig = px.bar(
        top10,
        x="dest",
        y="flight_count",
        title="Top 10 NYC Destinations",
        labels={"dest": "Destination Airport", "flight_count": "Number of Flights"},
        color_discrete_sequence=[utils.COLOR_PALETTE["pigment_green"]]
    )
    fig.update_xaxes(tickangle=45)
    return fig

def plot_flight_destinations(origin, month, day, conn=None):
    """
    Plot flight destinations from a given origin on a specified date using a geo scatter plot.
    """
    query = """
    SELECT f.dest, a.lat, a.lon
    FROM flights f
    JOIN airports a ON f.dest = a.faa
    WHERE f.origin = ? AND f.month = ? AND f.day = ?;
    """
    params = (origin, month, day)
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn, params=params)
    else:
        df = pd.read_sql(query, conn, params=params)
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="dest",
        title=f"Flight Destinations from {origin} on {month}/{day}",
        projection="natural earth"
    )
    fig.show()
    return fig

def get_flight_stats(origin, month, day, conn=None):
    """
    Retrieve flight statistics for a given origin and date.
    Prints total flights, unique destinations, and the most visited destination.
    """
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
    params = (origin, month, day)
    if conn is None:
        with utils.get_db_connection() as conn:
            df_stats = pd.read_sql(query, conn, params=params)
    else:
        df_stats = pd.read_sql(query, conn, params=params)
    if not df_stats.empty:
        print(f"📅 Flight Statistics for {origin} on {month}/{day}:")
        print(f"✈️ Total Flights: {df_stats['total_flights'].values[0]}")
        print(f"🌍 Unique Destinations: {df_stats['unique_destinations'].values[0]}")
        print(f"🏆 Most Visited Destination: {df_stats['most_visited'].values[0]} ({df_stats['visit_count'].values[0]} flights)")
    else:
        print(f"No flights found for {origin} on {month}/{day}.")
    return df_stats

def get_plane_type_counts(origin, dest, conn=None):
    """
    Retrieve the count of plane types used on a given route.
    """
    query = """
    SELECT p.type, COUNT(*) AS count
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.origin = ? AND f.dest = ?
    GROUP BY p.type
    ORDER BY count DESC;
    """
    params = (origin, dest)
    data = utils.execute_query(query, params=params, fetch='all', conn=conn)
    plane_type_counts = dict(data) if data else {}
    print(f"🛫 Plane Types Used from {origin} to {dest}:")
    for plane, count in plane_type_counts.items():
        print(f"✈️ {plane}: {count} flights")
    return plane_type_counts

def plot_avg_dep_delay(conn=None):
    """
    Plot average departure delay per airline using Plotly Express.
    """
    query = """
    SELECT a.name AS airline, AVG(f.dep_delay) AS avg_delay
    FROM flights f
    JOIN airlines a ON f.carrier = a.carrier
    GROUP BY a.name
    ORDER BY avg_delay DESC;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df_delays = pd.read_sql(query, conn)
    else:
        df_delays = pd.read_sql(query, conn)
    fig = px.bar(
        df_delays,
        x="airline",
        y="avg_delay",
        title="Average Departure Delay per Airline",
        labels={"airline": "Airline", "avg_delay": "Avg Departure Delay (minutes)"},
        color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]]
    )
    fig.update_xaxes(tickangle=90)
    return fig

def count_delayed_flights(start_month, end_month, destination, conn=None):
    """
    Count the number of delayed flights to a given destination within a specified range of months.
    """
    query = """
    SELECT COUNT(*) AS delayed_flights
    FROM flights
    WHERE dest = ? 
      AND month BETWEEN ? AND ? 
      AND dep_delay > 0;
    """
    params = (destination, start_month, end_month)
    result = utils.execute_query(query, params=params, fetch='one', conn=conn)
    count = result[0] if result else 0
    print(f"🛫 Delayed flights to {destination} from month {start_month} to {end_month}: {count}")
    return count

def analyze_distance_vs_arrival_delay(conn=None):
    """
    Analyze the relationship between flight distance and arrival delay.
    Prints the correlation coefficient and returns a Plotly Express scatter plot with an OLS trendline.
    """
    query = """
    SELECT distance, arr_delay
    FROM flights
    WHERE arr_delay IS NOT NULL;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    df = df.dropna()
    correlation = df["distance"].corr(df["arr_delay"])
    print(f"📊 Correlation between flight distance and arrival delay: {correlation:.3f}")
    fig = px.scatter(
        df,
        x="distance",
        y="arr_delay",
        trendline="ols",
        opacity=0.5,
        title="Relationship Between Flight Distance and Arrival Delay",
        labels={"distance": "Flight Distance (miles)", "arr_delay": "Arrival Delay (minutes)"}
    )
    return correlation, fig

def compute_avg_speed_per_plane_model(conn=None):
    """
    Compute and print the average speed for each plane model.
    """
    query = """
    SELECT p.model, AVG(f.distance / (f.air_time / 60.0)) AS avg_speed
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.air_time IS NOT NULL
    GROUP BY p.model;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df_speed = pd.read_sql(query, conn)
    else:
        df_speed = pd.read_sql(query, conn)
    print("✈️ Average Speed per Plane Model:")
    print(df_speed)
    return df_speed

def get_flights_from_airport(dep_airports, start_date, end_date, conn=None):
    """
    Retrieve flights from the given departure airport(s) within a date range.
    
    Args:
        dep_airports (list or str): List of departure airport codes or a single departure airport code.
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.
        conn (sqlite3.Connection, optional): Existing DB connection.
    
    Returns:
        DataFrame: A DataFrame with flight details.
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
    
    if isinstance(dep_airports, list):
        query = """
        SELECT DATE(f.date) AS date, 
               TIME(f.sched_dep_time) AS sched_dep_time, 
               f.dep_delay AS dep_delay, 
               TIME(f.sched_arr_time) AS sched_arr_time, 
               f.arr_delay AS arr_delay, 
               f.origin, 
               a2.name AS dest_name, 
               a.name AS carrier_name, 
               f.tailnum, 
               p.model
        FROM flights f
        JOIN planes p ON f.tailnum = p.tailnum
        JOIN airlines a ON f.carrier = a.carrier
        JOIN airports a2 ON f.dest = a2.faa
        WHERE f.origin IN ({})
          AND f.date BETWEEN ? AND ?
        ORDER BY f.date;
        """.format(','.join(['?']*len(dep_airports)))
        params = dep_airports + [start_date, end_date]
    else:
        query = """
        SELECT DATE(f.date) AS date, 
               TIME(f.sched_dep_time) AS sched_dep_time, 
               f.dep_delay AS dep_delay, 
               TIME(f.sched_arr_time) AS sched_arr_time, 
               f.arr_delay AS arr_delay,
               f.origin, 
               a2.name AS dest_name, 
               a.name AS carrier_name, 
               f.tailnum, 
               p.model
        FROM flights f
        JOIN planes p ON f.tailnum = p.tailnum
        JOIN airlines a ON f.carrier = a.carrier
        JOIN airports a2 ON f.dest = a2.faa
        WHERE f.origin = ?
          AND f.date BETWEEN ? AND ?
        ORDER BY f.date;
        """
        params = [dep_airports, start_date, end_date]

    df = pd.read_sql(query, conn, params=params)
    return df

def verify_distance_computation(conn=None):
    """
    Verify that the computed geodesic distances (using the haversine formula)
    roughly match the 'distance' column in the flights table.
    Returns a Plotly Express scatter plot comparing database vs. computed distances.
    """
    query = """
    SELECT f.distance as db_distance, a1.lat AS dep_lat, a1.lon AS dep_lon,
           a2.lat AS arr_lat, a2.lon AS arr_lon
    FROM flights f
    JOIN airports a1 ON f.origin = a1.faa
    JOIN airports a2 ON f.dest = a2.faa
    LIMIT 1000;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    
    # Compute the geodesic distance using the haversine function
    df["computed_distance"] = df.apply(
        lambda row: haversine(row["dep_lat"], row["dep_lon"], row["arr_lat"], row["arr_lon"]),
        axis=1
    )
    df["difference"] = df["db_distance"] - df["computed_distance"]
    df["relative_error"] = abs(df["difference"] / df["db_distance"])
    
    mean_diff = df["difference"].abs().mean()
    mean_rel_err = df["relative_error"].mean()
    text1=(f"Mean absolute difference: {mean_diff:.2f} km")
    text2=(f"Mean relatifve error: {mean_rel_err:.2%}")
    
    fig = px.scatter(
        df,
        x="db_distance",
        y="computed_distance",
        opacity=0.5,
        color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]],
        title="Database vs Computed Distance",
        labels={"db_distance": "Database Distance (km)", "computed_distance": "Computed Distance (km)"}
    )
    # Add a reference line y=x using Plotly Graph Objects
    min_val = min(df["db_distance"].min(), df["computed_distance"].min())
    max_val = max(df["db_distance"].max(), df["computed_distance"].max())
    line = go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode="lines",
        line=dict(color=utils.COLOR_PALETTE["pakistan_green"], dash="dash"),
        name="y = x"
    )
    fig.add_trace(line)
    return fig, text1, text2

def main():
    # Opening an persistent connection to the database
    conn = utils.get_persistent_db_connection()

    print("All Departure Origins in Database:")
    origins = get_departure_origins(conn)
    print(origins)

    print("Sample Flight Data:")
    print_sample_flights(conn)
    
    print("\nNYC Flights (first 5 rows):")
    nyc_flights = get_nyc_flights()
    print(nyc_flights.head())
    
    print("\nPlotting Top 10 NYC Destinations...")
    fig1 = plot_top_nyc_destinations(conn)
    fig1.show()
    
    print("\nPlotting Flight Destinations from JFK on 1/1...")
    plot_flight_destinations("JFK", 1, 1, conn)
    
    print("\nFlight Statistics for JFK on 1/1:")
    get_flight_stats("JFK", 1, 1, conn)
    
    print("\nPlane Type Counts from JFK to LAX:")
    get_plane_type_counts("JFK", "LAX")
    
    print("\nPlotting Average Departure Delay per Airline...")
    fig2 = plot_avg_dep_delay(conn)
    fig2.show()
    
    print("\nCounting Delayed Flights to LAX from Jan to Mar:")
    count_delayed_flights(1, 3, "LAX")
    
    print("\nAnalyzing Distance vs Arrival Delay:")
    corr, fig3 = analyze_distance_vs_arrival_delay(conn)
    print(f"Correlation: {corr:.3f}")
    fig3.show()
    
    print("\nComputing Average Speed per Plane Model:")
    compute_avg_speed_per_plane_model(conn)

    print("\nVerifying computed distances against the database values...")
    fig4, text1,text2 = verify_distance_computation(conn)
    fig4.show()
    print(text1)
    print(text2)

    print("\nFlights from JFK between 2023-01-01 and 2023-12-31:")
    flights_df = get_flights_from_airport("JFK", "2023-01-01", "2023-12-31", conn)
    print(flights_df.head())

if __name__ == "__main__":
    main()
