import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flights_project import utils
from utils import get_db_connection, load_airports_data
import plotly.graph_objects as go

def plot_airports_with_most_delays(conn=None):
    """
    Generates two bar plots:
    1. Airports with the highest departure delays.
    2. Airports with the highest arrival delays.
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
    query_dep = """
        SELECT origin AS airport, AVG(dep_delay) AS avg_dep_delay
        FROM flights
        GROUP BY origin
        ORDER BY avg_dep_delay DESC
        LIMIT 10
        """
    departure_delays = pd.read_sql_query(query_dep, conn=conn)
    query_arr = """
        SELECT dest AS airport, AVG(arr_delay) AS avg_arr_delay
        FROM flights
        GROUP BY dest
        ORDER BY avg_arr_delay DESC
        LIMIT 10
        """
    arrival_delays = pd.read_sql_query(query_arr, conn=conn)

    fig_dep = go.Figure([
        go.Bar(x=departure_delays["airport"], y=departure_delays["avg_dep_delay"], marker_color="blue", name="Departure Delay")
    ])
    fig_dep.update_layout(title="Top 10 Airports with Most Departure Delays", xaxis_title="Airport", yaxis_title="Avg Departure Delay (min)")

    fig_arr = go.Figure([
        go.Bar(x=arrival_delays["airport"], y=arrival_delays["avg_arr_delay"], marker_color="orange", name="Arrival Delay")
    ])
    fig_arr.update_layout(title="Top 10 Airports with Most Arrival Delays", xaxis_title="Airport", yaxis_title="Avg Arrival Delay (min)")

    return fig_dep, fig_arr

#Most common flight routes from NYC
def plot_nyc_routes():
    """
    Generates a bar plot of the most frequent flight routes from NYC airports (JFK, LGA, EWR).
    """
    nyc_airports = ['JFK', 'LGA', 'EWR']
    if conn is None:
        conn = utils.get_persistent_db_connection()
    query = """
        SELECT origin, dest, COUNT(*) AS num_flights
        FROM flights
        WHERE origin IN ('JFK', 'LGA', 'EWR')
        GROUP BY origin, dest
        ORDER BY num_flights DESC
        LIMIT 10
        """
    route_counts = pd.read_sql_query(query, conn)

    fig = go.Figure([
        go.Bar(y=route_counts["dest"], x=route_counts["num_flights"], orientation="h", marker_color="green", name="Flight Count")
    ])
    fig.update_layout(title="Most Frequent Routes from NYC Airports", xaxis_title="Number of Flights", yaxis_title="Destination")

    return fig

# Effect of wind and precipitation on delays
def plot_weather_effects():
    """
    Generates line graphs showing the dependency between weather conditions (wind speed, precipitation)
    and arrival delays.
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
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

    fig_wind = go.Figure([
        go.Scatter(x=wind_delay["wind_speed"], y=wind_delay["arr_delay"], mode="lines+markers", marker_color="blue", name="Wind Speed vs Delay")
    ])
    fig_wind.update_layout(title="Impact of Wind Speed on Arrival Delays", xaxis_title="Wind Speed (mph)", yaxis_title="Avg Arrival Delay (min)")

    fig_precip = go.Figure([
        go.Scatter(x=precip_delay["precip"], y=precip_delay["arr_delay"], mode="lines+markers", marker_color="red", name="Precipitation vs Delay")
    ])
    fig_precip.update_layout(title="Impact of Precipitation on Arrival Delays", xaxis_title="Precipitation (inches)", yaxis_title="Avg Arrival Delay (min)")

    return fig_wind, fig_precip


# Most frequent airlines from NYC
def plot_nyc_airlines():
    """
    Generates a bar chart of the most frequent airlines flying from NYC airports.
    """
    nyc_airports = ['JFK', 'LGA', 'EWR']

    if conn is None:
        conn = utils.get_persistent_db_connection()
    query = """
        SELECT carrier, COUNT(*) AS num_flights
        FROM flights
        WHERE origin IN ('JFK', 'LGA', 'EWR')
        GROUP BY carrier
        ORDER BY num_flights DESC
        """
    airline_counts = pd.read_sql_query(query, conn)

    fig = go.Figure([
        go.Bar(x=airline_counts["carrier"], y=airline_counts["num_flights"], marker_color="purple", name="Airline Count")
    ])
    fig.update_layout(title="Most Frequent Airlines from NYC Airports", xaxis_title="Carrier", yaxis_title="Number of Flights")

    return fig
