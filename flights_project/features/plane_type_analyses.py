"""
Plane Type Analyses Module

This module investigates correlations between:
    - Plane manufacturing year and flight duration (air_time)
    - Plane manufacturing year and flight distance
    - Number of engines and flight distance
    - Number of seats and flight distance

It produces two visualizations:
    1. Scatter plots for various relationships (unchanged).
    2. A scatter plot of average flight distance vs. plane manufacturing year,
       where each dot represents a plane model.
       
All outputs (plots and prints) are routed through main.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flights_project import utils

def get_plane_flight_data(conn=None):
    """
    Retrieve flight and plane data by joining the flights and planes tables.
    Returns a DataFrame with columns:
        - air_time (flight duration in minutes)
        - distance (flight distance)
        - year (plane manufacturing year)
        - engines (number of engines)
        - seats (number of seats)
        - model (plane model)
    """
    query = """
    SELECT f.air_time, f.distance, p.year, p.engines, p.seats, p.model
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.air_time IS NOT NULL 
      AND f.distance IS NOT NULL 
      AND p.year IS NOT NULL 
      AND p.engines IS NOT NULL 
      AND p.seats IS NOT NULL;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    return df

def analyze_correlations(df):
    """
    Compute and display the correlations between:
        - Plane year and flight duration (air_time)
        - Plane year and flight distance
        - Engines and flight distance
        - Seats and flight distance
        
    Returns the correlation heatmap as a figure.
    """
    cols = ['year', 'air_time', 'distance', 'engines', 'seats']
    corr_matrix = df[cols].corr()
    print("Correlation Matrix:")
    print(corr_matrix)
    
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix for Plane and Flight Variables")
    return fig

def plot_scatter_plots(df):
    """
    Create scatter plots for:
        - Plane year vs. Flight Duration (air_time)
        - Plane year vs. Flight Distance
        - Number of Engines vs. Flight Distance
        - Number of Seats vs. Flight Distance
        
    Returns the figure containing the subplots.
    """
    fig = plt.figure(figsize=(14, 10))
    
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.scatter(df['year'], df['air_time'], alpha=0.5)
    ax1.set_xlabel("Plane Manufacturing Year")
    ax1.set_ylabel("Flight Duration (air_time)")
    ax1.set_title("Year vs Flight Duration")
    
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.scatter(df['year'], df['distance'], alpha=0.5, color="green")
    ax2.set_xlabel("Plane Manufacturing Year")
    ax2.set_ylabel("Flight Distance")
    ax2.set_title("Year vs Flight Distance")
    
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.scatter(df['engines'], df['distance'], alpha=0.5, color="orange")
    ax3.set_xlabel("Number of Engines")
    ax3.set_ylabel("Flight Distance")
    ax3.set_title("Engines vs Flight Distance")
    
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.scatter(df['seats'], df['distance'], alpha=0.5, color="purple")
    ax4.set_xlabel("Number of Seats")
    ax4.set_ylabel("Flight Distance")
    ax4.set_title("Seats vs Flight Distance")
    
    fig.tight_layout()
    return fig

def plot_model_distance_year(df):
    """
    Create a scatter plot based on maximum flight distance and maximum air time
    for each plane model. Each dot represents a plane model and is annotated with its model name.
    
    Returns the figure.
    """
    # Aggregate by model: average flight distance and first year (assuming year is constant per model)
    df_grouped = df.groupby('model').agg({
        'distance': 'max',
        'air_time': 'max'
    }).reset_index()
    
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.scatter(df_grouped['distance'], df_grouped['air_time'], alpha=0.7)
    ax.set_xlabel("Maximum Flight Distance")
    ax.set_ylabel("Maximum Air Time")
    ax.set_title("Plane Models: Maximum Distance vs. Maximum Air Time")
    
    # Annotate each point with the plane model
    for _, row in df_grouped.iterrows():
        ax.text(row['distance'], row['air_time'], row['model'], fontsize=9, ha='right', va='bottom')
    
    return fig

def main():
    # Retrieve the data and print the first few rows
    df = get_plane_flight_data()
    print("First few rows of combined flight and plane data:")
    print(df.head())
    
    # Get figures from the various functions
    fig_corr = analyze_correlations(df)
    fig_scatter = plot_scatter_plots(df)
    fig_model = plot_model_distance_year(df)
    
    # Display the figures
    # Depending on your environment, you may call plt.show() once to display all figures.
    plt.show()

if __name__ == "__main__":
    main()
