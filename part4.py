import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

connector = sqlite3.connect('flights_database.db')
flights = pd.read_sql_query("SELECT * FROM flights", connector)
total_rows = len(flights)
flights_cleaned = flights.dropna()
remaining_rows = len(flights_cleaned)
deleted_rows = total_rows - remaining_rows
percentage_deleted = (deleted_rows / total_rows) * 100
print(f"Percentage of deleted rows: {percentage_deleted:.2f}%")
missing_values = flights_cleaned.isnull().sum()
print("Missing values per column:\n", missing_values)
# Remove duplicates
duplicates = flights_cleaned.duplicated()
print(f"Number of duplicate flights: {duplicates.sum()}")
flights = flights_cleaned.drop_duplicates()

# Convert times to datetime
if not {'year', 'month', 'day'}.issubset(flights.columns):
    raise ValueError("The dataset must contain 'year', 'month', and 'day' columns.")

flights['date'] = pd.to_datetime(flights[['year', 'month', 'day']])

def time_to_timedelta(time):
    if pd.isnull(time) or time == '' or time == 'NaN':
        return pd.NaT
    try:
        time = int(float(time)) 
        hours = time // 100  
        minutes = time % 100 
        return timedelta(hours=hours, minutes=minutes)
    except (ValueError, TypeError):
        return pd.NaT

for col in ['sched_dep_time', 'dep_time', 'sched_arr_time', 'arr_time']:
    flights[col] = flights[col].apply(time_to_timedelta)
    flights[col] = flights['date'] + flights[col] 

# Overnight Flights
flights.loc[
    (flights['dep_time'].dt.hour < 6) &
    (flights['sched_dep_time'].dt.hour > 18) & 
    (flights['dep_time'] < flights['sched_dep_time']),
    'dep_time'
] += timedelta(days=1)

flights.loc[
    (flights['sched_arr_time'].dt.hour < 6) & 
    (flights['sched_dep_time'].dt.hour > 18) & 
    (flights['sched_arr_time'] < flights['sched_dep_time']), 
    'sched_arr_time'
] += timedelta(days=1)

flights.loc[
    (flights['arr_time'].dt.hour < 6) & 
    (flights['dep_time'].dt.hour > 18) & 
    (flights['arr_time'] < flights['dep_time']), 
    'arr_time'
] += timedelta(days=1)

for col in ['sched_dep_time', 'dep_time', 'sched_arr_time', 'arr_time']:
    flights[col] = pd.to_datetime(flights[col], errors='coerce')

# Part of consistency
initial_rows = len(flights)
flights = flights[flights['sched_arr_time'] > flights['sched_dep_time']]
removed_rows = initial_rows - len(flights)
def fix_flight_data(row):
    sched_dep = row['sched_dep_time']
    dep = row['dep_time']
    sched_arr = row['sched_arr_time']
    arr = row['arr_time']
    air_time = row['air_time']
    dep_delay = row['dep_delay']
    arr_delay = row['arr_delay']

    # Fix dep_delay (if inconsistent)
    correct_dep_delay = (dep - sched_dep).total_seconds() / 60
    if not np.isclose(dep_delay, correct_dep_delay, atol=2):
        row['dep_delay'] = correct_dep_delay

    # Fix inconsistent arrival times
    if arr <= dep:
        if pd.notnull(sched_arr) and pd.notnull(dep_delay):
            row['arr_time'] = sched_arr + timedelta(minutes=dep_delay)

    # Fix incorrect air_time values
    actual_air_time = (row['arr_time'] - row['dep_time']).total_seconds() / 60
    if not np.isclose(actual_air_time, air_time, atol=5):
        row['air_time'] = actual_air_time

    # Fix inconsistent arr_delay
    correct_arr_delay = (arr - sched_arr).total_seconds() / 60
    if not np.isclose(arr_delay, correct_arr_delay, atol=2):
        row['arr_delay'] = correct_arr_delay

    return row

flights_fixed = flights.apply(fix_flight_data, axis=1)
def check_flight_consistency(row, air_time_tolerance=5):
    sched_dep = row['sched_dep_time']
    dep = row['dep_time']
    sched_arr = row['sched_arr_time']
    arr = row['arr_time']
    air_time = row['air_time']

    # 1. Arrival must be after departure
    if arr <= dep:
        return False 

    # 2. Scheduled times check
    if sched_arr <= sched_dep:
        return False

    # 3. Air time consistency
    actual_air_time = (arr - dep).total_seconds() / 60
    if not np.isclose(actual_air_time, air_time, atol=air_time_tolerance):
        return False 

    return True 

flights_fixed['is_consistent'] = flights_fixed.apply(check_flight_consistency, axis=1)
num_inconsistent = (~flights_fixed['is_consistent']).sum()
print(f"Percentage of inconsistent flights: {num_inconsistent / len(flights) * 100:.2f}%")

#Local arrival time
airports = pd.read_csv("airports.csv")
timezone_dict = dict(zip(airports['faa'], airports['tz']))
utc_offset_to_tz = {
    -10.0: -10,
    -9.0: -9,
    -8.0: -8,
    -7.0: -7,
    -6.0: -6,
    -5.0: -5,
    -4.0: -4,
    1.0: 1,
    8.0: 8
}

def convert_timezone(value):
    try:
        value = float(value)
        return utc_offset_to_tz.get(value, None) 
    except ValueError:
        return None 
    
airports['tz_offset'] = airports['tz'].apply(convert_timezone)
airports = airports.dropna(subset=['tz_offset'])
timezone_dict = dict(zip(airports['faa'], airports['tz_offset']))
flights = flights[flights['origin'].map(timezone_dict).notnull() & flights['dest'].map(timezone_dict).notnull()]
flights['dep_offset'] = flights['origin'].map(timezone_dict)
flights['arr_offset'] = flights['dest'].map(timezone_dict)
flights['arr_time'] = pd.to_datetime(flights['arr_time'], errors='coerce')
flights['local_arr_time'] = flights['arr_time'] - pd.to_timedelta(flights['dep_offset'], unit='h') + pd.to_timedelta(flights['arr_offset'], unit='h')

print(flights[['arr_time', 'local_arr_time', 'dep_offset', 'arr_offset']].head())
# Close the database connection'
connector.close()