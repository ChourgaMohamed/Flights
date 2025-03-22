"""
Weather Analysis Module

This module provides weather-related flight analysis functions.
Includes functions for flight direction calculation, wind alignment analysis,
and inner product analysis between flight direction and wind speed.
"""
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from flights_project import utils

def calculate_flight_direction(dep_lat, dep_lon, arr_lat, arr_lon):
    """
    Calculate the flight direction (bearing) from departure to arrival.
    Returns bearing in degrees (0-360).
    """
    delta_lon = np.radians(arr_lon - dep_lon)
    dep_lat, arr_lat = np.radians(dep_lat), np.radians(arr_lat)
    x = np.sin(delta_lon) * np.cos(arr_lat)
    y = np.cos(dep_lat) * np.sin(arr_lat) - np.sin(dep_lat) * np.cos(arr_lat) * np.cos(delta_lon)
    bearing = np.degrees(np.arctan2(x, y))
    return (bearing + 360) % 360

def analyze_wind_direction(conn=None):
    """
    Analyze wind direction by computing the flight direction and its alignment with wind direction.
    Prints a sample of computed flight directions and wind alignments.
    """
    query = """
    SELECT f.origin, f.dest, a1.lat AS dep_lat, a1.lon AS dep_lon, 
           a2.lat AS arr_lat, a2.lon AS arr_lon, w.wind_dir
    FROM flights f
    JOIN airports a1 ON f.origin = a1.faa
    JOIN airports a2 ON f.dest = a2.faa
    LEFT JOIN weather w ON f.origin = w.origin AND f.year = w.year AND f.month = w.month AND f.day = w.day
    WHERE f.origin IN ('JFK', 'LGA', 'EWR')
    LIMIT 1000;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    
    # Compute flight direction
    df["flight_direction"] = df.apply(lambda row: calculate_flight_direction(
        row["dep_lat"], row["dep_lon"], row["arr_lat"], row["arr_lon"]), axis=1)
    
    # Compute wind alignment as absolute difference between flight direction and wind direction
    df["wind_alignment"] = abs(df["flight_direction"] - df["wind_dir"])
    
    return df

def analyze_inner_product_and_airtime(conn=None):
    """
    Analyze the inner product between flight direction and wind speed,
    and examine its relationship with air time.
    Computes the inner product, correlation with air time, and plots a violin plot.
    """
    query = """
    SELECT f.origin, f.dest, f.air_time, f.distance,
           w.wind_speed, w.wind_dir,
           (f.distance / f.air_time) AS flight_speed
    FROM flights f
    JOIN weather w ON f.origin = w.origin AND f.time_hour = w.time_hour
    WHERE f.air_time IS NOT NULL AND f.distance IS NOT NULL;
    """
    if conn is None:
        with utils.get_db_connection() as conn:
            df = pd.read_sql(query, conn)
    else:
        df = pd.read_sql(query, conn)
    
    # Compute inner product: flight_speed * wind_speed * cos(wind_dir in radians)
    df["inner_product"] = df["flight_speed"] * df["wind_speed"] * np.cos(np.radians(df["wind_dir"]))
    
    df = df.dropna(subset=["inner_product", "air_time"])
    
    
    # Relation between inner product and air_time
    df["inner_product_sign"] = np.sign(df["inner_product"])
    
    correlation = df[["inner_product", "air_time"]].corr()
    
    
    # For plotting, select flights with highest positive and lowest negative inner product values
    highest_positive = df.nlargest(100, "inner_product")
    lowest_negative = df.nsmallest(100, "inner_product")
    combined_df = pd.concat([lowest_negative, highest_positive])
    # Add a column for category
    combined_df["Category"] = np.where(combined_df["inner_product"] >= 0, "High Positive", "High Negative")
    
    return df

def prepare_data(df, include_neutral=False):
    """
    Prepare and transform the input dataframe for wind and flight time analysis.
    
    Args:
        df (pd.DataFrame): Input dataframe with inner_product, air_time, and distance columns
        include_neutral (bool): Whether to include neutral wind conditions in the output
        
    Returns:
        pd.DataFrame: Processed dataframe with additional columns
    """
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Create wind condition categories - FIXED the labels
    # A negative inner product means a tailwind (helps the plane move faster)
    # A positive inner product means a headwind (slows the plane down)
    processed_df["wind_condition"] = np.select(
        [
            processed_df["inner_product"] < -10,  # Strong tailwind
            processed_df["inner_product"] < 10,   # Neutral/mild wind
            processed_df["inner_product"] >= 10   # Strong headwind
        ],
        [
            "Tailwind",
            "Neutral", 
            "Headwind"
        ],
        default="Neutral"
    )
    
    # Create a binary wind condition (removing neutral)
    processed_df["wind_binary"] = processed_df["wind_condition"]
    
    # Normalize air time by distance (air time per 100 miles)
    processed_df["normalized_air_time"] = processed_df["air_time"] * 100 / processed_df["distance"]
    
    # Filter out neutral values if specified
    if not include_neutral:
        processed_df = processed_df[processed_df["wind_condition"] != "Neutral"]
    
    # Sample data (max 5000 points per category) to make plots cleaner
    sampled_df = pd.DataFrame()
    for condition in processed_df["wind_condition"].unique():
        condition_df = processed_df[processed_df["wind_condition"] == condition]
        if len(condition_df) > 1000:
            condition_df = condition_df.sample(1000, random_state=42)
        sampled_df = pd.concat([sampled_df, condition_df])
    
    return sampled_df

def create_improved_density_plot(df):
    """
    Create an improved density plot that filters outliers for cleaner visualization.
    
    Args:
        df (pd.DataFrame): Processed dataframe with wind_condition and normalized_air_time columns
        
    Returns:
        plotly.graph_objects.Figure: Density plot figure
    """
    # Create a temporary dataframe to filter outliers for each category
    temp_df = df.copy()
    
    # Filter out outliers for density plot
    for category in temp_df['wind_condition'].unique():
        category_data = temp_df[temp_df['wind_condition'] == category]['normalized_air_time']
        q1 = category_data.quantile(0.025)  # More permissive bounds
        q3 = category_data.quantile(0.975)

        # Create mask for this category
        mask = (temp_df['wind_condition'] == category) & \
               (temp_df['normalized_air_time'] >= q1) & \
               (temp_df['normalized_air_time'] <= q3)

        # Update filtered dataframe
        temp_df.loc[~mask & (temp_df['wind_condition'] == category), 'normalized_air_time'] = np.nan
    
    # Drop rows with NaN values
    temp_df = temp_df.dropna(subset=['normalized_air_time'])
    
    # Create separate dataframes for each wind condition
    headwind_data = temp_df[temp_df["wind_condition"] == "Headwind"]["normalized_air_time"]
    tailwind_data = temp_df[temp_df["wind_condition"] == "Tailwind"]["normalized_air_time"]
    
    # Calculate means
    headwind_mean = headwind_data.mean()
    tailwind_mean = tailwind_data.mean()
    
    # Create figure
    fig = go.Figure()
    
    # Create histograms with density curves using Plotly's native functions
    for condition, color in zip(["Headwind", "Tailwind"], ["red", "blue"]):
        condition_data = temp_df[temp_df["wind_condition"] == condition]["normalized_air_time"]
        
        # Add KDE curve using the figure_factory
        hist_data = [condition_data.values]
        group_labels = [condition]
        
        kde_fig = ff.create_distplot(
            hist_data, 
            group_labels, 
            bin_size=(condition_data.max() - condition_data.min()) / 40,
            show_hist=False,
            show_rug=False,
            colors=[color]
        )
        
        # Extract the KDE curve data and add it to our main figure
        kde_trace = kde_fig.data[0]
        fig.add_trace(
            go.Scatter(
                x=kde_trace.x,
                y=kde_trace.y,
                mode='lines',
                name=condition,
                line=dict(color=color, width=2),
                fill='tozeroy',
                fillcolor=f'rgba({255 if color == "red" else 0}, {0 if color == "red" else 0}, {255 if color == "blue" else 0}, 0.2)'
            )
        )
    
    # Add vertical lines for means
    y_max = max([max(trace.y) for trace in fig.data])
    
    fig.add_trace(
        go.Scatter(
            x=[headwind_mean, headwind_mean],
            y=[0, y_max * 1.1],
            mode='lines',
            line=dict(color="darkred", width=2, dash="dash"),
            name=f"Headwind Mean"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=[tailwind_mean, tailwind_mean],
            y=[0, y_max * 1.1],
            mode='lines',
            line=dict(color="darkblue", width=2, dash="dash"),
            name=f"Tailwind Mean"
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Distribution of Air Time by Wind Condition",
        xaxis_title="Normalized Air Time (minutes per 100 miles)",
        yaxis_title="Density",
        template="plotly_white",
        legend_title="Wind Condition",
        legend=dict(
            x=0.7,
            y=0.95,
            font=dict(family="Arial", size=12),
            itemsizing="constant"
        ),
        xaxis=dict(
            range=[
                min(headwind_data.min(), tailwind_data.min()),
                max(headwind_data.max(), tailwind_data.max())
            ]
        ),
        yaxis=dict(
            range=[0, y_max * 1.1]
        )
    )
    
    return fig

def create_box_plot(df):
    """
    Create a box plot of normalized air time by wind condition.
    
    Args:
        df (pd.DataFrame): Processed dataframe with wind_condition and normalized_air_time columns
        
    Returns:
        plotly.graph_objects.Figure: Box plot figure
    """
    # Filter outliers for cleaner visualization
    filtered_df = df.copy()
    
    for category in filtered_df['wind_condition'].unique():
        category_data = filtered_df[filtered_df['wind_condition'] == category]['normalized_air_time']
        q1 = category_data.quantile(0.01)
        q3 = category_data.quantile(0.99)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Create mask for outliers
        outlier_mask = (filtered_df['wind_condition'] == category) & \
                      ((filtered_df['normalized_air_time'] < lower_bound) | 
                       (filtered_df['normalized_air_time'] > upper_bound))
        
        # Remove outliers
        filtered_df = filtered_df[~outlier_mask]
    
    fig = px.box(filtered_df, x="wind_condition", y="normalized_air_time", 
                color="wind_condition", 
                title="Normalized Air Time by Wind Condition",
                labels={"wind_condition": "Wind Condition", "normalized_air_time": "Air Time (min per 100 miles)"},
                color_discrete_map={"Headwind": "red", "Tailwind": "blue"})
    
    # Add mean points
    for condition, color in zip(["Headwind", "Tailwind"], ["red", "blue"]):
        mean_val = filtered_df[filtered_df["wind_condition"] == condition]["normalized_air_time"].mean()
        fig.add_trace(
            go.Scatter(
                x=[condition],
                y=[mean_val],
                mode="markers",
                marker=dict(
                    symbol="diamond",
                    size=12,
                    color="white",
                    line=dict(color=color, width=2)
                ),
                name=f"{condition} Mean",
                showlegend=True
            )
        )
    
    # Simplify the box plot
    fig.update_traces(quartilemethod="exclusive", selector=dict(type="box"))
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(title_font=dict(size=14)),
        yaxis=dict(title_font=dict(size=14)),
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_scatter_plot(df, sample_size=800):
    """
    Create a scatter plot of inner product vs normalized air time.
    
    Args:
        df (pd.DataFrame): Processed dataframe with inner_product, wind_condition and normalized_air_time columns
        sample_size (int): Maximum number of points to sample for the plot
        
    Returns:
        plotly.graph_objects.Figure: Scatter plot figure
    """
    # Sample data to reduce visual noise
    sampled_df = pd.DataFrame()
    for condition in df["wind_condition"].unique():
        condition_df = df[df["wind_condition"] == condition]
        if len(condition_df) > sample_size // len(df["wind_condition"].unique()):
            condition_df = condition_df.sample(sample_size // len(df["wind_condition"].unique()), random_state=42)
        sampled_df = pd.concat([sampled_df, condition_df])
    
    # Filter outliers for cleaner visualization
    for condition in sampled_df["wind_condition"].unique():
        condition_data = sampled_df[sampled_df["wind_condition"] == condition]["normalized_air_time"]
        q1 = condition_data.quantile(0.01)
        q3 = condition_data.quantile(0.99)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Create mask for outliers
        outlier_mask = (sampled_df["wind_condition"] == condition) & \
                      ((sampled_df["normalized_air_time"] < lower_bound) | 
                       (sampled_df["normalized_air_time"] > upper_bound))
        
        # Remove outliers
        sampled_df = sampled_df[~outlier_mask]
        
    fig = px.scatter(sampled_df, x="inner_product", y="normalized_air_time", 
                    color="wind_condition",
                    opacity=0.7,
                    trendline="ols",
                    title="Inner Product vs Normalized Air Time",
                    labels={"inner_product": "Inner Product", "normalized_air_time": "Air Time (min per 100 miles)"},
                    color_discrete_map={"Headwind": "red", "Tailwind": "blue"})
    
    # Add mean points for each condition
    for condition, color in zip(["Headwind", "Tailwind"], ["red", "blue"]):
        condition_df = sampled_df[sampled_df["wind_condition"] == condition]
        mean_x = condition_df["inner_product"].mean()
        mean_y = condition_df["normalized_air_time"].mean()
        
        fig.add_trace(
            go.Scatter(
                x=[mean_x],
                y=[mean_y],
                mode="markers",
                marker=dict(
                    symbol="star",
                    size=15,
                    color=color,
                    line=dict(color="white", width=1)
                ),
                name=f"{condition} Mean",
                showlegend=True
            )
        )
    
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(title_font=dict(size=14)),
        yaxis=dict(title_font=dict(size=14)),
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def calculate_statistics(df):
    """
    Calculate statistics for normalized air time by wind condition.
    
    Args:
        df (pd.DataFrame): Processed dataframe with wind_condition and normalized_air_time columns
        
    Returns:
        tuple: (stats_df, correlation, headwind_mean, tailwind_mean, percent_diff)
    """
    # Create statistics dataframe
    stats_df = df.groupby("wind_condition")["normalized_air_time"].agg(
        ["count", "mean", "median", "std"]
    ).reset_index()
    stats_df.columns = ["Wind Condition", "Count", "Mean Air Time", "Median Air Time", "Std Dev"]
    
    # Round for cleaner display
    for col in ["Mean Air Time", "Median Air Time", "Std Dev"]:
        stats_df[col] = stats_df[col].round(2)
    
    # Calculate correlation
    correlation = df[["inner_product", "normalized_air_time"]].corr().iloc[0, 1]
    
    # Calculate difference between headwind and tailwind means
    headwind_mean = df[df["wind_condition"] == "Headwind"]["normalized_air_time"].mean()
    tailwind_mean = df[df["wind_condition"] == "Tailwind"]["normalized_air_time"].mean()
    percent_diff = abs(headwind_mean - tailwind_mean) / ((headwind_mean + tailwind_mean) / 2) * 100
    
    return stats_df, correlation, headwind_mean, tailwind_mean, percent_diff

def get_conclusion_text(correlation, headwind_mean, tailwind_mean, percent_diff):
    """
    Generate conclusion text based on statistical analysis.
    
    Args:
        correlation (float): Correlation between inner product and normalized air time
        headwind_mean (float): Mean normalized air time for headwind condition
        tailwind_mean (float): Mean normalized air time for tailwind condition
        percent_diff (float): Percentage difference between headwind and tailwind means
        
    Returns:
        str: Conclusion text
    """
    correlation_text = f"Correlation between inner product and normalized air time: {correlation:.4f}"
    
    if percent_diff > 5:
        conclusion = f"""
        Yes, there is a relationship between the sign of the inner product and air time.
        
        The analysis shows that flights facing headwinds (negative inner product) have a mean normalized air time 
        of {headwind_mean:.2f} minutes per 100 miles, while flights with tailwinds (positive inner product) 
        average {tailwind_mean:.2f} minutes per 100 miles. This {percent_diff:.1f}% difference indicates that 
        wind conditions meaningfully impact flight duration, as expected from aerodynamic principles.
        """
    else:
        conclusion = f"""
        The analysis shows a subtle relationship between wind conditions and air time. While there is 
        a {percent_diff:.1f}% difference between headwind and tailwind mean air times ({headwind_mean:.2f} vs {tailwind_mean:.2f} 
        minutes per 100 miles), this effect may be partially mitigated by airline scheduling adjustments 
        or other operational factors that account for expected wind conditions.
        """
    
    return correlation_text, conclusion
def main():
    # Opening a persistent connection
    conn = utils.get_persistent_db_connection()

    """Run weather-related flight analyses."""
    print("Analyzing Wind Direction and Alignment...")
    analyze_wind_direction(conn)
    
    print("\nAnalyzing Inner Product and Air Time...")
    analyze_inner_product_and_airtime(conn)

if __name__ == "__main__":
    main()
