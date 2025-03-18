# plot_airports.py
import plotly.express as px
from flights_project import utils

def plot_airports():
    """Plot a world map of all airports."""
    df = utils.load_airports_data()
    fig = px.scatter_geo(df, lat="lat", lon="lon", hover_name="name", title="Airports Worldwide")
    return fig

def plot_us_airports():
    """Plot only US airports."""
    df = utils.load_airports_data()
    df["tz"] = df["tz"].astype(str).fillna("")
    us_airports = df[df["tz"].str.contains("America", na=False)]
    fig = px.scatter_geo(us_airports, lat="lat", lon="lon", hover_name="name", title="US Airports")
    return fig

def plot_non_us_airports():
    """Plot only non-US airports."""
    df = utils.load_airports_data()
    df["tz"] = df["tz"].astype(str).fillna("")
    non_us_airports = df[~df["tz"].str.contains("America", na=False)]
    fig = px.scatter_geo(non_us_airports, lat="lat", lon="lon", hover_name="name", title="Non-US Airports")
    return fig

if __name__ == "__main__":
    fig1 = plot_airports()
    fig2 = plot_us_airports()
    fig3 = plot_non_us_airports()

    fig1.show()
    fig2.show()
    fig3.show()