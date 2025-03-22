import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr  # New import for correlation testing

# If you don't have a custom utils module, replace with sqlite3.connect("path_to_db.sqlite")
from flights_project import utils

def bad_weather_analysis(conn=None):
    """
    Analyze how 'bad weather' conditions correlate with flight delays, cancellations,
    and flight time. Produces:
      - A correlation matrix among key flight & weather variables
      - A boxplot comparing delays under 'bad weather' vs. normal conditions.
      - The correlation coefficient (with p-value) between bad weather and arrival delay.
    """

    # -------------------------------------------------------------------------
    # 1. Query flights + weather
    #    (Adjust this query to match your schema or if you have a cancellations column)
    # -------------------------------------------------------------------------
    query = """
    SELECT
        f.origin,
        f.dest,
        f.dep_delay,
        f.arr_delay,
        f.air_time,
        -- f.cancelled,  -- Uncomment if you actually have a 'cancelled' column
        w.wind_speed,
        w.wind_dir,
        w.precip,
        w.visib,
        w.temp,
        w.pressure,
        w.wind_gust,
        w.humid
    FROM flights f
    JOIN weather w
        ON f.origin = w.origin
        AND f.year = w.year
        AND f.month = w.month
        AND f.day = w.day
        AND f.hour = w.hour
    WHERE f.dep_delay IS NOT NULL
      AND f.arr_delay IS NOT NULL
      AND f.air_time IS NOT NULL
      AND w.wind_speed IS NOT NULL
      AND w.wind_dir IS NOT NULL
    """
    
    if conn is None:
        with utils.get_db_connection() as c:
            df = pd.read_sql(query, c)
    else:
        df = pd.read_sql(query, conn)

    # -------------------------------------------------------------------------
    # 2. "bad weather" indicator
    # -------------------------------------------------------------------------
    # Based of observed histograms and research, we'll define "bad weather" as:
    df["bad_weather"] = (
        (df["precip"] > 0.05) |
        (df["visib"] < 10)    |
        (df["wind_speed"] > 17.5) |
        (df["temp"] < 30)      |
        (df["wind_gust"] > 20)
    ).astype(int)  # 1 = bad weather, 0 = not bad

    # -------------------------------------------------------------------------
    # 3. Correlation Analysis
    #    We'll look at correlations among flight delays, air_time, weather vars
    # -------------------------------------------------------------------------
    corr_vars = [
        "dep_delay", 
        "arr_delay", 
        "air_time",
        "wind_speed", 
        "wind_dir", 
        "precip", 
        "visib", 
        "temp", 
        "pressure", 
        "humid",
        "bad_weather",
        "wind_gust",
    ]

    # Keep only columns that actually exist in the DataFrame
    corr_vars = [v for v in corr_vars if v in df.columns]
    
    # Drop rows with any missing data in these columns
    corr_df = df[corr_vars].dropna()
    
    # Compute correlation matrix
    correlation_matrix = corr_df.corr()

    print("\n=== Correlation Matrix (Delays, Flight Time, Weather, Bad Weather) ===")
    print(correlation_matrix, "\n")

    # -------------------------------------------------------------------------
    # 3a. Correlation between Bad Weather and Arrival Delay (with p-value)
    # -------------------------------------------------------------------------
    # Drop missing values for the two specific columns
    sub_df = df[['bad_weather', 'arr_delay']].dropna()
    corr_value, p_value = pearsonr(sub_df['bad_weather'], sub_df['arr_delay'])
    print("=== Bad Weather vs. Arrival Delay ===")
    print(f"Correlation coefficient: {corr_value:.2f}")
    print(f"P-value: {p_value:.3f}\n")

    # -------------------------------------------------------------------------
    # 4. Visualization
    #    a) Correlation Heatmap
    #    b) Boxplot for Delays under bad vs. not-bad weather
    # -------------------------------------------------------------------------
    
    # (a) Correlation Heatmap
    fig1 = plt.figure(figsize=(10, 8))
    sns.heatmap(
        correlation_matrix, 
        annot=True, 
        fmt=".2f", 
        cmap="coolwarm", 
        square=True,
        cbar_kws={"shrink": 0.8}
    )
    plt.title("Correlation Heatmap: Flight & Weather Variables")
    plt.tight_layout()
    

    # (b) Boxplot: Compare arrival delay under bad vs. not-bad weather
    fig2 = plt.figure(figsize=(6, 5))
    sns.boxplot(
        x="bad_weather", 
        y="arr_delay", 
        data=df, 
        palette="Set2",
        showfliers=False
    )
    plt.title("Arrival Delay vs. Bad Weather Indicator")
    plt.xlabel("Bad Weather (1 = Yes, 0 = No)")
    plt.ylabel("Arrival Delay (minutes)")
    

    return df, fig1, fig2

def main():
    """
    Example main function to run the bad_weather_analysis.
    """
    print("Running Bad Weather Analysis...")
    final_df, fig1, fig2 = bad_weather_analysis()
    # final_df now contains a 'bad_weather' column for further custom analyses.
    plt.show()

if __name__ == "__main__":
    main()
