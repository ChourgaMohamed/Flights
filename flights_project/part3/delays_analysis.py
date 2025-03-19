"""
This module analyzes flight delays from the flights database.
Uses the shared DB helpers in utils.
"""

import plotly.express as px
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
    fig = px.histogram(
        x=delays,
        range_x=[-20, 300],
        title="Distribution of Flight Departure Delays",
        labels={'x': "Departure Delay (minutes)", 'y': "Number of Flights"},
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]]
    )
    return fig

def main():
    """Run delay analysis (opens its own DB connection if none provided)."""
    fig = plot_delay_histogram()
    fig.show()

if __name__ == "__main__":
    main()
