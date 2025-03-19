"""
Plane Type Analyses Module

This module investigates correlations between:
    - Plane manufacturing year and flight duration (air_time)
    - Plane manufacturing year and flight distance
    - Number of engines and flight distance
    - Number of seats and flight distance

It produces three visualizations:
    1. A correlation heatmap.
    2. Four scatter plots for various relationships.
    3. A scatter plot of maximum flight distance vs. maximum air time for each plane model.

All outputs (plots and prints) are routed through main.
"""

import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
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
        
    Returns the correlation heatmap as a Plotly figure.
    """
    cols = ['year', 'air_time', 'distance', 'engines', 'seats']
    corr_matrix = df[cols].corr()
    print("Correlation Matrix:")
    print(corr_matrix)
    
    # Create a custom colorscale using the palette:
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE,
        title="Correlation Matrix for Plane and Flight Variables"
    )
    return fig

def plot_scatter_plots(df):
    """
    Create scatter plots for:
        - Plane year vs. Flight Duration (air_time)
        - Plane year vs. Flight Distance
        - Number of Engines vs. Flight Distance
        - Number of Seats vs. Flight Distance
        
    Returns a Plotly figure containing the 2x2 subplots.
    """
    # Create a subplot figure with 2 rows and 2 columns
    subplot_titles = [
        "Year vs Flight Duration",
        "Year vs Flight Distance",
        "Engines vs Flight Distance",
        "Seats vs Flight Distance"
    ]
    fig = make_subplots(rows=2, cols=2, subplot_titles=subplot_titles)
    
    # Scatter 1: Year vs Flight Duration
    scatter1 = px.scatter(
        df,
        x="year",
        y="air_time",
        opacity=0.5,
        color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]],
        labels={"year": "Plane Manufacturing Year", "air_time": "Flight Duration (min)"}
    )
    for trace in scatter1.data:
        fig.add_trace(trace, row=1, col=1)
    
    # Scatter 2: Year vs Flight Distance
    scatter2 = px.scatter(
        df,
        x="year",
        y="distance",
        opacity=0.5,
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]],
        labels={"year": "Plane Manufacturing Year", "distance": "Flight Distance"}
    )
    for trace in scatter2.data:
        fig.add_trace(trace, row=1, col=2)
    
    # Scatter 3: Engines vs Flight Distance
    scatter3 = px.scatter(
        df,
        x="engines",
        y="distance",
        opacity=0.5,
        color_discrete_sequence=[utils.COLOR_PALETTE["pigment_green"]],
        labels={"engines": "Number of Engines", "distance": "Flight Distance"}
    )
    for trace in scatter3.data:
        fig.add_trace(trace, row=2, col=1)
    
    # Scatter 4: Seats vs Flight Distance
    scatter4 = px.scatter(
        df,
        x="seats",
        y="distance",
        opacity=0.5,
        color_discrete_sequence=[utils.COLOR_PALETTE["light_green"]],
        labels={"seats": "Number of Seats", "distance": "Flight Distance"}
    )
    for trace in scatter4.data:
        fig.add_trace(trace, row=2, col=2)
    
    # Update axes titles for clarity
    fig.update_xaxes(title_text="Plane Manufacturing Year", row=1, col=1)
    fig.update_yaxes(title_text="Flight Duration (min)", row=1, col=1)
    
    fig.update_xaxes(title_text="Plane Manufacturing Year", row=1, col=2)
    fig.update_yaxes(title_text="Flight Distance", row=1, col=2)
    
    fig.update_xaxes(title_text="Number of Engines", row=2, col=1)
    fig.update_yaxes(title_text="Flight Distance", row=2, col=1)
    
    fig.update_xaxes(title_text="Number of Seats", row=2, col=2)
    fig.update_yaxes(title_text="Flight Distance", row=2, col=2)
    
    fig.update_layout(height=800, showlegend=False, title_text="Scatter Plots for Plane and Flight Relationships")
    return fig

def plot_model_distance_year(df):
    """
    Create a scatter plot based on maximum flight distance and maximum air time
    for each plane model. Each dot represents a plane model and is annotated with its model name.
    
    Returns the Plotly figure.
    """
    # Aggregate by model: maximum flight distance and maximum air time per model
    df_grouped = df.groupby('model').agg({
        'distance': 'max',
        'air_time': 'max'
    }).reset_index()
    
    fig = px.scatter(
        df_grouped,
        x="distance",
        y="air_time",
        text="model",
        opacity=0.7,
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]],
        labels={"distance": "Maximum Flight Distance", "air_time": "Maximum Air Time"}
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        title="Plane Models: Maximum Distance vs. Maximum Air Time",
        xaxis_title="Maximum Flight Distance",
        yaxis_title="Maximum Air Time"
    )
    return fig

def plot_violin_distance_by_engine(conn=None):
    """
    Create a violin plot of flight distance by engine type for 'Turbo-fan' and 'Turbo-jet'
    using Plotly Express.
    
    This function joins the flights and planes tables to retrieve flight distance and engine type,
    filters the data to only include 'Turbo-fan' and 'Turbo-jet', and then creates a violin plot.
    A low bandwidth (5) is used (set on the underlying traces) to enforce strict smoothing.
    
    Returns the Plotly figure.
    """
    query = """
    SELECT p.engine, f.distance
    FROM flights f
    JOIN planes p ON f.tailnum = p.tailnum
    WHERE f.distance IS NOT NULL 
      AND p.engine IN ('Turbo-fan', 'Turbo-jet')
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    
    # Create the violin plot without the 'color' argument.
    fig = px.violin(
        df,
        x="engine",
        y="distance",
        box=True,
        # points="all",
        title="Flight Distance by Engine Type",
        category_orders={"engine": ["Turbo-fan", "Turbo-jet"]},
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]]
    )
    
    fig.update_layout(xaxis_title="Engine Type", yaxis_title="Flight Distance")
    return fig



def main():
    # Retrieve the data and print the first few rows
    df = get_plane_flight_data()
    print("First few rows of combined flight and plane data:")
    print(df.head())
    
    # Generate figures from the various functions
    fig_corr = analyze_correlations(df)
    fig_scatter = plot_scatter_plots(df)
    fig_model = plot_model_distance_year(df)
    fig_violin = plot_violin_distance_by_engine()
    
    # Display the figures
    fig_corr.show()
    fig_scatter.show()
    fig_model.show()
    fig_violin.show()

if __name__ == "__main__":
    main()
