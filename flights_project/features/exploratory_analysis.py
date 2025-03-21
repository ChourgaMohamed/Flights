import plotly.express as px
from plotly.subplots import make_subplots
from geopy.distance import geodesic
from flights_project import utils

def exploratory_analysis():
    """Perform additional analysis on airport data to uncover trends."""
    df = utils.load_airports_data()

    # Get JFK coordinates
    jfk = df[df["faa"] == "JFK"].iloc[0]
    jfk_lat, jfk_lon = jfk["lat"], jfk["lon"]

    # Compute Geodesic distance if missing
    if "geodesic_dist" not in df.columns:
        df["geodesic_dist"] = df.apply(
            lambda row: geodesic((jfk_lat, jfk_lon), (row["lat"], row["lon"])).km, axis=1
        )

    light_green = utils.COLOR_PALETTE["light_green"]

    # Create scatter plot: Altitude vs. Distance from JFK using Plotly Express
    scatter_fig = px.scatter(
        df,
        x="geodesic_dist",
        y="alt",
        opacity=0.5,
        color_discrete_sequence=[light_green],
        labels={
            "geodesic_dist": "Geodesic Distance from JFK (miles)",
            "alt": "Altitude (ft)"
        },
        title="Exploring Altitude vs Distance from NYC"
    )

    # Create histogram: Density of Airports by Latitude using Plotly Express
    hist_fig = px.histogram(
        df,
        x="lat",
        nbins=50,
        labels={
            "lat": "Latitude",
            "count": "Number of Airports"
        },
        title="Density of Airports by Latitude",
        color_discrete_sequence=[light_green]
    )

    # Add outlines to the histogram bars
    hist_fig.update_traces(marker=dict(
        line=dict(width=1, color="black")  # Black outline for clarity
    ))

    # Combine the two plots into a single figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            "Exploring Altitude vs Distance from NYC",
            "Density of Airports by Latitude"
        )
    )

    # Add scatter plot traces to the first subplot
    for trace in scatter_fig["data"]:
        fig.add_trace(trace, row=1, col=1)

    # Add histogram traces to the second subplot
    for trace in hist_fig["data"]:
        fig.add_trace(trace, row=2, col=1)

    # Update axis labels and overall layout
    fig.update_layout(height=800, showlegend=False)
    fig.update_xaxes(title_text="Geodesic Distance from JFK (miles)", row=1, col=1)
    fig.update_yaxes(title_text="Altitude (ft)", row=1, col=1)
    fig.update_xaxes(title_text="Latitude", row=2, col=1)
    fig.update_yaxes(title_text="Number of Airports", row=2, col=1)

    return fig

if __name__ == "__main__":
    fig = exploratory_analysis()
    fig.show()