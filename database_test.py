import sqlite3
import pandas as pd

# Connect to your database
db_path = "flights_database.db"
conn = sqlite3.connect(db_path)

import sqlite3
import pandas as pd

# Connect to your database
db_path = "flights_database.db"
conn = sqlite3.connect(db_path)

# Query to list all tables
tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql(tables_query, conn)
print("Tables available in the database:")
print(tables)


# Loop through each table and print its schema
for table in tables['name']:
    print(f"\nSchema for table '{table}':")
    schema_query = f"PRAGMA table_info({table});"
    schema = pd.read_sql(schema_query, conn)
    print(schema)

# Close the connection
conn.close()
