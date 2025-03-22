import pandas as pd
import numpy as np
from flights_project import utils
from scipy.stats import gaussian_kde
import plotly.graph_objects as go

def get_flight_statistics(dep_airport, arr_airport, conn=None):
    """
    Retrieve flight statistics for a route.
    
    Returns:
        A tuple of descriptive text and a DataFrame with total flights,
        average departure delay, air time, and arrival delay.
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
    query = """
    SELECT COUNT(*) AS total_flights,
           AVG(dep_delay) AS avg_departure_delay,
           AVG(air_time) AS avg_air_time,
           AVG(arr_delay) AS avg_arrival_delay
    FROM flights
    WHERE origin = ? AND dest = ?
    """
    result = utils.execute_query(query, params=(dep_airport, arr_airport), fetch="all", conn=conn)
    text = f"Flight statistics for {dep_airport} → {arr_airport}"
    return text, result

def delay_histogram(airport, start_date, end_date, conn=None):
    """
    Plot KDE curves for departure and arrival delays for a given airport and date range.
    
    Returns:
        A Plotly figure.
    """
    if conn is None:
        conn = utils.get_persistent_db_connection()
    query = """
    SELECT dep_delay, arr_delay
    FROM flights
    WHERE origin = ? AND date BETWEEN ? AND ?
    """
    df = pd.read_sql_query(query, conn, params=(airport, start_date, end_date))
    
    if df.empty:
        msg = f"No delay data available for {airport} between {start_date} and {end_date}."
        print(msg)
        return msg
    
    # Define x_grid between -100 and 250
    x_grid = np.linspace(-100, 250, 200)
    
    # Compute KDE for departure and arrival delays.
    kde_dep = gaussian_kde(df["dep_delay"].dropna())
    kde_arr = gaussian_kde(df["arr_delay"].dropna())
    dep_density = kde_dep(x_grid)
    arr_density = kde_arr(x_grid)
    
    # Create Plotly figure.
    fig = go.Figure()
    
    # Use colors from the shared palette.
    dep_color = utils.COLOR_PALETTE.get("pakistan_green", "darkgreen")
    arr_color = utils.COLOR_PALETTE.get("light_green", "limegreen")
    
    fig.add_trace(go.Scatter(
        x=x_grid.tolist(),
        y=dep_density,
        mode="lines",
        name="Departure delay",
        line=dict(color=dep_color, width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=x_grid.tolist(),
        y=arr_density,
        mode="lines",
        name="Arrival delay",
        line=dict(color=arr_color, width=2)
    ))
    
    fig.update_layout(
        title=f"Delay Statistics at {airport} from {start_date} to {end_date}",
        xaxis_title="Delay (minutes)",
        yaxis_title="Density",
        legend_title="Delay Type",
        xaxis_range=[-100, 250]
    )
    
    return fig

def get_nyc_flight_statistics(conn=None):
    """
    Retrieve NYC flight statistics for 2023, including total flights and breakdown by airport.
    """
    nyc_airports = ["JFK", "LGA", "EWR"]
    if conn is None:
        conn = utils.get_persistent_db_connection()
    
    query_total = """
    SELECT COUNT(*) AS total_nyc_flights
    FROM flights
    WHERE origin IN (?, ?, ?) AND year = 2023
    """
    total_flights = pd.read_sql_query(query_total, conn, params=nyc_airports)

    query_per_airport = """
    SELECT origin, COUNT(*) AS num_flights
    FROM flights
    WHERE origin IN (?, ?, ?) AND year = 2023
    GROUP BY origin
    ORDER BY num_flights DESC
    """
    flights_per_airport = pd.read_sql_query(query_per_airport, conn, params=nyc_airports)
    return total_flights.iloc[0, 0], flights_per_airport

def main():
    # Get persistent database connection
    conn = utils.get_persistent_db_connection()

    ######
    # Example usage of functions
    ######

    # Plot delay histogram for JFK airport in January 2023
    fig = delay_histogram("JFK", "2023-01-01", "2023-01-31", conn)
    if isinstance(fig, str):
        print(fig)
    else:
        fig.show()

    # Get flight statistics for JFK to LAX route
    text, result = get_flight_statistics("JFK", "LAX",conn)
    print(text)
    print(result)

    # Get NYC flight statistics for 2023
    total, per_airport = get_nyc_flight_statistics(conn)
    print("Total flights:", total)
    print("Flights per airport:")
    print(per_airport)


if __name__ == "__main__":
    main()
