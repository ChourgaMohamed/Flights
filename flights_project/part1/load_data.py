# load_data.py
import pandas as pd
from flights_project import utils

def load_airports():
    """Load and display the first few rows of the dataset."""
    df = utils.load_airports_data()
    print(df.head())  # Display first few rows
    return df

if __name__ == "__main__":
    load_airports()