import plotly.express as px
import pandas as pd
from flights_project import utils


def plot_flight_route(faa_code):
    """
    Plot a flight route from NYC airport JFK to the target airport.

    Args:
        faa_code (str): The FAA code of the target airport.
    """
    df = utils.load_airports_data()
    # Get JFK's data as a DataFrame row
    nyc_airport = df[df["faa"] == "JFK"]
    target_airport = df[df["faa"] == faa_code]

    if target_airport.empty:
        print(f"Airport with FAA code {faa_code} not found!")
        return

    # Concatenate JFK and target airport for plotting
    plot_data = pd.concat([nyc_airport, target_airport])
    fig = px.scatter_geo(
        plot_data, lat="lat", lon="lon",
        text="name",
        hover_name="name",
        title=f"Route from NYC to {faa_code}",
        size_max=5,
        opacity=0.6
    )
    # Draw a line from JFK to the target airport
    fig.add_trace(px.line_geo(plot_data, lat="lat", lon="lon").data[0])
    return fig


def plot_multiple_routes(faa_codes):
    """
    Plot multiple flight routes from NYC airports (JFK, LGA, EWR) to a list of target airports.

    Args:
        faa_codes (list): List of FAA codes for target airports.
    """
    df = utils.load_airports_data()
    nyc_airports = df[df["faa"].isin(["JFK", "LGA", "EWR"])]
    target_airports = df[df["faa"].isin(faa_codes)]

    if target_airports.empty:
        print("No valid airports found!")
        return

    # Combine all airport points for the scatter geo plot
    plot_data = pd.concat([nyc_airports, target_airports])
    fig = px.scatter_geo(
        plot_data, lat="lat", lon="lon",
        text="name",
        hover_name="name",
        title="Routes from NYC to Selected Airports",
        size_max=5,
        opacity=0.6
    )

    # Draw a line from each NYC airport to each target airport
    for faa in faa_codes:
        target_airport = df[df["faa"] == faa]
        if not target_airport.empty:
            for _, nyc_row in nyc_airports.iterrows():
                # Create a small DataFrame with two rows: one for the NYC airport and one for the target airport.
                line_data = pd.DataFrame([nyc_row, target_airport.iloc[0]])
                fig.add_trace(px.line_geo(line_data, lat="lat", lon="lon").data[0])
    return fig


def main():
    """Test flight route functions."""
    fig1 = plot_flight_route("LAX")
    if fig1:
        fig1.show()
    fig2 = plot_multiple_routes(["LAX", "ORD", "MIA"])
    if fig2:
        fig2.show()


if __name__ == "__main__":
    main()
