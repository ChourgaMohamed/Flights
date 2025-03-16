import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flights_project import utils
from utils import get_db_connection, load_airports_data

def plot_airports_with_most_delays():
    """
    Generates two bar plots:
    1. Airports with the highest departure delays.
    2. Airports with the highest arrival delays.
    """

    with get_db_connection() as conn:
        query_dep = """
        SELECT origin AS airport, AVG(dep_delay) AS avg_dep_delay
        FROM flights
        GROUP BY origin
        ORDER BY avg_dep_delay DESC
        LIMIT 10
        """
        departure_delays = pd.read_sql_query(query_dep, conn)
        query_arr = """
        SELECT dest AS airport, AVG(arr_delay) AS avg_arr_delay
        FROM flights
        GROUP BY dest
        ORDER BY avg_arr_delay DESC
        LIMIT 10
        """
        arrival_delays = pd.read_sql_query(query_arr, conn)

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 4))
    sns.barplot(data=departure_delays, x="airport", y="avg_dep_delay", palette="Blues_r")
    plt.xlabel("Airports")
    plt.ylabel("Average departure delay (minutes)")
    plt.title("Top 3 Airports with most departure delays")
    plt.xticks(rotation=45)
    plt.show()

    plt.figure(figsize=(10, 4))
    sns.barplot(data=arrival_delays, x="airport", y="avg_arr_delay", palette="Oranges_r")
    plt.xlabel("Airports")
    plt.ylabel("Average arrival elay (minutes)")
    plt.title("Top 10 airports with most arrival delays")
    plt.xticks(rotation=45)
    plt.show()

#Most common flight routes from NYC
def plot_nyc_routes():
    """
    Generates a bar plot of the most frequent flight routes from NYC airports (JFK, LGA, EWR).
    """
    nyc_airports = ['JFK', 'LGA', 'EWR']

    with get_db_connection() as conn:
        query = """
        SELECT origin, dest, COUNT(*) AS num_flights
        FROM flights
        WHERE origin IN ('JFK', 'LGA', 'EWR')
        GROUP BY origin, dest
        ORDER BY num_flights DESC
        LIMIT 10
        """
        route_counts = pd.read_sql_query(query, conn)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=route_counts, x="num_flights", y="dest", hue="origin", dodge=False)
    plt.xlabel("Number of Flights")
    plt.ylabel("Destination")
    plt.title("Most Frequent Routes from NYC Airports")
    plt.legend(title="Origin")
    plt.show()

# Effect of wind and precipitation on delays
def plot_weather_effects():
    """
    Generates line graphs showing the dependency between weather conditions (wind speed, precipitation)
    and arrival delays.
    """

    with get_db_connection() as conn:
        query = """
        SELECT f.carrier, w.wind_speed, w.precip, f.arr_delay
        FROM flights f
        JOIN weather w 
        ON f.origin = w.origin 
        AND f.day = w.day 
        AND f.month = w.month 
        AND f.year = w.year
        """
        weather_effects = pd.read_sql_query(query, conn)

    wind_delay = weather_effects.groupby("wind_speed")["arr_delay"].mean().reset_index()
    precip_delay = weather_effects.groupby("precip")["arr_delay"].mean().reset_index()

    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=wind_delay, x="wind_speed", y="arr_delay", marker="o", color="blue")
    plt.xlabel("Wind speed (mph)")
    plt.ylabel("Average arrival delay (minutes)")
    plt.title("Influence of wind speed on arrival delay")
    plt.show()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=precip_delay, x="precip", y="arr_delay", marker="o", color="red")
    plt.xlabel("Precipitation (inches)")
    plt.ylabel("Average arrival delay (minutes)")
    plt.title("Influence of precipitation on arrival delay")
    plt.show()


# Most frequent airlines from NYC
def plot_nyc_airlines():
    """
    Generates a bar chart of the most frequent airlines flying from NYC airports.
    """
    nyc_airports = ['JFK', 'LGA', 'EWR']

    with get_db_connection() as conn:
        query = """
        SELECT carrier, COUNT(*) AS num_flights
        FROM flights
        WHERE origin IN ('JFK', 'LGA', 'EWR')
        GROUP BY carrier
        ORDER BY num_flights DESC
        """
        airline_counts = pd.read_sql_query(query, conn)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=airline_counts, x="carrier", y="num_flights", palette="coolwarm")
    plt.xlabel("Carrier")
    plt.ylabel("Number of Flights")
    plt.title("Most Frequent Airlines from NYC Airports")
    plt.show()
