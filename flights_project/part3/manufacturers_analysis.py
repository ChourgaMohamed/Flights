"""
This module provides analysis on airplane manufacturers based on flight data.
Uses a provided DB connection via utils.
"""

import matplotlib.pyplot as plt
from flights_project import utils

def get_manufacturer_data(destination="LAX", conn=None):
    """
    Retrieve top 5 airplane manufacturers for flights to a given destination.
    
    Args:
        destination (str): Destination airport FAA code.
        conn (sqlite3.Connection, optional): Existing DB connection.
    """
    query = """
    SELECT p.manufacturer, COUNT(*) AS flight_count
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.dest = ?
    GROUP BY p.manufacturer
    ORDER BY flight_count DESC
    LIMIT 5;
    """
    data = utils.execute_query(query, params=(destination,), fetch='all', conn=conn)
    return data

def plot_manufacturer_data(destination="LAX", conn=None):
    """Plot the manufacturer data as a bar chart using a provided DB connection."""
    data = get_manufacturer_data(destination, conn)
    if not data:
        return f"No data available for destination: {destination}"
    manufacturers = [row[0] for row in data]
    counts = [row[1] for row in data]
    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(manufacturers, counts, edgecolor="black")
    ax.set_xlabel("Manufacturer")
    ax.set_ylabel("Number of Flights")
    ax.set_title(f"Top Airplane Manufacturers for flights to {destination}")
    return fig


def main():
    """Run manufacturers analysis (opens its own DB connection if none provided)."""
    plot_manufacturer_data("LAX")
    plt.show()

if __name__ == "__main__":
    main()
