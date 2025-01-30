
#kam,luo,mcandrew

import streamlit as st
import numpy as np
import pandas as pd
from epiweeks import Week
import matplotlib.pyplot as plt
import altair as alt

if __name__ == "__main__":

    # Set the working directory for hospital admission 
    file_path_hosp = "https://raw.githubusercontent.com/cdcepi/FluSight-forecast-hub/refs/heads/main/target-data/target-hospital-admissions.csv"

    # Set the working directory for ilidata 
    file_path_ili = "https://raw.githubusercontent.com/computationalUncertaintyLab/iliplus/refs/heads/main/ilidata.csv"

    # Read the CSV file for ili 
    ilidata = pd.read_csv(file_path_ili)

    # Read the CSV file
    fludata = pd.read_csv(file_path_hosp)

    # Display the first few rows of the data
    #print(fludata.head())

    # Check the data type of the 'date' column
    #print(fludata['date'].dtype)

    # Extract the year from the 'date' column and convert it to numeric
    fludata['epiyear'] = fludata['date'].str[:4].astype(int)

    # Display the first few rows of the modified data
    print(fludata[['date', 'epiyear']].head())

    # Create DataFrame
    fludf = pd.DataFrame(fludata)

    # Convert date column to datetime format
    fludf['date'] = pd.to_datetime(fludf['date'])

    # Calculate epidemiological week and year for each date
    fludf['epiweek'] = fludf['date'].apply(lambda x: Week.fromdate(x).week)
    fludf['epiyear'] = fludf['date'].apply(lambda x: Week.fromdate(x).year)

    st.title('Flu Site')

    # Define season based on epiweek and epiyear
    def get_season(row):
        epiyear = row['epiyear']
        epiweek = row['epiweek']
        if epiweek >= 40:
            return f"{epiyear}/{epiyear + 1}"
        elif 1 <= epiweek <= 20:
            return f"{epiyear - 1}/{epiyear}"
        else:
            return "off season"

    # Apply the get_season function to each row to create a new column 'season'
    fludf['season'] = fludf.apply(get_season, axis=1)

    # Display the updated DataFrame
    print(fludf)

    # st.dataframe(fludf)
    #st.markdown ("Cleaned seasons without offseason")
    cleanfludf = fludf[fludf["season"] != "off season"]
    #st.dataframe(cleanfludf)

    def flu_season_week(row):
        if row['season'] == "2021/2022":  # Special case for the first season
            if 6 <= row['epiweek'] <= 20:  # Weeks 6-20
                return row['epiweek'] # Start from 6 for week 6
            #elif row['epiweek'] >= 40:  # Weeks 40-52
                #return row['epiweek'] - 28  # Offset to place weeks 40-52 before week 0
            else:
                return None  # Ignore invalid weeks for this season
        else:  # Regular case for other seasons
            if row['epiweek'] >= 40:  # Weeks 40–52
                return row['epiweek'] - 39  # Start from 0 for week 40
            elif row['epiweek'] <= 20:  # Weeks 1–20
                return row['epiweek'] + 12  # Offset by 13 for continuity
            else:
                return None  # Ignore invalid weeks

    # st.dataframe with flu_season_week function
    st.markdown ("### Cleaned seasons in order of epiyear weeks")
    cleanfludf['flu_season_week'] = cleanfludf.apply(flu_season_week, axis=1)
    cleanfludf = cleanfludf.sort_values(by=['season', 'flu_season_week'])
    st.dataframe(cleanfludf)

    def plot_altair_chart(df, season):
        return alt.Chart(df).mark_line(point=True).encode(
            x='flu_season_week:Q',
            y='value:Q',
            tooltip=['flu_season_week', 'value']
        ).properties(
            title=f"Flu Admissions for {season}", width=600, height=400
        )

    # Plot for 2024/2025
    st.markdown("### 2024/2025 Flu Season")
    year25 = cleanfludf[cleanfludf['season'] == "2024/2025"]
    chart25 = plot_altair_chart(year25, "2024/2025")
    st.altair_chart(chart25, use_container_width=True)

    # Plot for 2023/2024
    st.markdown("### 2023/2024 Flu Season")
    year24 = cleanfludf[cleanfludf['season'] == "2023/2024"]
    chart24 = plot_altair_chart(year24, "2023/2024")
    st.altair_chart(chart24, use_container_width=True)

    # Plot for 2022/2023
    st.markdown("### 2022/2023 Flu Season")
    year23 = cleanfludf[cleanfludf['season'] == "2022/2023"]
    chart23 = plot_altair_chart(year23, "2022/2023")
    st.altair_chart(chart23, use_container_width=True)

    # Plot for 2021/2022
    st.markdown("### 2021/2022 Flu Season")
    year22 = cleanfludf[cleanfludf['season'] == "2021/2022"]
    chart22 = plot_altair_chart(year22, "2021/2022")
    st.altair_chart(chart22, use_container_width=True)


    # Add a Streamlit widget to select states (using location_name column)
    st.markdown("## Flu Admissions by State (Location Name)")
    states = cleanfludf['location_name'].unique()  # Get the list of unique states
    selected_states = st.multiselect("Select locations to display charts for:", states, default=states[:1])  # Default to the first state


    # Function to plot charts for a given state and season
    def plot_location_charts(df, location, season):
        location_df = df[(df['location_name'] == location) & (df['season'] == season)]  
        return alt.Chart(location_df).mark_line(point=True).encode(
            x=alt.X('flu_season_week:Q', title='Flu Season Week'),
            y=alt.Y('value:Q', title='Admissions'),
            tooltip=['flu_season_week', 'value']
        ).properties(
            title=f"{location} - {season}", width=600, height=400
        )

    # Iterate through selected locations
    for location in selected_states:
        st.markdown(f"### Charts for {location}")
        for season in cleanfludf['season'].unique():
            # Skip empty data
            if cleanfludf[(cleanfludf['location_name'] == location) & (cleanfludf['season'] == season)].empty:
                continue

            # Create and display the chart for the specific location and season
            chart = plot_location_charts(cleanfludf, location, season)
            st.altair_chart(chart, use_container_width=True)

    # Function to plot overlayed charts for a given location
    def plot_overlay_charts(df, location):
        # Filter data for the selected location
        location_df = df[df['location_name'] == location]

        # Create the overlayed chart
        overlay_chart = alt.Chart(location_df).mark_line(point=True).encode(
            x=alt.X('flu_season_week:Q', title='Flu Season Week'),
            y=alt.Y('value:Q', title='Admissions'),
            color=alt.Color('season:N', title='Season'),  # Differentiate seasons by color
            tooltip=['flu_season_week', 'value', 'season']  # Add season to the tooltip
        ).properties(
            title=f"{location} - Admissions Overlaid for All Seasons",
            width=800,
            height=400
        )

        return overlay_chart

    # Iterate through selected locations
    for location in selected_states:
        st.markdown(f"### Overlaid Charts for {location}")

        # Create and display the overlaid chart for the location
        chart = plot_overlay_charts(cleanfludf, location)
        st.altair_chart(chart, use_container_width=True)

    # Add a Streamlit widget to select states (using location_name column)
    st.markdown("## Flu Admissions by State and Season")
    states = cleanfludf['location_name'].unique()  # Get the list of unique states
    selected_states = st.multiselect(
        "Select locations to display charts for:", 
        states, 
        default=states[:1], 
        key="state_selector"  # Unique key for state selector
    )


    # Add a Streamlit widget to select seasons
    available_seasons = cleanfludf['season'].unique()
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
            x=alt.X('flu_season_week:Q', title='Flu Season Week'),
            y=alt.Y('value:Q', title='Admissions'),
            tooltip=['flu_season_week', 'value']
        ).properties(
            title=f"{location} - {season}", width=600, height=400
        )

    # Iterate through selected locations and seasons
    for location in selected_states:
        st.markdown(f"### Charts for {location}")
        for season in selected_seasons:
            # Skip empty data
            if cleanfludf[(cleanfludf['location_name'] == location) & (cleanfludf['season'] == season)].empty:
                continue

            # Create and display the chart for the specific location and season
            chart = plot_location_charts(cleanfludf, location, season)
            st.altair_chart(chart, use_container_width=True)

    # Function to plot overlayed charts for selected states and seasons
    def plot_overlay_states_seasons(df, states, seasons):
        # Filter data based on selected states and seasons
        filtered_df = df[(df['location_name'].isin(states)) & (df['season'].isin(seasons))]

        # Create an overlayed line chart
        overlay_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('flu_season_week:Q', title='Flu Season Week'),
            y=alt.Y('value:Q', title='Admissions'),
            color=alt.Color('location_name:N', title='State'),  # Differentiate by state
            strokeDash=alt.StrokeDash('season:N', title='Season'),  # Differentiate by season
            tooltip=['flu_season_week', 'value', 'location_name', 'season']  # Tooltip details
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
        overlay_chart = plot_overlay_states_seasons(cleanfludf, selected_states, selected_seasons)
        # Display the chart
        st.altair_chart(overlay_chart, use_container_width=True)
    else:
        st.error("Please select at least one state and one season.")

    # Combine both datasets
    #combined_df = pd.concat([cleanfludf, ili_df], ignore_index=True)

    # sorting through epiweek column from csv file ili 
    ilidata['year'] = ilidata['epiweek'].astype(str).str[:4]  # First 4 digits for the year
    ilidata['week'] = ilidata['epiweek'].astype(str).str[4:]  # last 2 digits for the week 

    # Display the first few rows of the modified data
    print(ilidata[['epiweek']].head())

    ilidf = pd.DataFrame(ilidata)

    print(ilidf)

    st.markdown ("## ILIDATA")
    st.dataframe(ilidf)
