import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

#  We could do the cleaning with a function instead of just for flights
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
def convert_times_to_datetime(df):
    try:
        df['date'] = pd.to_datetime(df[['year', 'month', 'day']])
    except KeyError as e:
        print(f"Missing required column: {e}")
    except Exception as e:
        print(f"An error occurred while combining columns to datetime: {e}")
    return df


flights = convert_times_to_datetime(flights)


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

# Local arrival time
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
flights['local_arr_time'] = flights['arr_time'] - pd.to_timedelta(flights['dep_offset'], unit='h') + pd.to_timedelta(
    flights['arr_offset'], unit='h')

print(flights[['arr_time', 'local_arr_time', 'dep_offset', 'arr_offset']].head())
# Close the database connection'


#Part4-Last 3 bullet points and futher analysis
weather = pd.read_sql_query("SELECT * FROM weather", connector)
weather = convert_times_to_datetime(weather)

# #Analyzes the effect of wind speed and precipitation on different plane types.
def analyze_weather_effect_on_planes(flights_df, weather_df):
    try:
        merged_df = pd.merge(flights_df, weather_df, on=['date', 'origin'])
    except KeyError as e:
        print(f"Merge failed. Missing column: {e}")
        return

    plane_weather = merged_df.groupby(['carrier', 'wind_speed', 'precip'])['arr_delay'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=plane_weather, x='wind_speed', y='arr_delay', hue='carrier', style='precip')
    plt.title('Effect of Wind Speed and Precipitation on Delay by Carrier')
    plt.xlabel('Wind Speed (mph)')
    plt.ylabel('Average Arrival Delay (minutes)')
    plt.legend(title='Carrier')
    plt.show()



def analyze_delays_by_airport(flights):
    airport_delays = flights.groupby(['origin'])[['dep_delay', 'arr_delay']].mean().reset_index()
    airport_delays = airport_delays.rename(
        columns={'origin': 'airport', 'dep_delay': 'avg_dep_delay', 'arr_delay': 'avg_arr_delay'})

    plt.figure(figsize=(12, 6))
    sns.barplot(data=airport_delays, x='airport', y='avg_dep_delay', color='blue', label='Departure Delay')
    sns.barplot(data=airport_delays, x='airport', y='avg_arr_delay', color='orange', label='Arrival Delay')
    plt.xlabel('Airport')
    plt.ylabel('Average Delay (minutes)')
    plt.title('Average Delays by Departure/Arrival Airports')
    plt.legend()
    plt.show()

    return airport_delays

def popular_routes_from_nyc(flights):
    nyc_airports = ['JFK', 'LGA', 'EWR']
    nyc_flights = flights[flights['origin'].isin(nyc_airports)]

    route_counts = nyc_flights.groupby(['origin', 'dest']).size().reset_index(name='flight_count')
    route_counts = route_counts.sort_values('flight_count', ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=route_counts, x='flight_count', y='dest', hue='origin', dodge=False)
    plt.xlabel('Number of Flights')
    plt.ylabel('Destination')
    plt.title('Most Frequent Routes from NYC Airports')
    plt.legend(title='Origin')
    plt.show()

    return route_counts

def weather_influence_on_delays(flights, weather):

    merged_df = pd.merge(flights, weather, on=['date', 'origin'])
    delay_weather_corr = merged_df[['dep_delay', 'arr_delay', 'temp', 'humid', 'wind_speed', 'precip']].corr()

    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=merged_df, x='wind_speed', y='dep_delay', alpha=0.5)
    plt.title('Departure Delays vs. Wind Speed')
    plt.xlabel('Wind Speed (mph)')
    plt.ylabel('Departure Delay (minutes)')
    plt.show()

    return delay_weather_corr

def frequent_carriers_from_nyc(flights):
    nyc_airports = ['JFK', 'LGA', 'EWR']
    nyc_flights = flights[flights['origin'].isin(nyc_airports)]

    carrier_counts = nyc_flights.groupby('carrier').size().reset_index(name='flight_count')
    carrier_counts = carrier_counts.sort_values('flight_count', ascending=False)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=carrier_counts, x='carrier', y='flight_count', palette='coolwarm')
    plt.xlabel('Carrier')
    plt.ylabel('Number of Flights')
    plt.title('Most Frequent Carriers from NYC Airports')
    plt.show()

    return carrier_counts

#analyze_weather_effect_on_planes(flights, weather) 
delays_by_airport = analyze_delays_by_airport(flights)
popular_routes = popular_routes_from_nyc(flights)
weather_correlation = weather_influence_on_delays(flights, weather)
carriers_from_nyc = frequent_carriers_from_nyc(flights)

print("Delays by Airport:\n", delays_by_airport)
print("Popular Routes from NYC:\n", popular_routes)
print("Correlation between Weather and Delays:\n", weather_correlation)
print("Frequent Carriers from NYC:\n", carriers_from_nyc)
