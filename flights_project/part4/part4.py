import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def convert_times_to_datetime(df):
    """
    Convert year, month, day columns to a datetime column
    """
    try:
        # Make sure df is a DataFrame
        if isinstance(df, list):
            column_names = ['year', 'month', 'day']  # Add all column names here
            df = pd.DataFrame(df, columns=column_names)
        
        # Create date column if necessary columns exist
        if all(col in df.columns for col in ['year', 'month', 'day']):
            df['date'] = pd.to_datetime({
                'year': df['year'],
                'month': df['month'],
                'day': df['day']
            })
    except KeyError as e:
        print(f"Missing required column: {e}")
    except Exception as e:
        print(f"An error occurred while combining columns to datetime: {e}")
    return df

def clean_flights_data(conn, verbose=False):
    """
    Clean the flights data from the database using the provided connection.
    All cleaning is performed in pandas and the cleaned DataFrame is written
    back to the temporary database so that later SQL queries operate on the cleaned data.
    """
    # Load flights data from the SQL database copy
    flights = pd.read_sql_query("SELECT * FROM flights", conn)
    # Remove NaN

    flights = flights.dropna()
    
     # Remove duplicates
    flights = flights.drop_duplicates()

    # Convert times to datetime
    flights = convert_times_to_datetime(flights)
    
    if verbose: # Calculations only done when needed
        total_rows = len(flights)
        remaining_rows = len(flights)
        deleted_rows = total_rows - remaining_rows
        percentage_deleted = (deleted_rows / total_rows) * 100
        print(f"Percentage of deleted rows: {percentage_deleted:.2f}%")
        missing_values = flights.isnull().sum()
        print("Missing values per column:\n", missing_values)
        duplicates = flights.duplicated()
        print(f"Number of duplicate flights: {duplicates.sum()}")


    for col in ['sched_dep_time', 'dep_time', 'sched_arr_time', 'arr_time']:
        flights[col] = flights[col].apply(time_to_timedelta)
        flights[col] = flights['date'] + flights[col]

    # Overnight Flights adjustments
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

    # Filter out inconsistent scheduled times
    initial_rows = len(flights)
    flights = flights[flights['sched_arr_time'] > flights['sched_dep_time']]
    removed_rows = initial_rows - len(flights)

    # Fix flight data
    flights = flights.apply(fix_flight_data, axis=1)
    flights['is_consistent'] = flights.apply(check_flight_consistency, axis=1)
    if verbose:
        num_inconsistent = (~flights['is_consistent']).sum()
        print(f"Percentage of inconsistent flights: {num_inconsistent / len(flights) * 100:.2f}%")

# Local arrival time adjustment
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
    if verbose:
        print(flights[['arr_time', 'local_arr_time', 'dep_offset', 'arr_offset']].head())
    
    # Prepare the final cleaned DataFrame.
    flights = flights.copy()
    if 'is_consistent' in flights.columns:
        flights.drop(columns=['is_consistent'], inplace=True)

    # Write the cleaned DataFrame back to the database, replacing the original flights table.
    return flights
    
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

def prepare_data_for_analysis(data, data_type):
    """
    Convert list data from SQL queries into properly formatted DataFrames
    """
    # Convert to DataFrame if it's a list
    if isinstance(data, list):
        if data_type == 'flights':
            columns = ['year', 'month', 'day', 'dep_time', 'sched_dep_time', 'dep_delay',
                      'arr_time', 'sched_arr_time', 'arr_delay', 'carrier', 'flight', 
                      'tailnum', 'origin', 'dest', 'air_time', 'distance', 'hour', 
                      'minute', 'time_hour']  
            df = pd.DataFrame(data, columns=columns)
        elif data_type == 'weather':
            columns = ['origin', 'year', 'month', 'day', 'hour', 'temp', 'dewp',
                      'humid', 'wind_dir', 'wind_speed', 'wind_gust', 'precip',
                      'pressure', 'visib', 'time_hour'] 
            df = pd.DataFrame(data, columns=columns)
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
    elif isinstance(data, pd.DataFrame):
        df = data  # Already a DataFrame
    else:
        raise TypeError(f"Data must be a DataFrame or list, not {type(data)}")
    
    # Ensure date column exists in all cases
    if all(col in df.columns for col in ['year', 'month', 'day']):
        df['date'] = pd.to_datetime({
            'year': df['year'],
            'month': df['month'],
            'day': df['day']
        })
        
    return df

if __name__ == "__main__":
    conn = sqlite3.connect("flights_database.db", check_same_thread=False)
    test = clean_flights_data(conn, False)
    print(test)