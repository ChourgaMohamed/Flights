import sqlite3
import pandas as pd

# Path to your database
db_path = "/Users/laurensrobbe/Desktop/flights_database.db"  # Update path if needed

# Connect to the database
conn = sqlite3.connect(db_path)

# Query first 5 rows from flights table
query = "SELECT * FROM flights LIMIT 5;"
df_flights = pd.read_sql(query, conn)

# Print the first few rows
print(df_flights)

# Close connection
conn.close()