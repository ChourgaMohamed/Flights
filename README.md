# Flight Information Dashboard

## Team members

Pepijn de Veer, Pedro Cristos Martinez, Laurens Robbe, Mohamed Chourga

## Overview
This project focuses on analyzing and visualizing flight information from a large dataset of flights departing New York City in 2023. It is divided into three main parts:
- **Data Exploration and Visualization (Part 1):**  
  Working with the `airports.csv` dataset, this section includes tasks such as mapping airport locations, identifying international versus domestic airports, plotting flight paths from NYC, and computing both Euclidean and geodesic distances between airports.
- **Version Control and Collaboration (Part 2):**  
  Setting up a GitHub repository, managing version control, and continuously updating this README as the project evolves.
- **Database Interaction and Advanced Analysis (Part 3):**  
  Connecting to a SQLite database (`flights_database.db`) containing detailed tables on airlines, flights, planes, and weather to perform complex queries and cross-referenced analysis.
- **Data Wrangling (Part 4):**
  Cleaning and optimizing data to perform more advanced cross-refecenced analysis, solving missing values and NaN values.

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
To run this script we use the following dependencies.
- Python 3.x
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- SQLite3 (included with Python)

<<<<<<< HEAD
To facilitate the use of this script, install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

You also need the following files in the same directory as the script:

- **`airports.csv`**: Contains airport data (including location and timezone).
- **`flights_database.db`**: SQLite database containing flight records.
=======


Part 4: Data Wrangling

In this section, we performed extensive data wrangling to ensure the dataset is clean, consistent, and useful for analysis. The following tasks were completed:
	•	Handling Missing Values: Checked for missing data in the flights table and resolved inconsistencies.
	•	Duplicate Removal: Identified and removed duplicate flights while ensuring no critical data was lost.
	•	Datetime Conversion: Transformed scheduled and actual departure/arrival times into datetime objects for better analysis.
	•	Flight Consistency Checks: Verified that air_time, dep_time, and sched_dep_time align correctly to prevent inconsistencies.
	•	Local Arrival Time Calculation: Added a new column that computes local arrival times considering airport time zone differences.
	•	Flight & Aircraft Type Insights: Explored different aircraft manufacturers and analyzed their role in flights departing from NYC.
	•	Weather & Delay Considerations: Conducted an initial investigation into how weather may impact flight delays.

Part 5: Interactive Dashboard (Streamlit)

We developed an interactive NYC Flight Statistics Dashboard using streamlit, allowing users to explore flight statistics dynamically.

Key Features:
	1.	General Statistics
	•	Provides a numerical summary of all flights departing from NYC.
	•	Displays a histogram of air time for better flight duration insights.
	2.	Flight Analysis
	•	Users can select departure and arrival airports to analyze specific routes.
	•	Shows details like flight number, airline, departure/arrival times.
	•	Includes a flight duration distribution graph for selected routes.
	3.	Delay Analysis
	•	Offers insights into departure delays across different flights.
	•	Displays a histogram of delay times for a better understanding of patterns.
	4.	Weather Impact Analysis (New)
	•	Investigates the relationship between weather conditions and flight delays.
	•	Helps identify how factors like wind speed and visibility affect flight performance.
