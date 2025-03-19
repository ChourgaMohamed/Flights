"""
This module provides heatmap analysis functions for flight data.
It creates heatmaps for flight counts and average departure delays aggregated by day of week and hour of day,
using Plotly Express for interactive visualization.
"""

import pandas as pd
import plotly.express as px
from flights_project import utils

def get_flights_heatmap_data(week_range=None, conn=None):
    """
    Retrieve and aggregate flight count data for heatmap analysis.

    Args:
        week_range (tuple, optional): (start_week, end_week) to filter data by ISO week.
                                      If None, all data is used.
        conn (sqlite3.Connection, optional): Existing DB connection.

    Returns:
        pivot_df (DataFrame): Pivoted dataframe with index as hours (0-23) and columns as days (Monday to Sunday),
                               values as flight counts.
    """
    query = "SELECT year, month, day, hour FROM flights WHERE hour IS NOT NULL;"
    if conn is not None:
        df = pd.read_sql_query(query, conn)
    else:
        with utils.get_db_connection() as conn_local:
            df = pd.read_sql_query(query, conn_local)
            
    # Create a date column and compute ISO week number and day name
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Filter by week range if provided
    if week_range is not None:
        start_week, end_week = week_range
        df = df[(df['week'] >= start_week) & (df['week'] <= end_week)]
    
    # Group by day of week and hour, count flights
    grouped = df.groupby(['day_of_week', 'hour']).size().reset_index(name='flights_count')
    
    # Pivot so that rows are hours and columns are days (ordered Monday to Sunday)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_df = grouped.pivot(index='hour', columns='day_of_week', values='flights_count').reindex(columns=day_order)
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df.reindex(range(24), fill_value=0)
    return pivot_df

def plot_flights_heatmap(week_range=None, conn=None):
    """
    Plot a heatmap of flight counts aggregated by day of week and hour of day using Plotly Express.

    Args:
        week_range (tuple, optional): (start_week, end_week) to filter data.
                                      If None, all data is used.
        conn (sqlite3.Connection, optional): DB connection.

    Returns:
        fig (Figure): Plotly figure object containing the interactive heatmap.
    """
    data = get_flights_heatmap_data(week_range, conn)
    fig = px.imshow(
        data,
        labels={
            "x": "Day of Week",
            "y": "Hour of Day (24h)",
            "color": "Number of Flights"
        },
        x=data.columns,
        y=data.index,
        aspect="auto",
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE  # Ensure CUSTOM_CMAP is a valid Plotly color scale (e.g., list of hex colors)
    )
    fig.update_layout(title="Heatmap of Flight Counts")
    return fig

def get_delays_heatmap_data(week_range=None, conn=None):
    """
    Retrieve and aggregate average departure delay data for heatmap analysis.

    Args:
        week_range (tuple, optional): (start_week, end_week) to filter data.
                                      If None, all data is used.
        conn (sqlite3.Connection, optional): Existing DB connection.

    Returns:
        pivot_df (DataFrame): Pivoted dataframe with index as hours (0-23) and columns as days (Monday to Sunday),
                               values as average departure delay.
    """
    query = "SELECT year, month, day, hour, dep_delay FROM flights WHERE hour IS NOT NULL AND dep_delay IS NOT NULL;"
    if conn is not None:
        df = pd.read_sql_query(query, conn)
    else:
        with utils.get_db_connection() as conn_local:
            df = pd.read_sql_query(query, conn_local)
    
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.day_name()
    
    if week_range is not None:
        start_week, end_week = week_range
        df = df[(df['week'] >= start_week) & (df['week'] <= end_week)]
    
    # Group by day of week and hour, compute average delay
    grouped = df.groupby(['day_of_week', 'hour'])['dep_delay'].mean().reset_index(name='avg_delay')
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_df = grouped.pivot(index='hour', columns='day_of_week', values='avg_delay').reindex(columns=day_order)
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df.reindex(range(24), fill_value=0)
    return pivot_df

def plot_delays_heatmap(week_range=None, conn=None):
    """
    Plot a heatmap of average departure delays aggregated by day of week and hour of day using Plotly Express.

    Args:
        week_range (tuple, optional): (start_week, end_week) to filter data.
                                      If None, all data is used.
        conn (sqlite3.Connection, optional): DB connection.

    Returns:
        fig (Figure): Plotly figure object containing the interactive heatmap.
    """
    data = get_delays_heatmap_data(week_range, conn)
    fig = px.imshow(
        data,
        labels={
            "x": "Day of Week",
            "y": "Hour of Day (24h)",
            "color": "Average Delay (minutes)"
        },
        x=data.columns,
        y=data.index,
        aspect="auto",
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE  # Ensure CUSTOM_CMAP is compatible with Plotly Express
    )
    fig.update_layout(title="Heatmap of Average Departure Delays (minutes)")
    return fig

if __name__ == "__main__":
    # For testing purposes: show both heatmaps using all data.
    flights_fig = plot_flights_heatmap()
    delays_fig = plot_delays_heatmap()
    # To view the figures in a browser or interactive window:
    flights_fig.show()
    delays_fig.show()
