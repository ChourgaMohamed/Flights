# plot_airports.py
import plotly.express as px
from flights_project import utils

def plot_airports():
    """Plot a world map of all airports."""
    df = utils.load_airports_data()
    fig = px.scatter_geo(df, lat="lat", lon="lon", hover_name="name", title="Airports Worldwide")
    fig.show()

def plot_us_airports():
    """Plot only US airports."""
    df = utils.load_airports_data()
    df["tz"] = df["tz"].astype(str).fillna("")  # Ensure tz is treated as a string
    us_airports = df[df["tz"].str.contains("America", na=False)]  # Use na=False to prevent issues
    fig = px.scatter_geo(us_airports, lat="lat", lon="lon", hover_name="name", title="US Airports")
    fig.show()

def plot_non_us_airports():
    """Plot only non-US airports."""
    df = utils.load_airports_data()
    df["tz"] = df["tz"].astype(str).fillna("")  # Ensure tz is treated as a string
    non_us_airports = df[~df["tz"].str.contains("America", na=False)]  # Fix filtering condition
    fig = px.scatter_geo(non_us_airports, lat="lat", lon="lon", hover_name="name", title="Non-US Airports")
    fig.show()

if __name__ == "__main__":
    plot_airports()
    plot_us_airports()
    plot_non_us_airports()