import streamlit as st
from part3.weather_analysis import ( analyze_inner_product_and_airtime,
    prepare_data, create_improved_density_plot, create_box_plot, 
    create_scatter_plot, calculate_statistics, get_conclusion_text
)
from db import get_db_connection


# Database connection and data retrieval
db_conn = get_db_connection()
st.title("Wind and Flight Time Analysis")
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
st.dataframe(stats_df)

# Get and display conclusion
correlation_text, conclusion = get_conclusion_text(correlation, headwind_mean, tailwind_mean, percent_diff)
st.subheader("Conclusion")
st.write(f"**{correlation_text}**")
st.write(conclusion)

# Footer
st.sidebar.markdown('''
---
Created by: M. Chourga, P. de Veer, L. Robbe, P. Martinez.
''')