"""
This module provides heatmap analysis functions for flight data.
It creates heatmaps for flight counts and average departure delays aggregated by day of week and hour of day.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
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
    Plot a heatmap of flight counts aggregated by day of week and hour of day.

    Args:
        week_range (tuple, optional): (start_week, end_week) to filter data.
                                      If None, all data is used.
        conn (sqlite3.Connection, optional): DB connection.

    Returns:
        fig (Figure): Matplotlib figure object containing the heatmap.
    """
    data = get_flights_heatmap_data(week_range, conn)
    fig, ax = plt.subplots(figsize=(10, 8))
    # Use the custom colormap from utils for consistent color mapping
    cax = ax.imshow(data, aspect='auto', origin='lower', cmap=utils.CUSTOM_CMAP)
    ax.set_title("Heatmap of Flight Counts")
    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(24))
    ax.set_yticklabels(range(24))
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Hour of Day (24h)")
    fig.colorbar(cax, ax=ax, label="Number of Flights")
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
    Plot a heatmap of average departure delays aggregated by day of week and hour of day.

    Args:
        week_range (tuple, optional): (start_week, end_week) to filter data.
                                      If None, all data is used.
        conn (sqlite3.Connection, optional): DB connection.

    Returns:
        fig (Figure): Matplotlib figure object containing the heatmap.
    """
    data = get_delays_heatmap_data(week_range, conn)
    fig, ax = plt.subplots(figsize=(10, 8))
    # Use the custom colormap from utils for consistent color mapping
    cax = ax.imshow(data, aspect='auto', origin='lower', cmap=utils.CUSTOM_CMAP)
    ax.set_title("Heatmap of Average Departure Delays (minutes)")
    ax.set_xticks(range(len(data.columns)))
    ax.set_xticklabels(data.columns)
    ax.set_yticks(range(24))
    ax.set_yticklabels(range(24))
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Hour of Day (24h)")
    fig.colorbar(cax, ax=ax, label="Average Delay (minutes)")
    return fig

if __name__ == "__main__":
    # For testing purposes: show both heatmaps using all data.
    fig1 = plot_flights_heatmap()
    fig2 = plot_delays_heatmap()
    plt.show()
