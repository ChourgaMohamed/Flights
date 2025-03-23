import streamlit as st
from features import bad_weather_analysis
from part3.weather_analysis import ( analyze_inner_product_and_airtime,
    prepare_data, create_improved_density_plot, create_box_plot, 
    create_scatter_plot, calculate_statistics, get_conclusion_text
)
from db import get_db_connection


# Database connection and data retrieval
db_conn = get_db_connection()

# Page title
st.subheader("Relationship between wind effect and air time")

# Run the analysis and get the data
df = analyze_inner_product_and_airtime(conn=db_conn)

# Prepare the data - now excluding neutral values
processed_df = prepare_data(df, include_neutral=False)

# Let the user select visualization type
viz_type = st.radio("Select Visualization", ("Density Plot", "Box Plot", "Scatter Plot"))

# Create the appropriate visualization based on selection
if viz_type == "Density Plot":
    fig = create_improved_density_plot(processed_df)
elif viz_type == "Box Plot":
    fig = create_box_plot(processed_df)
else:  # Scatter Plot
    fig = create_scatter_plot(processed_df)

# Display the figure
st.plotly_chart(fig)

# Calculate and display statistics
stats_df, correlation, headwind_mean, tailwind_mean, percent_diff = calculate_statistics(processed_df)

# Display statistics table
st.subheader("Air Time Statistics by Wind Condition")
st.dataframe(stats_df.set_index(stats_df.columns[0]))

# Get and display conclusion
correlation_text, conclusion = get_conclusion_text(correlation, headwind_mean, tailwind_mean, percent_diff)
st.subheader("Conclusion")
st.write(f"**{correlation_text}**")
st.write(conclusion)

st.subheader("Bad weather conditions")
# Get the bad weather data
df, fig1, fig2, text1, text2 = bad_weather_analysis.bad_weather_analysis(conn=db_conn)

# Display the data
st.plotly_chart(fig1)
st.write("Overall, departure and arrival delays show moderate correlation with each other, while weather factors exhibit weak relationships with flight delays, indicating minimal impact of weather on overall flight timing.")

st.plotly_chart(fig2)

st.text(text1 + "\n" + text2)
st.write("Bad weather shows a statistically significant but minimal impact on arrival delays, suggesting only a slight increase in delays when weather is bad.")

# Footer
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')