import plotly.express as px
import pandas as pd
from flights_project import utils

def load_clean_airports_data():
    """Load and clean airport data."""
    df = utils.load_airports_data()

    # Ensure time zone and altitude are properly formatted
    df["tzone"] = df["tzone"].astype(str).fillna("Unknown")
    df["alt"] = pd.to_numeric(df["alt"], errors="coerce").fillna(0)  # Convert altitude to numeric

    # Drop rows where lat/lon is missing
    df = df.dropna(subset=["lat", "lon"])
    
    # Drop rows where NA is present in tzone column
    df = df[df["tzone"] != "NA"]
    # Drop rows where nan is present in tzone column
    df = df[df["tzone"] != "nan"]

    return df


def plot_airports():
    """Plot a world map of all airports in the dataset, color-coded by altitude."""
    df = load_clean_airports_data()

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="name",
        title="Airports, in the Dataset (Color Coded by Altitude)",
        color=df["alt"],  # Color by altitude
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE
    )
    return fig


def plot_us_airports():
    """Plot only Northern American Airports."""
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
        title="Northern American Airports (Color Coded by Altitude)",
        color=us_airports["alt"],  # Color by altitude
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE
    )
    return fig


def plot_non_us_airports():
    """Plot only non-Northern American Airports."""
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
        (df["tzone"] != "Unknown") # Exclude any unknown values
    ]

    fig = px.scatter_geo(
        non_us_airports,
        lat="lat",
        lon="lon",
        hover_name="name",
        title="non-Northern American Airports (Color Coded by Altitude)",
        color=non_us_airports["alt"],  # Color by altitude
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE
    )
    return fig

if __name__ == "__main__":
    fig1 = plot_airports()
    fig2 = plot_us_airports()
    fig3 = plot_non_us_airports()

    fig1.show()
    fig2.show()
    fig3.show()