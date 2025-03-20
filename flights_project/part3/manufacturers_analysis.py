"""
This module provides analysis on airplane manufacturers based on flight data.
Uses a provided DB connection via utils.
"""

import pandas as pd
import plotly.express as px
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
    """Plot the manufacturer data as a bar chart using Plotly Express."""
    data = get_manufacturer_data(destination, conn)
    if not data:
        return f"No data available for destination: {destination}"
    
    # Prepare data for plotting
    manufacturers = [row[0] for row in data]
    counts = [row[1] for row in data]
    df = pd.DataFrame({
        "Manufacturer": manufacturers,
        "Number of Flights": counts
    })
    
    # Create bar chart with a color from the shared palette
    fig = px.bar(
        df,
        x="Manufacturer",
        y="Number of Flights",
        title=f"Top Airplane Manufacturers for Flights to {destination}",
        labels={"Number of Flights": "Number of Flights", "Manufacturer": "Manufacturer"},
        color_discrete_sequence=[utils.COLOR_PALETTE["light_green"]]
    )
    
    return fig

def main():
    """Run manufacturers analysis (opens its own DB connection if none provided)."""
    fig = plot_manufacturer_data("LAX")
    # Display the interactive Plotly figure
    if isinstance(fig, str):
        print(fig)
    else:
        fig.show()

if __name__ == "__main__":
    main()
