"""
This module compares airline performance from the flights database.
It computes on-time performance metrics:
    - Within 15 min %
    - Within 1 hr %
    - Within 2 hr %
100% is good and 0% is bad. Cancellations are dropped.
A spider (polar) chart is produced to visualize the performance metrics.
Uses shared DB helpers and color palette from utils.
"""

from flights_project import utils
import plotly.graph_objects as go

def get_airline_performance(conn=None):
    """
    Compute performance metrics per airline, but only include airlines
    that have at least 2 valid data points in each of the following:
      1) departure delay
      2) arrival delay
      3) on-time performance (non-cancelled flights)
      4) total flights

    Returns a list of dicts, each containing:
      carrier, airline_name, on_time performance metrics (within 15 min, 1 hr, 2 hr),
      average departure/arrival delays, most frequent route, total_flights, etc.
    """
    # Updated SQL: add counts for flights within 1 hour and 2 hours
    query = """
    SELECT 
        f.carrier,
        a.name AS airline_name,
        COUNT(*) AS total_flights,
        SUM(CASE WHEN f.dep_delay IS NOT NULL THEN 1 ELSE 0 END) AS valid_dep_delay_count,
        SUM(CASE WHEN f.arr_delay IS NOT NULL THEN 1 ELSE 0 END) AS valid_arr_delay_count,
        COUNT(f.dep_delay) AS non_cancelled,
        SUM(CASE WHEN f.dep_delay <= 15 THEN 1 ELSE 0 END) AS on_time_count,
        SUM(CASE WHEN f.dep_delay <= 60 THEN 1 ELSE 0 END) AS within_1hr_count,
        SUM(CASE WHEN f.dep_delay <= 120 THEN 1 ELSE 0 END) AS within_2hr_count,
        AVG(f.dep_delay) AS avg_dep_delay,
        AVG(f.arr_delay) AS avg_arr_delay
    FROM flights f
    JOIN airlines a 
      ON f.carrier = a.carrier
    GROUP BY f.carrier, a.name
    ORDER BY a.name;
    """
    data = utils.execute_query(query, fetch='all', conn=conn)

    results = []
    for row in data:
        (
            carrier, airline_name,
            total_flights,
            valid_dep_delay_count,
            valid_arr_delay_count,
            non_cancelled,
            on_time_count,
            within_1hr_count,
            within_2hr_count,
            avg_dep_delay,
            avg_arr_delay
        ) = row

        # Skip if carrier is missing or empty
        if carrier is None or not isinstance(carrier, str) or not carrier.strip():
            continue

        # Data quality: require >= 2 data points for each category
        if (
            valid_dep_delay_count < 2 or
            valid_arr_delay_count < 2 or
            non_cancelled < 2 or
            total_flights < 2
        ):
            continue

        # Compute on-time performance metrics (percentage of non-cancelled flights)
        on_time_15 = (on_time_count / non_cancelled) * 100 if non_cancelled else 0
        on_time_60 = (within_1hr_count / non_cancelled) * 100 if non_cancelled else 0
        on_time_120 = (within_2hr_count / non_cancelled) * 100 if non_cancelled else 0

        # Get the most frequent route for this airline
        route_query = """
        SELECT origin || '-' || dest AS route, COUNT(*) AS route_count 
        FROM flights 
        WHERE carrier = ?
        GROUP BY route 
        ORDER BY route_count DESC 
        LIMIT 1;
        """
        route_data = utils.execute_query(
            route_query, params=(carrier,), fetch='one', conn=conn
        )
        most_freq_route = route_data[0] if route_data else "N/A"

        results.append({
            "carrier": carrier,
            "airline_name": airline_name if airline_name else carrier,
            "on_time_15": on_time_15,
            "on_time_60": on_time_60,
            "on_time_120": on_time_120,
            "avg_dep_delay": avg_dep_delay,
            "avg_arr_delay": avg_arr_delay,
            "most_freq_route": most_freq_route,
            "total_flights": total_flights
        })

    return results

def get_all_carriers(conn=None):
    """
    Return a sorted list of airline names (or codes if name is missing) 
    for all carriers in the database that pass the data-quality filter.
    """
    performance = get_airline_performance(conn)
    carriers = []
    for p in performance:
        label = p["airline_name"] if p["airline_name"] else p["carrier"]
        if label not in carriers:
            carriers.append(label)
    return sorted(carriers)

def get_top_carriers_by_flight_count(conn=None, limit=3):
    """
    Return a list of the top N carriers (by total flight count),
    only among those that meet the data-quality filter.
    """
    performance = get_airline_performance(conn)
    performance_sorted = sorted(performance, key=lambda x: x["total_flights"], reverse=True)
    top_carriers = []
    for p in performance_sorted:
        label = p["airline_name"] if p["airline_name"] else p["carrier"]
        if label not in top_carriers:
            top_carriers.append(label)
        if len(top_carriers) == limit:
            break
    return top_carriers

def plot_airline_performance_spider(conn=None, carriers=None):
    """
    Create a spider (polar) chart comparing airline performance for the
    specified carriers (or all that pass the filter if carriers is None).

    The chart displays three metrics:
        - Within 15 min %
        - Within 1 hr %
        - Within 2 hr %

    Returns:
        A Plotly figure containing the spider chart.
    """
    performance = get_airline_performance(conn)

    # Filter if specific carriers were chosen
    if carriers:
        filtered = []
        for p in performance:
            label = p["airline_name"] if p["airline_name"] else p["carrier"]
            if label in carriers:
                filtered.append(p)
        performance = filtered

    if not performance:
        return None  # Nothing to plot

    # Define metric labels and categories
    categories = ["Within 15 min %", "Within 1 hr %", "Within 2 hr %"]

    # Create Plotly figure
    fig = go.Figure()

    # Cycle through colors from the palette for different airlines
    palette_colors = list(utils.COLOR_PALETTE.values())

    for idx, d in enumerate(performance):
        # Extract metrics for the airline
        m15 = d["on_time_15"]
        m60 = d["on_time_60"]
        m120 = d["on_time_120"]
        # Create list of metric values and close the loop by repeating the first metric
        values = [m15, m60, m120, m15]
        # Append the first category to the list of category labels
        theta = categories + [categories[0]]
        label = d["airline_name"] if d["airline_name"] else d["carrier"]

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=theta,
            mode="lines+markers",
            name=label,
            line=dict(color=palette_colors[idx % len(palette_colors)])
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="Airline Performance Spider Chart (On-Time Metrics)",
        showlegend=True
    )
    return fig

def main():
    """Example usage: show a spider chart with all carriers (that pass the filter)
       and print the top 3 carriers by flight count.
    """
    fig = plot_airline_performance_spider()
    if fig:
        fig.show()
    else:
        print("No data to plot.")

    # Also print top 3 carriers by flight count
    print("Top 3 carriers:", get_top_carriers_by_flight_count(limit=3))

if __name__ == "__main__":
    main()
