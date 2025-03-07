import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('flights_database.db')

# Load the flights table
flights = pd.read_sql_query("SELECT * FROM flights", conn)

# ----------- 1. Check for missing values -----------
missing_values = flights.isnull().sum()
print("Missing values per column:\n", missing_values)

# Example fix: fill missing dep_time with sched_dep_time
flights['dep_time'].fillna(flights['sched_dep_time'], inplace=True)

# ----------- 2. Look for duplicates -----------
duplicates = flights.duplicated(subset=['flight', 'tailnum', 'origin', 'dest', 'dep_time', 'arr_time'])
print(f"Number of duplicate flights: {duplicates.sum()}")

# Remove duplicates
flights = flights[~duplicates]

# ----------- 3. Convert times to datetime -----------
def convert_to_datetime(date_col, time_col):
    dt = pd.to_datetime(flights[date_col], format='%Y-%m-%d')
    time = flights[time_col].apply(lambda x: pd.to_timedelta(f"{int(x):04d}"[:2] + ':' + f"{int(x):04d}"[2:] + ':00') if pd.notnull(x) else pd.NaT)
    return dt + time

flights['scheduled_dep_datetime'] = convert_to_datetime('date', 'sched_dep_time')
flights['dep_datetime'] = convert_to_datetime('date', 'dep_time')
flights['scheduled_arr_datetime'] = convert_to_datetime('date', 'sched_arr_time')
flights['arr_datetime'] = convert_to_datetime('date', 'arr_time')

# ----------- 4. Check if the data is consistent -----------
def check_flight_data(row):
    if pd.notnull(row['air_time']) and pd.notnull(row['dep_datetime']) and pd.notnull(row['arr_datetime']):
        expected_air_time = (row['arr_datetime'] - row['dep_datetime']).total_seconds() / 60
        return np.isclose(expected_air_time, row['air_time'], atol=5)
    return True

flights['is_consistent'] = flights.apply(check_flight_data, axis=1)
inconsistent_flights = flights[~flights['is_consistent']]
print(f"Inconsistent flights found: {len(inconsistent_flights)}")

# ----------- 5. Add local arrival time column -----------
# Load airports data to get timezones
airports = pd.read_sql_query("SELECT faa, tz FROM airports", conn)
tz_dict = dict(zip(airports['faa'], airports['tz']))

def calculate_local_arrival_time(row):
    dep_tz = tz_dict.get(row['origin'], 0)
    arr_tz = tz_dict.get(row['dest'], 0)
    if pd.notnull(row['arr_datetime']):
        time_diff = arr_tz - dep_tz
        return row['arr_datetime'] + timedelta(hours=time_diff)
    return pd.NaT

flights['local_arrival_time'] = flights.apply(calculate_local_arrival_time, axis=1)

# ----------- 6. Weather effects on plane types -----------
# Example: merge with weather data and analyze
weather = pd.read_sql_query("SELECT * FROM weather", conn)
planes = pd.read_sql_query("SELECT * FROM planes", conn)

# Merge flights with planes to get plane type
flights = flights.merge(planes[['tailnum', 'manufacturer', 'model']], on='tailnum', how='left')

# Merge flights with weather on origin airport and datetime
weather['datetime'] = pd.to_datetime(weather['date']) + pd.to_timedelta(weather['hour'], unit='h')
flights = pd.merge_asof(flights.sort_values('dep_datetime'), 
                        weather.sort_values('datetime'),
                        left_on='dep_datetime', 
                        right_on='datetime', 
                        by='origin', 
                        direction='backward')

# Example: Analyze effect of precipitation on delays
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10,6))
sns.boxplot(x='manufacturer', y='dep_delay', hue='precip', data=flights)
plt.title('Departure Delay by Manufacturer and Precipitation')
plt.xticks(rotation=45)
plt.show()

# ----------- 7. Grouped functions for dashboard prep -----------
def stats_by_airport(airport_code):
    subset = flights[flights['origin'] == airport_code]
    return {
        'total_flights': len(subset),
        'avg_dep_delay': subset['dep_delay'].mean(),
        'avg_arr_delay': subset['arr_delay'].mean(),
        'top_destinations': subset['dest'].value_counts().head(5).to_dict()
    }

print(stats_by_airport('JFK'))

# Close the database connection
conn.close()