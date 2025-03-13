"""
This module creates global and US flight maps using Plotly.
It uses the CSV loading function from utils.
"""

import plotly.express as px
from flights_project import utils

def plot_global_airports():
    """Plot global airports on a scatter geo map."""
    df = utils.load_airports_data()
    fig = px.scatter_geo(
        df, lat="lat", lon="lon",
        hover_name="name",
        title="Global Airports",
        size_max=5,
        opacity=0.6
    )
    return fig

def plot_us_airports():
    """Plot US airports on a scatter geo map."""
    df = utils.load_airports_data()
    us_airports = df[df["tz"].str.contains("America")]
    fig = px.scatter_geo(
        us_airports, lat="lat", lon="lon",
        hover_name="name",
        title="US Airports",
        size_max=5,
        opacity=0.6
    )
    
    return fig

def main():
    """Test the global and US maps functions."""
    fig1 = plot_global_airports()
    fig1.show()
    fig2 = plot_us_airports()
    fig2.show()

if __name__ == "__main__":
    main()