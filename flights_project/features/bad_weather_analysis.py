import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from flights_project import utils
import numpy as np
import plotly.express as px

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
    # -------------------------------------------------------------------------
    query = """
    SELECT
        f.origin,
        f.dest,
        f.dep_delay,
        f.arr_delay,
        f.air_time,
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
    df["bad_weather"] = (
        (df["precip"] > 0.05) |
        (df["visib"] < 10)    |
        (df["wind_speed"] > 17.5) |
        (df["temp"] < 30)      |
        (df["wind_gust"] > 20)
    ).astype(int)  # 1 = bad weather, 0 = not bad

    # -------------------------------------------------------------------------
    # 3. Correlation Analysis
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
    correlation_matrix = corr_df.corr().round(2)

    print("\n=== Correlation Matrix (Delays, Flight Time, Weather, Bad Weather) ===")
    print(correlation_matrix, "\n")

    # -------------------------------------------------------------------------
    # 3a. Correlation between Bad Weather and Arrival Delay (with p-value)
    # -------------------------------------------------------------------------
    sub_df = df[['bad_weather', 'arr_delay']].dropna()
    corr_value, p_value = pearsonr(sub_df['bad_weather'], sub_df['arr_delay'])
    print("=== Bad Weather vs. Arrival Delay ===")
    text1 = (f"Correlation coefficient: {corr_value:.2f}")
    text2 = (f"P-value: {p_value:.3f}\n")
    print(text1)
    print(text2)

    # -------------------------------------------------------------------------
    # 4. Visualization
    #    a) Correlation Heatmap (only bottom triangle)
    #    b) Boxplot for Delays under bad vs. not-bad weather
    # -------------------------------------------------------------------------
    
    # (a) Correlation Heatmap with nicer labels
    rename_dict = {
        "dep_delay":   "Departure Delay",
        "arr_delay":   "Arrival Delay",
        "air_time":    "Flight Time",
        "wind_speed":  "Wind Speed",
        "wind_dir":    "Wind Direction",
        "precip":      "Precipitation",
        "visib":       "Visibility",
        "temp":        "Temperature",
        "pressure":    "Pressure",
        "humid":       "Humidity",
        "bad_weather": "Bad Weather",
        "wind_gust":   "Wind Gust"
    }
    
    # Rename rows/columns in the correlation matrix
    corr_renamed = correlation_matrix.rename(index=rename_dict, columns=rename_dict)
    
    # Create a mask for the upper triangle (excluding the diagonal)
    mask = np.triu(np.ones(corr_renamed.shape, dtype=bool), k=1)
    # Mask the correlation matrix so only the lower triangle is shown
    corr_lower = corr_renamed.mask(mask)

    fig1 = px.imshow(
        corr_lower,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=utils.CUSTOM_PLOTLY_COLOR_SCALE,
        range_color=(-1, 1),  # Ensures a consistent scale from -1 to +1
        title="Correlation Heatmap: Flight & Weather Variables (Bottom Triangle)",
    )
    # Move x-axis labels to the top and add a colorbar title
    fig1.update_layout(
        coloraxis_colorbar=dict(title="Correlation"),
    )

    # (b) Boxplot: Compare arrival delay under bad vs. not-bad weather
    fig2 = px.box(
        df,
        x="bad_weather",
        y="arr_delay",
        title="Arrival Delay vs. Bad Weather Indicator",
        labels={"bad_weather": "Bad Weather (1 = Yes, 0 = No)", "arr_delay": "Arrival Delay (minutes)"},
        category_orders={"bad_weather": [0, 1]},
        range_y=[-100, 100],
        points=False,  # Hide outliers
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]]
    )
    
    return df, fig1, fig2, text1, text2


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
