"""
This module computes general flight statistics.
Uses a provided DB connection via utils.
"""

import pandas as pd
from flights_project import utils

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

def main():
    """Run flight statistics computations (opens its own DB connection if none provided)."""
    conn = utils.get_persistent_db_connection()

    total = get_total_flights(conn)
    print(f"Total flights: {total}")

    busiest = get_busiest_airports(conn=conn)
    print("Busiest Airports (top 5):")
    print(busiest.to_string(index=False))

if __name__ == "__main__":
    main()