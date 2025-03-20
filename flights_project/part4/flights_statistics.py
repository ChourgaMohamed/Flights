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


def get_nyc_flight_statistics():
    nyc_airports = ["JFK", "LGA", "EWR"]

    with get_db_connection() as conn:
        query_total = """
        SELECT COUNT(*) AS total_nyc_flights
        FROM flights
        WHERE origin IN (?, ?, ?) AND year = 2023
        """
        total_flights = pd.read_sql_query(query_total, conn, params=nyc_airports)

        query_per_airport = """
        SELECT origin, COUNT(*) AS num_flights
        FROM flights
        WHERE origin IN (?, ?, ?) AND year = 2023
        GROUP BY origin
        ORDER BY num_flights DESC
        """
        flights_per_airport = pd.read_sql_query(query_per_airport, conn, params=nyc_airports)

    print("📊 Total Flights Departing from NYC Airports in 2023:", total_flights.iloc[0, 0])
    print("\n✈️ Breakdown by Airport:")
    print(flights_per_airport)

    return total_flights.iloc[0, 0], flights_per_airport
