"""
This module analyzes flight delays from the flights database.
Uses the shared DB helpers in utils.
"""

import matplotlib.pyplot as plt
from flights_project import utils

def get_delay_data(conn=None):
    """
    Query the flights database to retrieve departure delay data.
    
    Args:
        conn (sqlite3.Connection, optional): Existing DB connection.
    """
    query = "SELECT dep_delay FROM flights WHERE dep_delay IS NOT NULL;"
    data = utils.execute_query(query, fetch='all', conn=conn)
    return [row[0] for row in data]

def plot_delay_histogram(conn=None):
    delays = get_delay_data(conn)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(delays, bins=30, edgecolor="black")
    ax.set_xlabel("Departure Delay (minutes)")
    ax.set_ylabel("Number of Flights")
    ax.set_title("Distribution of Flight Departure Delays")
    return fig


def main():
    """Run delay analysis (opens its own DB connection if none provided)."""
    plot_delay_histogram()
    plt.show()

if __name__ == "__main__":
    main()
