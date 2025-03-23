import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu

from flights_project import utils

def normalize_angle_diff(angle_diff):
    """Normalize angle differences to [-180, 180]."""
    return (angle_diff + 180) % 360 - 180

def calculate_flight_direction(dep_lat, dep_lon, arr_lat, arr_lon):
    """Compute bearing (0-360) from departure to arrival."""
    dep_lat_rad, arr_lat_rad = np.radians(dep_lat), np.radians(arr_lat)
    delta_lon = np.radians(arr_lon - dep_lon)

    x = np.sin(delta_lon) * np.cos(arr_lat_rad)
    y = (np.cos(dep_lat_rad) * np.sin(arr_lat_rad) -
         np.sin(dep_lat_rad) * np.cos(arr_lat_rad) * np.cos(delta_lon))

    bearing = np.degrees(np.arctan2(x, y))
    return (bearing + 360) % 360

def classify_wind(angle_diff, threshold=45):
    """
    Classify flights as Tailwind, Headwind, or Crosswind based on angle_diff in [-180, 180].
      - Tailwind if within +/- threshold of 0.
      - Headwind if within +/- threshold of ±180.
      - Crosswind otherwise.
    """
    if -threshold <= angle_diff <= threshold:
        return "Tailwind"
    if angle_diff >= 180 - threshold or angle_diff <= -180 + threshold:
        return "Headwind"
    return "Crosswind"

def group_flights_by_model_distance(conn=None, angle_threshold=45, distance_bin=100):
    """
    1. Pull flights + planes + weather + airports.
    2. Compute flight direction, angle difference -> tailwind/headwind/crosswind.
    3. Bin distances and return the resulting DataFrame.
    """
    query = """
    SELECT
        f.origin,
        f.dest,
        f.air_time,
        f.distance,
        f.tailnum,
        a1.lat AS dep_lat,
        a1.lon AS dep_lon,
        a2.lat AS arr_lat,
        a2.lon AS arr_lon,
        w.wind_dir,
        w.wind_speed,
        p.model AS plane_model
    FROM flights f
    JOIN weather w
        ON f.origin = w.origin
        AND f.year = w.year
        AND f.month = w.month
        AND f.day = w.day
        AND f.hour = w.hour
    JOIN airports a1
        ON f.origin = a1.faa
    JOIN airports a2
        ON f.dest = a2.faa
    JOIN planes p
        ON f.tailnum = p.tailnum
    WHERE f.air_time IS NOT NULL
      AND f.distance IS NOT NULL
      AND w.wind_speed IS NOT NULL
      AND w.wind_dir IS NOT NULL
      AND p.model IS NOT NULL
    """
    if conn is None:
        with utils.get_db_connection() as c:
            df = pd.read_sql(query, c)
    else:
        df = pd.read_sql(query, conn)

    # Compute flight direction, angle difference, wind_type
    df["flight_direction"] = df.apply(
        lambda row: calculate_flight_direction(
            row["dep_lat"], row["dep_lon"], row["arr_lat"], row["arr_lon"]
        ),
        axis=1
    )
    diff = df["flight_direction"] - df["wind_dir"]
    df["angle_diff"] = normalize_angle_diff(diff)
    df["wind_type"] = df["angle_diff"].apply(lambda x: classify_wind(x, angle_threshold))

    # Bin distance (e.g., every 100 miles)
    df["distance_bin"] = (df["distance"] // distance_bin) * distance_bin

    return df

def run_headwind_tailwind_tests(df, alpha=0.05):
    """
    For each (plane_model, distance_bin), compare 'air_time' for Headwind vs Tailwind flights.
    We run:
      - Welch's t-test (independent, unequal variances)
      - Mann–Whitney U test (non-parametric)
    and keep only groups that have at least 5 flights in each category.
    """
    results = []
    grouped = df.groupby(["plane_model", "distance_bin"])

    for (plane, dist), group in grouped:
        tail = group.loc[group["wind_type"] == "Tailwind", "air_time"]
        head = group.loc[group["wind_type"] == "Headwind", "air_time"]

        if len(tail) >= 5 and len(head) >= 5:
            # 1) T-test
            t_stat, t_pval = ttest_ind(tail, head, equal_var=False)

            # 2) Mann-Whitney U (two-sided)
            u_stat, u_pval = mannwhitneyu(tail, head, alternative="two-sided")

            # Summarize
            results.append({
                "plane_model": plane,
                "distance_bin": dist,
                "count_tail": len(tail),
                "count_head": len(head),
                "mean_tail": tail.mean(),
                "mean_head": head.mean(),
                "t_stat": t_stat,
                "t_pval": t_pval,
                "u_stat": u_stat,
                "u_pval": u_pval
            })

    results_df = pd.DataFrame(results)
    if results_df.empty:
        print("No groups with sufficient data for both headwind & tailwind.")
        return results_df

    # 3. Mark significant if both p-values < alpha (or you can pick one test)
    results_df["significant"] = (
        (results_df["t_pval"] < alpha) & 
        (results_df["u_pval"] < alpha)
    )

    # 4. Indicate direction (which is faster?)
    # If mean_head > mean_tail => "Tailwind is faster"
    results_df["faster_side"] = np.where(
        results_df["mean_head"] > results_df["mean_tail"],
        "Tailwind is faster", 
        "Headwind is faster"
    )

    return results_df

def analyze_significant_bins(results_df):
    """
    Filter to significant bins, aggregate all results, and provide a final conclusion.
    """

    # 1. Filter to only significant groups
    sig_df = results_df[results_df["significant"] == True].copy()
    total_sig = len(sig_df)

    if total_sig == 0:
        print("\nNo bins are statistically significant based on the chosen criteria.")
        return

    # 2. Count how many bins show "Tailwind is faster" vs "Headwind is faster"
    counts = sig_df["faster_side"].value_counts()
    tailwind_faster = counts.get("Tailwind is faster", 0)
    headwind_faster = counts.get("Headwind is faster", 0)

    # 3. Print summary
    print("\n=== Significant Bins Summary ===")
    print(f"Total significant bins: {total_sig}")
    print(f"Tailwind is faster in {tailwind_faster} bins.")
    print(f"Headwind is faster in {headwind_faster} bins.")

    # 4. Overall percentages
    tail_pct = (tailwind_faster / total_sig) * 100
    head_pct = (headwind_faster / total_sig) * 100
    print(f"Percentage of significant bins with Tailwind faster: {tail_pct:.2f}%")
    print(f"Percentage of significant bins with Headwind faster: {head_pct:.2f}%")

    # 5. Overall conclusion
    if tailwind_faster > headwind_faster:
        print("\nConclusion: For bins where we see a significant difference, "
              "tailwinds more often correspond to shorter air times.")
    else:
        print("\nConclusion: For bins where we see a significant difference, "
              "headwinds more often correspond to shorter air times (unexpected, "
              "could be due to data mismatch or other confounders).")

def main():
    # 1. Gather data
    df = group_flights_by_model_distance(angle_threshold=45, distance_bin=100)

    # 2. Run T-test & Mann-Whitney on headwind vs tailwind
    results_df = run_headwind_tailwind_tests(df, alpha=0.05)
    if results_df.empty:
        return  # No valid groups

    # 3. Show a few lines of raw results
    print("\n=== Headwind vs. Tailwind Test Results (Sample) ===")
    print(results_df.head(10))

    # 4. Select significant bins and aggregate
    analyze_significant_bins(results_df)

if __name__ == "__main__":
    main()
