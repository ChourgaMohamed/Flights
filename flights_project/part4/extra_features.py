import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from flights_project import utils
import seaborn as sns
from utils import get_db_connection, load_airports_data

def get_flight_statistics(dep_airport, arr_airport):
    with get_db_connection() as conn:
        query = """
        SELECT COUNT(*) AS total_flights,
            AVG(dep_delay) AS avg_departure_delay
            AVG(air_time) AS avg_air_time,
            AVG(arr_delay) AS avg_arrival_delay
        FROM flights
        WHERE origin = ? AND dest = ?
        """
        result = pd.read_sql_query(query, conn, params=(dep_airport, arr_airport))

    print(f"Flight statistics for {dep_airport} → {arr_airport}")
    print(result)

def delay_histogram(airport, start_date, end_date):
    with get_db_connection() as conn:
        query = """
        SELECT dep_delay, arr_delay
        FROM flights
        WHERE origin = ? AND date BETWEEN ? AND ?
        """
        df = pd.read_sql_query(query, conn, params=(airport, start_date, end_date))

    if df.empty:
        print(f"No delay data available for {airport} between {start_date} and {end_date}.")
        return None
    plt.figure(figsize=(10, 6))
    sns.kdeplot(df["dep_delay"], color="darkgreen", linewidth=2, label="Departure delay")
    sns.kdeplot(df["arr_delay"], color="limegreen", linewidth=2, label="Arrival delay")
    plt.xlabel("Delay (minutes)")
    plt.ylabel("Frequency")
    plt.title(f"Statistics delays at {airport} date: {start_date} - {end_date}")
    plt.legend()
    plt.show()
