"""
This module computes general flight statistics.
Uses a provided DB connection via utils.
"""

import pandas as pd
from flights_project import utils

def get_all_arrival_airports(conn=None):
    """
    Return a list of all unique arrival airports using a provided DB connection.

    Returns a DataFrame with columns:
        - faa (airport code)
        - name (airport name)
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
    query = """
    SELECT DISTINCT a.faa, a.name
    FROM flights f
    JOIN airports a ON f.dest = a.faa;
    """
    df = utils.execute_query(query, fetch='all', conn=conn)
    df = pd.DataFrame(df, columns=["faa", "name"])
    
    return df

def get_total_flights(conn=None):
    """Return the total number of flights using a provided DB connection."""
    query = "SELECT COUNT(*) FROM flights;"
    result = utils.execute_query(query, fetch='one', conn=conn)
    return result[0] if result else 0

def get_busiest_airports(n=5, conn=None):
    """Return the top n busiest airports by flight count using a provided DB connection."""
    query = """
    SELECT origin, COUNT(*) as flight_count
    FROM flights
    GROUP BY origin
    ORDER BY flight_count DESC
    LIMIT ?;
    """
    result = utils.execute_query(query, params=(n,), fetch='all', conn=conn)

    # Convert result to a pandas DataFrame for better readability
    df = pd.DataFrame(result, columns=["Airport", "Flights"])
    return df

def get_flight_statistics(dep_airports, start_date, end_date, conn=None):
    """
    Retrieve flight statistics for a given departure airport(s) and date range.
    
    Args:
        dep_airports (list): List of departure airport codes.
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.
        conn (sqlite3.Connection, optional): Existing DB connection.
    
    Returns:
        DataFrame: A DataFrame with total flights, average departure delay, average airtime, and average arrival delay.
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
    
    query = """
    SELECT origin,
           COUNT(*) AS total_flights,
           AVG(dep_delay) AS avg_departure_delay,
           AVG(air_time) AS avg_air_time,
           AVG(arr_delay) AS avg_arrival_delay
    FROM flights
    WHERE origin IN ({})
      AND date BETWEEN ? AND ?
    GROUP BY origin
    """.format(','.join(['?']*len(dep_airports)))
    
    params = dep_airports + [start_date, end_date]
    df = pd.read_sql_query(query, conn, params=params)
    
    return df

def main():
    """Run flight statistics computations (opens its own DB connection if none provided)."""
    conn = utils.get_persistent_db_connection()

    total = get_total_flights(conn)
    print(f"Total flights: {total}")

    busiest = get_busiest_airports(conn=conn)
    print("Busiest Airports (top 5):")
    print(busiest.to_string(index=False))

    dep_airports = ["JFK", "LGA", "EWR"]
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    stats_df = get_flight_statistics(dep_airports, start_date, end_date, conn)
    print (stats_df.to_string(index=False))

if __name__ == "__main__":
    main()