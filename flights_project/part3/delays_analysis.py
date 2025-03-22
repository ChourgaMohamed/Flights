"""
This module analyzes flight delays from the flights database.
Uses the shared DB helpers in utils.
"""

from datetime import datetime
import pandas as pd
import plotly.express as px
from flights_project import utils

def get_delay_data(start_date="2023-01-01", end_date="2023-12-31", conn=None):

    query = """
    SELECT dep_delay 
    FROM flights 
    WHERE dep_delay IS NOT NULL 
    AND date BETWEEN ? AND ?;
    """
    data = utils.execute_query(query, fetch='all', conn=conn, params=(start_date, end_date))
    return [row[0] for row in data]


def plot_delay_histogram(start_date="2023-01-01", end_date="2023-12-31", conn=None):
    if conn is None:
        conn = utils.get_db_connection()
    delays = get_delay_data(start_date, end_date, conn)
    fig = px.histogram(
        x=delays,
        range_x=[-20, 150],
        title=f"Departure delays ({start_date} to {end_date})",
        color_discrete_sequence=[utils.COLOR_PALETTE["india_green"]]
    )
    fig.update_layout(
    xaxis_title='Departure delay (minutes)',
    yaxis_title='Number of flights'
    )
    return fig

def get_day_delay(day="2023-01-01", conn=None):

    date_obj = datetime.strptime(day, "%Y-%m-%d")
    day = date_obj.day
    month = date_obj.month
    query_dep = """
    SELECT sched_dep_time, dep_delay 
    FROM flights 
    WHERE dep_delay IS NOT NULL 
    AND day = ? AND month = ?;
    """
    dep_data = utils.execute_query(query_dep, fetch='all', conn=conn, params=(day, month))
    query_arr = """
    SELECT sched_dep_time, arr_delay 
    FROM flights 
    WHERE arr_delay IS NOT NULL 
    AND day = ? AND month = ?;
    """
    arr_data = utils.execute_query(query_arr, fetch='all', conn=conn, params=(day, month))

    df_dep = pd.DataFrame(dep_data, columns=["sched_dep_time", "dep_delay"])
    df_arr = pd.DataFrame(arr_data, columns=["sched_dep_time", "arr_delay"])
    delay_df = pd.merge(df_dep, df_arr, on="sched_dep_time", how="outer")
    delay_df["sched_dep_time"] = delay_df["sched_dep_time"].astype(str).str.zfill(4).str[:-2] + ":" + delay_df["sched_dep_time"].astype(str).str[-2:]

    return delay_df


def plot_day_delay(day="2023-01-01", conn=None):
   if conn is None:
        conn = utils.get_db_connection()

   delay_df = get_day_delay(day, conn)
   delay_df = delay_df.sort_values("sched_dep_time")
   delay_df['sched_dep_time'] = delay_df['sched_dep_time'].str.replace('::', ':', regex=False)
   delay_df['sched_dep_time'] = pd.to_datetime(delay_df['sched_dep_time'])
   delay_df.set_index('sched_dep_time', inplace=True)
   delay_df_resemled = delay_df.resample('2H').mean().reset_index()
   delay_df_resemled['time'] = delay_df_resemled['sched_dep_time'].dt.time
    
   fig = px.line(
        delay_df_resemled, 
        x="time", 
        y=["dep_delay", "arr_delay"],
        title=f"Delays on ({day})",
        color_discrete_map={
            "dep_delay": utils.COLOR_PALETTE["pakistan_green"],
            "arr_delay": utils.COLOR_PALETTE["light_green"]
        }
    )
   fig.update_layout(
    xaxis_title='Time',
    yaxis_title='Delay (minutes)'
    )
   fig.update_xaxes(
       tickformat="%H:%M",
       tickmode="array",
       tickvals=pd.date_range("00:00", "23:59", freq="1H").time
     )
   return fig
   

def main():
    # Opening a persistent connection
    conn = utils.get_persistent_db_connection()

    """Run delay analysis (opens its own DB connection if none provided)."""
    fig = plot_delay_histogram(conn=conn)
    fig.show()

if __name__ == "__main__":
    main()
