import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "data/flights_database.db"

@contextmanager
def get_db_connection(db_path=DATABASE_PATH):
    """
    Context manager to handle SQLite database connections.
    Automatically commits changes and closes the connection.
    """
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

def open_connection(db_path=DATABASE_PATH):
    """Open a database connection manually."""
    return sqlite3.connect(db_path)

def close_connection(conn):
    """Close a given database connection."""
    conn.close()

def execute_query(query, params=None, fetch='all', conn=None, db_path=DATABASE_PATH):
    """
    Execute a SQL query and optionally fetch results.
    If a connection is provided, it will be used (and not closed inside).
    Otherwise, a new connection is opened and closed automatically.
    
    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters to use with the query.
        fetch (str, optional): 'all' to fetch all results, 'one' for one result, or None.
        conn (sqlite3.Connection, optional): An existing open connection.
        db_path (str, optional): Path to the SQLite database.
        
    Returns:
        The fetched results if applicable, otherwise None.
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

if __name__ == "__main__":
    # Example usage: List all tables in the database
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = execute_query(query, fetch='all')
    print("Tables in database:", tables)