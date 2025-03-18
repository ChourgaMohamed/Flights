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
    y = (np.cos(dep_lat) * np.sin(arr_lat) -
         np.sin(dep_lat) * np.cos(arr_lat) * np.cos(delta_lon))
    bearing = np.degrees(np.arctan2(x, y))
    return (bearing + 360) % 360

def analyze_tailwind_headwind_effect(conn=None):
    """
    Analyze how tailwinds or headwinds (derived from the difference 
    between flight direction and wind direction) affect flight times.
    """
    # Pull in data: flight times, lat/lon for origin/dest, wind data
    query = """
    SELECT 
        f.origin, f.dest, 
        f.air_time, 
        f.distance,
        a1.lat AS dep_lat, 
        a1.lon AS dep_lon,
        a2.lat AS arr_lat, 
        a2.lon AS arr_lon,
        w.wind_speed, 
        w.wind_dir
    FROM flights f
    JOIN airports a1 
        ON f.origin = a1.faa
    JOIN airports a2 
        ON f.dest = a2.faa
    JOIN weather w 
        ON f.origin = w.origin 
        AND f.year = w.year 
        AND f.month = w.month 
        AND f.day = w.day
        AND f.hour = w.hour
    WHERE f.air_time IS NOT NULL 
      AND f.distance IS NOT NULL
      AND w.wind_speed IS NOT NULL
      AND w.wind_dir IS NOT NULL
    """
    # Use provided connection or get a new one
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)

    # 1. Calculate the flight direction
    df["flight_direction"] = df.apply(
        lambda row: calculate_flight_direction(
            row["dep_lat"], row["dep_lon"], row["arr_lat"], row["arr_lon"]
        ),
        axis=1
    )

    # 2. Compute difference between flight direction and wind direction
    #    If this difference is near 0°, the wind is a tailwind;
    #    near 180° means a headwind.
    df["direction_diff"] = df["flight_direction"] - df["wind_dir"]

    # 3. Tailwind/Headwind component:
    #    > Positive = tailwind (wind in same direction as flight)
    #    > Negative = headwind (wind against flight direction)
    df["tailwind_component"] = df["wind_speed"] * np.cos(
        np.radians(df["direction_diff"])
    )

    # 4. Look at correlation with air_time
    correlation = df[["tailwind_component", "air_time"]].corr()
    print("Sample Tailwind/Headwind Component Analysis:")
    print(df[["origin", "dest", "flight_direction", "wind_dir", 
              "tailwind_component", "air_time"]].head())
    
    print("\nCorrelation between tailwind component and air_time:")
    print(correlation)

    # Optional: quick plot to visualize relationship
    plt.figure(figsize=(8,5))
    sns.scatterplot(
        x="tailwind_component", 
        y="air_time", 
        data=df.sample(n=2000, random_state=1),  # sample to reduce clutter
        alpha=0.5
    )
    plt.title("Tailwind/Headwind Component vs. Air Time")
    plt.xlabel("Tailwind Component (positive = tailwind, negative = headwind)")
    plt.ylabel("Air Time (minutes)")
    plt.show()

    return df

def main():
    """Run the improved tailwind/headwind effect analysis."""
    print("Analyzing Tailwind/Headwind Effect on Air Time...")
    analyze_tailwind_headwind_effect()

if __name__ == "__main__":
    main()
