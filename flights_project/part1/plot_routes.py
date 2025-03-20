import plotly.express as px
import pandas as pd
from flights_project import utils


def plot_flight_route(dept_airport, arr_airport):
    """
    Plot a flight route from NYC airport to the target airport.

    Args:
        dept_airport (str): FAA code of the departure airport.
        arr_airport (str): FAA code of the arrival airport.
    """
    df = utils.load_airports_data()
    # Get departure airport's data as a DataFrame row
    dept_airport_data = df[df["faa"] == dept_airport]
    target_airport = df[df["faa"] == arr_airport]

    if target_airport.empty:
        print(f"Airport with FAA code {arr_airport} not found!")
        return

    # Concatenate departure and target airport for plotting
    plot_data = pd.concat([dept_airport_data, target_airport])
    fig = px.scatter_geo(
        plot_data, lat="lat", lon="lon",
        text="name",
        hover_name="name",
        title=f"Route from {dept_airport} to {arr_airport}",
        size_max=5,
        opacity=0.6,
        color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]]
    )
    # Draw a line from departure to the target airport with the darkest color in the palette
    fig.add_trace(px.line_geo(plot_data, lat="lat", lon="lon", line_dash_sequence=['solid'], color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]]).data[0])
    
    # Autozoom to the selected route with a bit less zoom
    fig.update_geos(fitbounds="locations", visible=False)
    
    # Remove the box around the plot and use custom color palette
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            showland=True,
            showcountries=True,
            showlakes=True,
            lakecolor=utils.COLOR_PALETTE["light_green"],
            landcolor=utils.COLOR_PALETTE["nyanza"],
            projection_scale=1.2  # Adjust this value to control zoom
        ),
    )
    
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
