"""
Utility functions for database access, CSV data loading, and other shared operations.
"""

import sqlite3
from contextlib import contextmanager
import pandas as pd
import os
import matplotlib.colors as mcolors
import shutil
import tempfile
from flights_project.part4.part4 import clean_flights_data

# Define the path to the original database and CSV files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'flights_database.db')
AIRPORTS_CSV_PATH = os.path.join(BASE_DIR, '..', 'airports.csv')

COLOR_PALETTE = {
    "pakistan_green": "#134611",
    "india_green":    "#3E8914",
    "pigment_green":  "#3DA35D",
    "light_green":    "#96E072",
    "nyanza":         "#E8FCCF"
}

CUSTOM_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "custom_cmap", 
    [COLOR_PALETTE["nyanza"], COLOR_PALETTE["light_green"], COLOR_PALETTE["pigment_green"], COLOR_PALETTE["india_green"], COLOR_PALETTE["pakistan_green"]]
)

@contextmanager
def get_db_connection(db_path=DATABASE_PATH):
    """
    Context manager that creates a temporary copy of the database,
    cleans the flights data using that copy, and then yields the connection.
    The temporary database file is deleted after the connection is closed.
    """
    # Create a temporary file to store the copy of the database
    temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_file.close()  # Close the file so that SQLite can open it
    shutil.copy(db_path, temp_db_file.name)
    
    # Connect to the temporary copy
    conn = sqlite3.connect(temp_db_file.name, check_same_thread=False)
    try:
        # Clean the flights data on the temporary database;
        # after cleaning, the flights table will be replaced with cleaned data.
        cleaned_flights = clean_flights_data(conn, verbose=False)
        cleaned_flights.to_sql('flights', conn, if_exists='replace', index=False)
        yield conn
    finally:
        conn.close()
        os.remove(temp_db_file.name)

def execute_query(query, params=None, fetch='all', conn=None, db_path=DATABASE_PATH):
    """
    Execute a SQL query and optionally fetch results.
    If a connection is provided, it will be used (and not closed inside).
    Otherwise, a new connection is opened and closed automatically.
    """
    def _execute_with_connection(conn):
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        if fetch == 'all':
            return cursor.fetchall()
        elif fetch == 'one':
            return cursor.fetchone()
        else:
            return None

    if conn is not None:
        return _execute_with_connection(conn)
    else:
        with get_db_connection(db_path) as conn:
            return _execute_with_connection(conn)

def load_airports_data(csv_path=AIRPORTS_CSV_PATH):
    """
    Load airport data from a CSV file.
    This centralizes CSV loading for all modules.
    """
    df = pd.read_csv(csv_path)
    df["tz"] = df["tz"].astype(str).fillna("")
    return df

if __name__ == "__main__":
    # Example usage: List all tables in the database copy
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = execute_query(query, fetch='all')
    print("Tables in database:", tables)
