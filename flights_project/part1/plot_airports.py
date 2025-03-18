import plotly.express as px
import pandas as pd
import numpy as np
from flights_project import utils


# Define the color scale based on the provided color palette
CUSTOM_COLOR_SCALE = [
    "#134611",  # Pakistan green
    "#3E8914",  # India green
    "#3DA35D",  # Pigment green
    "#96E072",  # Light green
    "#E8FCCF"   # Nyanza
]

def load_clean_airports_data():
    """Load and clean airport data."""
    df = utils.load_airports_data()

    # Ensure time zone and altitude are properly formatted
    df["tzone"] = df["tzone"].astype(str).fillna("Unknown")
    df["alt"] = pd.to_numeric(df["alt"], errors="coerce").fillna(0)  # Convert altitude to numeric

    # Drop rows where lat/lon is missing
    df = df.dropna(subset=["lat", "lon"])

    return df


def plot_airports():
    """Plot a world map of all airports, color-coded by altitude."""
    df = load_clean_airports_data()

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="name",
        title="Airports Worldwide (Color Coded by Altitude)",
        color=df["alt"],  # Color by altitude
        color_continuous_scale=CUSTOM_COLOR_SCALE
    )
    return fig


def plot_us_airports():
    """Plot only US airports."""
    df = load_clean_airports_data()

    # Known US time zones
    us_timezones = [
        "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
        "America/Anchorage", "America/Phoenix", "America/Adak"
    ]

    # Filter only US airports
    us_airports = df[df["tzone"].isin(us_timezones)]

    fig = px.scatter_geo(
        us_airports,
        lat="lat",
        lon="lon",
        hover_name="name",
        title="US Airports (Color Coded by Altitude)",
        color=us_airports["alt"],  # Color by altitude
        color_continuous_scale=CUSTOM_COLOR_SCALE
    )
    return fig


def plot_non_us_airports():
    """Plot only non-US airports."""
    df = load_clean_airports_data()

    # List of known US time zones
    us_timezones = [
        "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
        "America/Anchorage", "America/Phoenix", "America/Adak"
    ]

    # Ensure proper filtering of non-US airports
    non_us_airports = df[
        (~df["tzone"].isin(us_timezones)) &  # Exclude known US time zones
        (~df["tzone"].str.contains("America", na=False)) &  # Exclude any timezone containing 'America'
        (df["tzone"].notna()) &  # Ensure non-null values
        (df["tzone"] != "NA") &  # Explicitly exclude 'NA' values
        (df["tzone"] != "Unknown")  # Exclude any unknown values
    ]

    fig = px.scatter_geo(
        non_us_airports,
        lat="lat",
        lon="lon",
        hover_name="name",
        title="Non-US Airports (Color Coded by Altitude)",
        color=non_us_airports["alt"],  # Color by altitude
        color_continuous_scale=CUSTOM_COLOR_SCALE
    )
    return fig


if __name__ == "__main__":
    fig1 = plot_airports()
    fig2 = plot_us_airports()
    fig3 = plot_non_us_airports()

    fig1.show()
    fig2.show()
    fig3.show()