 #kam,luo,mcandrew

import streamlit as st 
import numpy as np
import pandas as pd
from epiweeks import Week
import matplotlib.pyplot as plt
import altair as alt

if __name__ == "__main__":

    #Set working directory for flu data
    file_path_hosp = "https://raw.githubusercontent.com/cdcepi/FluSight-forecast-hub/refs/heads/main/target-data/target-hospital-admissions.csv"

    #Set working directory for ili plus data
    file_path_iliplus = "https://raw.githubusercontent.com/computationalUncertaintyLab/iliplus/refs/heads/main/ili_plus.csv"

    # Read the CSV file for ili 
    ilidata = pd.read_csv(file_path_iliplus)

    # Read the CSV file
    fludata = pd.read_csv(file_path_hosp)

    #making it a dataframe 
    ilidf = pd.DataFrame(ilidata)
    #cleaning offseason out of "season" column 
    cleanilidf = ilidf[ilidf["season"] != "offseason"]

    cleanilidf = cleanilidf.drop(columns=['epiweek'])
    
    def ili_season_week(row):
        if row['week'] >= 40:
            return row['week'] - 39
        elif row ['week'] <=20:
            return row['week'] + 12  # Offset by 13 for continuity
        else:
            return None
            
    st.markdown ("## ILIDATA")
    st.dataframe(ilidf)

    st.markdown ("## cleaned ili data")
    st.dataframe (cleanilidf)

    # st.dataframe with ili_season_week function
    st.markdown ("### Cleaned ili in order of epiyear weeks")
    cleanilidf['ili_week'] = cleanilidf.apply(ili_season_week, axis=1)
    cleanilidf = cleanilidf.sort_values(by=['season', 'ili_week'])
    st.dataframe(cleanilidf)

    def plot_altair_chart(df, season):
        return alt.Chart(df).mark_line(point=True).encode(
            x='ili_week:Q',
            y='ili_plus:Q',
            tooltip=['ili_week', 'ili_plus']
        ).properties(
            title=f"ILI data for {season}", width=600, height=400
        )
    # Add a Streamlit widget to select states (using location_name column)
    st.markdown("## ILI Data by State and Season")
    states = cleanilidf['location_name'].unique()  # Get the list of unique states
    selected_states = st.multiselect("Select locations to display charts for:", states, default=states[:1])  # Default to the first state

    # Add a Streamlit widget to select seasons
    available_seasons = cleanilidf['season'].unique()
    selected_seasons = st.multiselect(
        "Select flu seasons to display:", 
        available_seasons, 
        default=available_seasons, 
        key="season_selector"  # Unique key for season selector
    )

    # Function to plot charts for a given state and season
    def plot_location_charts(df, location, season):
        location_df = df[(df['location_name'] == location) & (df['season'] == season)]
        return alt.Chart(location_df).mark_line(point=True).encode(
            x=alt.X('ili_week:Q', title="ILI DATA"),
            y=alt.Y('ili_plus:Q', title='ILI Plus Data'),
            tooltip=['ili_week', 'ili_plus']
        ).properties(
            title=f"{location} - {season}", width=600, height=400
        )

    # Iterate through selected locations and seasons
    for location in selected_states:
        st.markdown(f"### Charts for {location}")
        for season in selected_seasons:
            # Skip empty data
            if cleanilidf[(cleanilidf['location_name'] == location) & (cleanilidf['season'] == season)].empty:
                continue

            # Create and display the chart for the specific location and season
            #chart = plot_location_charts(cleanilidf, location, season)
            #st.altair_chart(chart, use_container_width=True)

    # Function to plot overlayed charts for selected states and seasons
    def plot_overlay_states_seasons(df, states, seasons):
        # Filter data based on selected states and seasons
        filtered_df = df[(df['location_name'].isin(states)) & (df['season'].isin(seasons))]

        # Create an overlayed line chart
        overlay_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('ili_week:Q', title='ILI Week'),
            y=alt.Y('ili_plus:Q', title='ILI Plus data'),
            color=alt.Color('location_name:N', title='State'),  # Differentiate by state
            strokeDash=alt.StrokeDash('season:N', title='Season'),  # Differentiate by season
            tooltip=['ili_week', 'ili_plus', 'location_name', 'season']  # Tooltip details
        ).properties(
            title="Admissions Overlayed for Selected States and Seasons",
            width=800,
            height=400
        )

        return overlay_chart

    # Check if selections are valid
    if selected_states and selected_seasons:
        st.markdown('## Overlay chart by state and season')
        # Generate the overlayed chart
        overlay_chart = plot_overlay_states_seasons(cleanilidf, selected_states, selected_seasons)
        # Display the chart
        st.altair_chart(overlay_chart, use_container_width=True)
    else:
        st.error("Please select at least one state and one season.")





