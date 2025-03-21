"""
This module provides analysis on airplane manufacturers based on flight data.
Uses a provided DB connection via utils.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    """Plot the manufacturer data as a bar chart using Plotly Express with outlined bars."""
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

    # Create figure using Graph Objects to add black outlines
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["Manufacturer"],
        y=df["Number of Flights"],
        marker=dict(color=utils.COLOR_PALETTE["light_green"], line=dict(color="black", width=1.5)),  # Add black outline
    ))

    # Update layout
    fig.update_layout(
        title=f"Top Airplane Manufacturers for Flights to {destination}",
        xaxis_title="Manufacturer",
        yaxis_title="Number of Flights",
    )

    return fig

def main():
    """Run manufacturers analysis (opens its own DB connection if none provided)."""
    fig = plot_manufacturer_data("LAX")
    if isinstance(fig, str):
        print(fig)
    else:
        fig.show()

if __name__ == "__main__":
    main()