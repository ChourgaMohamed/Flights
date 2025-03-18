"""
Weather Analysis Module

This module provides weather-related flight analysis functions.
Includes functions for flight direction calculation, wind alignment analysis,
and inner product analysis between flight direction and wind speed.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flights_project import utils

def calculate_flight_direction(dep_lat, dep_lon, arr_lat, arr_lon):
    """
    Calculate the flight direction (bearing) from departure to arrival.
    Returns bearing in degrees (0-360).
    """
    delta_lon = np.radians(arr_lon - dep_lon)
    dep_lat, arr_lat = np.radians(dep_lat), np.radians(arr_lat)
    x = np.sin(delta_lon) * np.cos(arr_lat)
    y = np.cos(dep_lat) * np.sin(arr_lat) - np.sin(dep_lat) * np.cos(arr_lat) * np.cos(delta_lon)
    bearing = np.degrees(np.arctan2(x, y))
    return (bearing + 360) % 360

def analyze_wind_direction(conn=None):
    """
    Analyze wind direction by computing the flight direction and its alignment with wind direction.
    Prints a sample of computed flight directions and wind alignments.
    """
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
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    
    # Compute flight direction
    df["flight_direction"] = df.apply(lambda row: calculate_flight_direction(
        row["dep_lat"], row["dep_lon"], row["arr_lat"], row["arr_lon"]), axis=1)
    
    # Compute wind alignment as absolute difference between flight direction and wind direction
    df["wind_alignment"] = abs(df["flight_direction"] - df["wind_dir"])
    
    print("Sample Wind Direction Analysis:")
    print(df[["origin", "dest", "flight_direction", "wind_dir", "wind_alignment"]].head())
    return df

def analyze_inner_product_and_airtime(conn=None):
    """
    Analyze the inner product between flight direction and wind speed,
    and examine its relationship with air time.
    Computes the inner product, correlation with air time, and plots a violin plot.
    """
    query = """
    SELECT f.origin, f.dest, f.air_time, f.distance,
           w.wind_speed, w.wind_dir,
           (f.distance / f.air_time) AS flight_speed
    FROM flights f
    JOIN weather w ON f.origin = w.origin AND f.time_hour = w.time_hour
    WHERE f.air_time IS NOT NULL AND f.distance IS NOT NULL;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    
    # Compute inner product: flight_speed * wind_speed * cos(wind_dir in radians)
    df["inner_product"] = df["flight_speed"] * df["wind_speed"] * np.cos(np.radians(df["wind_dir"]))
    
    df = df.dropna(subset=["inner_product", "air_time"])
    
    print("Sample Inner Product Analysis:")
    print(df[["origin", "dest", "inner_product"]].head())
    
    # Relation between inner product and air_time
    df["inner_product_sign"] = np.sign(df["inner_product"])
    
    correlation = df[["inner_product", "air_time"]].corr()
    print("Correlation between inner product and air_time:")
    print(correlation)
    
    # For plotting, select flights with highest positive and lowest negative inner product values
    highest_positive = df.nlargest(100, "inner_product")
    lowest_negative = df.nsmallest(100, "inner_product")
    combined_df = pd.concat([lowest_negative, highest_positive])
    # Add a column for category
    combined_df["Category"] = np.where(combined_df["inner_product"] >= 0, "High Positive", "High Negative")
    
    plt.figure(figsize=(10,6))
    sns.violinplot(x="Category", y="air_time", data=combined_df,
                   palette={"High Positive": "blue", "High Negative": "red"})
    plt.title("Air Time vs Inner Product Categories (Selected Flights)")
    plt.xlabel("Inner Product Category")
    plt.ylabel("Air Time (minutes)")
    plt.show()
    
    return df

def main():
    """Run weather-related flight analyses."""
    print("Analyzing Wind Direction and Alignment...")
    analyze_wind_direction()
    
    print("\nAnalyzing Inner Product and Air Time...")
    analyze_inner_product_and_airtime()

if __name__ == "__main__":
    main()
