"""
This module provides heatmap analysis functions for flight data.
It creates heatmaps for flight counts and average departure delays aggregated by day of week and hour of day,
using Plotly Express for interactive visualization.
"""

import pandas as pd
import plotly.express as px
from flights_project import utils

def get_flights_heatmap_data(start_date="2023-01-01", end_date="2023-12-31", conn=None):
    query = """
    SELECT year, month, day, hour 
    FROM flights 
    WHERE hour IS NOT NULL 
    AND date BETWEEN ? AND ?;
    """
    if conn is not None:
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    else:
        with utils.get_db_connection() as conn_local:
            df = pd.read_sql_query(query, conn_local, params=(start_date, end_date))
            
    # Create a date column and compute ISO week number and day name
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Group by day of week and hour, count flights
    grouped = df.groupby(['day_of_week', 'hour']).size().reset_index(name='flights_count')
    
    # Pivot so that rows are hours and columns are days (ordered Monday to Sunday)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_df = grouped.pivot(index='hour', columns='day_of_week', values='flights_count').reindex(columns=day_order)
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df.reindex(range(24), fill_value=0)
    return pivot_df

def plot_flights_heatmap(start_date="2023-01-01", end_date="2023-12-31", conn=None):

    data = get_flights_heatmap_data(start_date, end_date, conn)
    fig = px.imshow(
        data,
        labels={
            "x": "Day of week",
            "y": "Hour of day (24h)",
            "color": "Number of flights"
        },
        x=data.columns,
        y=data.index,
        aspect="auto",
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE  # Ensure CUSTOM_CMAP is a valid Plotly color scale (e.g., list of hex colors)
    )
    fig.update_layout(title=f"Frequency flights ({start_date} to {end_date})")
    return fig

def get_delays_heatmap_data(start_date="2023-01-01", end_date="2023-12-31", conn=None):
    query = """
    SELECT year, month, day, hour, dep_delay 
    FROM flights 
    WHERE hour IS NOT NULL 
    AND dep_delay IS NOT NULL 
    AND date BETWEEN ? AND ?;
    """
    if conn is not None:
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    else:
        with utils.get_db_connection() as conn_local:
            df = pd.read_sql_query(query, conn_local, params=(start_date, end_date))
    
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Group by day of week and hour, compute average delay
    grouped = df.groupby(['day_of_week', 'hour'])['dep_delay'].mean().reset_index(name='avg_delay')
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_df = grouped.pivot(index='hour', columns='day_of_week', values='avg_delay').reindex(columns=day_order)
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df.reindex(range(24), fill_value=0)
    return pivot_df

def plot_delays_heatmap(start_date="2023-01-01", end_date="2023-12-31", conn=None):

    data = get_delays_heatmap_data(start_date, end_date, conn)
    fig = px.imshow(
        data,
        labels={
            "x": "Day of week",
            "y": "Hour of day (24h)",
            "color": "Average delay (minutes)"
        },
        x=data.columns,
        y=data.index,
        aspect="auto",
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE  # Ensure CUSTOM_CMAP is compatible with Plotly Express
    )
    fig.update_layout(title=f"Average departure delays (minutes) ({start_date} to {end_date})")
    return fig

if __name__ == "__main__":
    # Get persistent connection to the flights database
    conn = utils.get_persistent_db_connection()

    # For testing purposes: show both heatmaps using all data.
    flights_fig = plot_flights_heatmap(conn=conn)
    delays_fig = plot_delays_heatmap(conn=conn)
    # To view the figures in a browser or interactive window:
    flights_fig.show()
    delays_fig.show()
