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

## Project Structure
In our project, we have chosen a program structure that facilitates the execution and testing of individual sub-tasks. These sub-tasks are modular components that can be independently developed and tested. Once they are verified to be working correctly, they are imported into the main dashboard. This approach allows for better organization and maintainability of the codebase, as each sub-task can be managed separately. Additionally, it enhances the overall reliability of the program by ensuring that each component is thoroughly tested before being integrated into the main application.

## Requirements
To run this script we use the dependencies in `requirements.txt`. With Python 3.12.9

<<<<<<< HEAD
To facilitate the use of this script, install the required dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

You also need the following files in the same directory as the script:

- **`airports.csv`**: Contains airport data (including location and timezone).
- **`flights_database.db`**: SQLite database containing flight records.
=======

