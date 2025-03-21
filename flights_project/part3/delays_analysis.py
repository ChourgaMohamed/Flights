"""
This module analyzes flight delays from the flights database.
Uses the shared DB helpers in utils.
"""

import plotly.express as px
from flights_project import utils

def get_delay_data(start_date="2023-01-01", end_date="2023-12-31", conn=None):
    """
    Query the flights database to retrieve departure delay data within a date range.
    
    Args:
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.
        conn (sqlite3.Connection, optional): Existing DB connection.
    """
    query = """
    SELECT dep_delay 
    FROM flights 
    WHERE dep_delay IS NOT NULL 
    AND date BETWEEN ? AND ?;
    """
    data = utils.execute_query(query, fetch='all', conn=conn, params=(start_date, end_date))
    return [row[0] for row in data]


def plot_delay_histogram(start_date="2023-01-01", end_date="2023-12-31", conn=None):
    if conn is None:
        conn = utils.get_db_connection()
    delays = get_delay_data(start_date, end_date, conn)
    fig = px.histogram(
        x=delays,
        range_x=[-20, 150],
        title=f"Distribution of flight departure delays ({start_date} to {end_date})",
        labels={'x': "Departure delay (minutes)", 'y': "Number of flights"},
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]]
    )
    return fig

def main():
    # Opening a persistent connection
    conn = utils.get_persistent_db_connection()

    """Run delay analysis (opens its own DB connection if none provided)."""
    fig = plot_delay_histogram(conn=conn)
    fig.show()

if __name__ == "__main__":
    main()
