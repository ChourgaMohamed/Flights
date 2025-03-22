from datetime import datetime
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


def plot_multiple_routes(dept_airport = "JFK", day_flight = "01-01-2023", airports_df = None, conn=None):
    """
    Plot multiple flight routes from a single departure airport to a list of target airports.

    Args:
        dept_airport (str): FAA code of the departure airport.
        faa_codes (list): List of FAA codes for target airports.
    """
    if conn is None:
        conn = utils.get_db_connection()
    faa_codes, frequency = get_dest_airports(dept_airport, day_flight, conn)
    df = airports_df
    
    dept_airport_data = df[df["faa"] == dept_airport]
    target_airports = df[df["faa"].isin(faa_codes)]

    if dept_airport_data.empty:
        print(f"Departure airport with FAA code {dept_airport} not found!")
        return

    if target_airports.empty:
        print("No valid target airports found!")
        return

    # Combine all airport points for the scatter geo plot
    plot_data = pd.concat([dept_airport_data, target_airports])
    fig = px.scatter_geo(
        plot_data, lat="lat", lon="lon",
        text="name",
        hover_name="name",
        title=f"Routes from {dept_airport} on the {day_flight} that occur more than 5 times",
        size_max=5,
        opacity=0.6,
        color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]]
    )

    # Draw a line from the departure airport to each target airport
    for faa in faa_codes:
        target_airport = df[df["faa"] == faa]
        if not target_airport.empty:
            # Create a small DataFrame with two rows: one for the departure airport and one for the target airport.
            line_data = pd.DataFrame([dept_airport_data.iloc[0], target_airport.iloc[0]])
            fig.add_trace(px.line_geo(line_data, lat="lat", lon="lon", line_dash_sequence=['solid'], color_discrete_sequence=[utils.COLOR_PALETTE["pakistan_green"]]).data[0])

    # Autozoom to the selected routes with a bit less zoom
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
    
    df = pd.DataFrame(frequency, columns=["Airport", "Visit Count"])
    fig2 = px.bar(df, x="Airport", y="Visit Count", 
                 title=f"Flight Frequency from {dept_airport} on {day_flight}",
                 labels={"Airport": "Destination Airport", "Visit Count": "Number of Flights"},
                 color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]],
                 text_auto=True)

    fig2.update_layout(yaxis_title="Number of flights", xaxis_title="Destination airport")

    return fig, fig2

def get_dest_airports(dep_airport = "JFK", day_flight = "01-01-2023", conn=None):
  
    date_obj = datetime.strptime(day_flight, "%Y-%m-%d")
    day_dep = date_obj.day
    month_dep = date_obj.month
    query = """
    SELECT dest
    FROM flights 
    WHERE dest IS NOT NULL 
    AND origin = ? AND day = ? AND month = ?;
    """
    data = utils.execute_query(query, fetch='all', conn=conn, params=(dep_airport, day_dep, month_dep))
    airport_counts = {}
    for row in data:
        airport = row[0]
        airport_counts[airport] = airport_counts.get(airport, 0) + 1
    
    airport_visit_counts = sorted(airport_counts.items(), key=lambda x: x[1], reverse=True)
    print("Airport Visit Counts:", airport_visit_counts)  # Debugging step (optional)
    frequent_airports = [airport for airport, count in airport_counts.items() if count > 5]
    return frequent_airports, airport_visit_counts

def main():
    """Test flight route functions."""
    fig1 = plot_flight_route("JFK", "LAX")
    if fig1:
        fig1.show()
    fig2 = plot_multiple_routes("JFK", ["LAX", "ORD", "MIA"])
    if fig2:
        fig2.show()


if __name__ == "__main__":
    main()
