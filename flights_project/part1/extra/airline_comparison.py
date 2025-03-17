"""
This module compares airline performance from the flights database.
It computes average departure/arrival delays, on-time performance,
cancellation rates, and the most frequent route per airline.
A spider (radar) chart is produced to visualize the performance metrics.
Uses shared DB helpers from utils.
"""

import matplotlib.pyplot as plt
import numpy as np
from flights_project import utils

def get_airline_performance(conn=None):
    """
    Compute performance metrics per airline, but only include airlines
    that have at least 2 valid data points in each of the 4 categories:
      1) departure delay
      2) arrival delay
      3) on-time performance (non-cancelled flights)
      4) cancellation rate (total flights)

    Also uses an INNER JOIN on airlines, so any carrier not in the airlines
    table is excluded.

    Returns a list of dicts, each containing:
      carrier, airline_name, avg_dep_delay, avg_arr_delay,
      on_time_performance, cancellation_rate, most_freq_route, total_flights
    """
    # We gather counts for each category to ensure each airline has >= 2 data points
    query = """
    SELECT 
        f.carrier,
        a.name AS airline_name,
        COUNT(*) AS total_flights,
        -- Number of flights that have a non-null dep_delay
        SUM(CASE WHEN f.dep_delay IS NOT NULL THEN 1 ELSE 0 END) AS valid_dep_delay_count,
        -- Number of flights that have a non-null arr_delay
        SUM(CASE WHEN f.arr_delay IS NOT NULL THEN 1 ELSE 0 END) AS valid_arr_delay_count,
        -- Number of flights that are not cancelled (dep_delay is not null)
        COUNT(f.dep_delay) AS non_cancelled,
        -- Among non-cancelled flights, how many have dep_delay <= 15
        SUM(CASE WHEN f.dep_delay <= 15 THEN 1 ELSE 0 END) AS on_time_count,
        -- We'll still compute average dep/arr delays
        AVG(f.dep_delay) AS avg_dep_delay,
        AVG(f.arr_delay) AS avg_arr_delay
    FROM flights f
    -- Use an INNER JOIN so we only include carriers that appear in 'airlines'
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
            avg_dep_delay,
            avg_arr_delay
        ) = row

        # Skip if carrier is missing or empty
        if carrier is None or not isinstance(carrier, str) or not carrier.strip():
            continue

        # We require >= 2 data points for each category:
        #  1) dep_delay -> valid_dep_delay_count >= 2
        #  2) arr_delay -> valid_arr_delay_count >= 2
        #  3) on-time   -> non_cancelled >= 2
        #  4) total_flights >= 2
        if (
            valid_dep_delay_count < 2 or
            valid_arr_delay_count < 2 or
            non_cancelled < 2 or
            total_flights < 2
        ):
            # Skip this airline because it doesn't have enough data
            continue

        # Compute final metrics
        cancellation_rate = (
            (total_flights - non_cancelled) / total_flights * 100
            if total_flights else 0
        )
        on_time_performance = (
            (on_time_count / non_cancelled) * 100
            if non_cancelled else 0
        )

        # Safely get the most frequent route for this airline
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
            "avg_dep_delay": avg_dep_delay,
            "avg_arr_delay": avg_arr_delay,
            "on_time_performance": on_time_performance,
            "cancellation_rate": cancellation_rate,
            "most_freq_route": most_freq_route,
            "total_flights": total_flights
        })

    return results


def get_all_carriers(conn=None):
    """
    Return a list of airline names (or codes if name is missing) 
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
    only among those that meet the data-quality filter above.
    """
    performance = get_airline_performance(conn)
    # Sort by total_flights descending
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
    Create a spider (radar) chart comparing airline performance for only the
    specified carriers. If carriers is None or empty, we plot all (that pass filter).

    The chart displays four metrics (normalized to 0-1 for comparability):
      - Average Departure Delay (inverted; lower is better)
      - Average Arrival Delay (inverted; lower is better)
      - On-Time Performance (higher is better)
      - Cancellation Rate (inverted; lower is better)

    Returns:
        Matplotlib figure containing the spider chart, or None if no data.
    """
    performance = get_airline_performance(conn)

    # Filter if a specific subset of carriers was chosen
    if carriers:
        filtered = []
        for p in performance:
            label = p["airline_name"] if p["airline_name"] else p["carrier"]
            if label in carriers:
                filtered.append(p)
        performance = filtered

    if not performance:
        return None  # Nothing to plot

    # Extract lists of raw values for normalization across selected airlines
    dep_delays = [d["avg_dep_delay"] for d in performance]
    arr_delays = [d["avg_arr_delay"] for d in performance]
    on_time = [d["on_time_performance"] for d in performance]
    canc_rate = [d["cancellation_rate"] for d in performance]
    
    # Helper functions to normalize metrics
    # For delays and cancellation rate, lower is better => invert
    def normalize_inverted(values, value):
        min_val, max_val = min(values), max(values)
        if max_val == min_val:  # edge case: all values same
            return 1.0
        return (max_val - value) / (max_val - min_val)
    
    # For on-time performance, higher is better
    def normalize(values, value):
        min_val, max_val = min(values), max(values)
        if max_val == min_val:  # edge case: all values same
            return 1.0
        return (value - min_val) / (max_val - min_val)
    
    labels = ['Avg Dep Delay', 'Avg Arr Delay', 'On-Time %', 'Cancellation %']
    num_vars = len(labels)
    
    # Angles for radar/spider chart
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # close the loop
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for d in performance:
        norm_dep = normalize_inverted(dep_delays, d["avg_dep_delay"])
        norm_arr = normalize_inverted(arr_delays, d["avg_arr_delay"])
        norm_on_time = normalize(on_time, d["on_time_performance"])
        norm_canc = normalize_inverted(canc_rate, d["cancellation_rate"])
        
        values = [norm_dep, norm_arr, norm_on_time, norm_canc]
        values += values[:1]  # close the radar polygon
        
        label = d["airline_name"] if d["airline_name"] else d["carrier"]
        
        ax.plot(angles, values, label=label)
        ax.fill(angles, values, alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title("Airline Performance Spider Chart")
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    return fig


def main():
    """Example usage: run a spider chart with all carriers (that pass the filter)."""
    fig = plot_airline_performance_spider()
    if fig:
        plt.show()
    else:
        print("No data to plot.")

    # Also show top 3 carriers by flight count (that pass the filter)
    print("Top 3 carriers:", get_top_carriers_by_flight_count(limit=3))

if __name__ == "__main__":
    main()
