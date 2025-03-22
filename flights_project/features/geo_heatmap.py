import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from flights_project import utils

def plot_flights_geo_heatmap(dept_airport=None, start_date="2023-01-01", end_date="2023-12-31", conn=None):
    """
    Plot flights from a certain airport or all departure airports to all other airports within a date range.
    Lines are colored by the number of flights using a color map.

    Args:
        dept_airport (str or list, optional): FAA code(s) of the departure airport(s). If None, include all departure airports.
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.
        conn (sqlite3.Connection, optional): Existing DB connection.

    Returns:
        fig (Figure): Plotly figure object containing the interactive geo heatmap.
    """
    if conn is None:
        conn = utils.get_db_connection()

    query = """
    SELECT origin, dest, COUNT(*) as num_flights
    FROM flights
    WHERE date BETWEEN ? AND ?
    """
    params = [start_date, end_date]
    if dept_airport:
        if isinstance(dept_airport, list):
            query += " AND origin IN ({})".format(','.join(['?']*len(dept_airport)))
            params.extend(dept_airport)
        else:
            query += " AND origin = ?"
            params.append(dept_airport)
    query += " GROUP BY origin, dest"

    df = pd.read_sql_query(query, conn, params=params)

    airports_df = utils.load_airports_data()
    df = df.merge(airports_df, left_on="origin", right_on="faa", suffixes=("", "_origin"))
    df = df.merge(airports_df, left_on="dest", right_on="faa", suffixes=("", "_dest"))

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        lon=df['lon'],
        lat=df['lat'],
        hoverinfo='text',
        text=df['name'],
        mode='markers',
        marker=dict(
            size=2,
            color='rgb(255, 0, 0)',
            line=dict(
                width=3,
                color='rgba(68, 68, 68, 0)'
            )
        )
    ))

    for _, row in df.iterrows():
        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[row["lon"], row["lon_dest"]],
            lat=[row["lat"], row["lat_dest"]],
            mode='lines',
            line=dict(width=1, color=utils.COLOR_PALETTE["pakistan_green"]),
            opacity=float(row["num_flights"]) / float(df["num_flights"].max()),
            hoverinfo='text',
            text=f"Date: {start_date} to {end_date}<br>From: {row['name']}<br>To: {row['name_dest']}<br>Flights: {row['num_flights']}"
        ))

    fig.update_layout(
        title_text=f"Flights from {dept_airport if dept_airport else 'All Airports'} ({start_date} to {end_date})",
        showlegend=False,
        geo=dict(
            scope='north america',
            projection_type='azimuthal equal area',
            showland=True,
            showframe=False,
            showcoastlines=True,
            showlakes=True,
            showcountries=True,
            lakecolor=utils.COLOR_PALETTE["light_green"],
            landcolor=utils.COLOR_PALETTE["nyanza"],
            projection_scale=1.2
        ),
    )

    fig.update_geos(fitbounds="locations", visible=False)

    return fig

if __name__ == "__main__":
    conn = utils.get_persistent_db_connection()
    fig = plot_flights_geo_heatmap(dept_airport=["JFK"], start_date="2023-01-01", end_date="2023-12-31", conn=conn)
    fig.show()
