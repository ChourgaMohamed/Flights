# Flight Information Dashboard

## Overview
This project focuses on analyzing and visualizing flight information from a large dataset of flights departing New York City in 2023. It is divided into three main parts:
- **Data Exploration and Visualization (Part 1):**  
  Working with the `airports.csv` dataset, this section includes tasks such as mapping airport locations, identifying international versus domestic airports, plotting flight paths from NYC, and computing both Euclidean and geodesic distances between airports.
- **Version Control and Collaboration (Part 2):**  
  Setting up a GitHub repository, managing version control, and continuously updating this README as the project evolves.
- **Database Interaction and Advanced Analysis (Part 3):**  
  Connecting to a SQLite database (`flights_database.db`) containing detailed tables on airlines, flights, planes, and weather to perform complex queries and cross-referenced analysis.

## Features
- **Interactive Visualizations:**  
  Use of Plotly Express to generate maps and scatter plots showcasing global and US-specific airport data.
- **Dynamic Flight Path Mapping:**  
  Functions that plot flight paths from NYC to any given airport (or a list of airports) based on FAA abbreviations.
- **Distance Computations:**  
  Calculation of Euclidean and geodesic distances between JFK and other airports.
- **Flight Analytics:**  
  Analysis of time zones, flight frequency, delays, and airplane usage statistics.
- **Database Queries:**  
  Leveraging SQL queries via sqlite3 to join multiple tables and extract insights from a comprehensive flights database.

## Requirements
- Python 3.x
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- SQLite3 (included with Python)
