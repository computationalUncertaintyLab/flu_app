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
    file_path_ili = "https://raw.githubusercontent.com/computationalUncertaintyLab/iliplus/refs/heads/main/ili_plus.csv"
    # Read the CSV file for ili 
    ilidata = pd.read_csv(file_path_ili)

    # Read the CSV file
    fludata = pd.read_csv(file_path_hosp)

    st.set_page_config(layout='wide')

#ILIDF
    ilidf = pd.DataFrame(ilidata)
    #cleaning offseason out of "season" column 
    cleanilidf = ilidf[ilidf["season"] != "offseason"]

    #removing the epiweek column 
    cleanilidf = cleanilidf.drop(columns=['epiweek'])
    
    #function for season week instead of epiweek 
    def ili_season_week(row): #something is wrong 
        if row['week'] >= 40:
            return row['week'] - 39
        elif row ['week'] <=20:
            return row['week'] + 12  # Offset by 13 for continuity
        else:
            return None
    
    st.markdown ("### Cleaned ili in order of epiyear weeks")
    cleanilidf['ili_week'] = cleanilidf.apply(ili_season_week, axis=1)
    cleanilidf = cleanilidf.sort_values(by=['season', 'ili_week'])
    st.dataframe(cleanilidf)

#FLUDF
    fludf = pd.DataFrame(fludata)
    fludf['date'] = pd.to_datetime(fludf['date'])

    # Calculate epidemiological week and year for each date
    fludf['epiweek'] = fludf['date'].apply(lambda x: Week.fromdate(x).week)
    fludf['epiyear'] = fludf['date'].apply(lambda x: Week.fromdate(x).year)

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
    cleanfludf = fludf[fludf["season"] != "off season"]
    
    cleanfludf = cleanfludf.drop(columns=['weekly_rate'])

    def flu_season_week(row): #something is wrong 
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

#combining the two data frames --> just to check 
    # Rename columns to match for merging
    cleanilidf = cleanilidf.rename(columns={'ili_week': 'season_week', 'week':'year_week'})
    cleanfludf = cleanfludf.rename(columns={'flu_season_week': 'season_week', 'epiweek':'year_week'})

    # Outer merge to preserve all ILI data, even if flu data doesn't exist for older seasons
    combined_df = pd.merge(cleanilidf, cleanfludf, on=['season', 'season_week'], how='outer')

    # Sort and display
    combined_df = combined_df.sort_values(by=['season', 'season_week'])

    st.markdown("### Combined Data (Preserving All ILI Data)")
    st.dataframe(combined_df)

#MERGE into 1 df 
    # Rename columns to ensure consistency for merging
    cleanilidf.rename(columns={'ili_week': 'season_week', 'location_name': 'state', 'location': 'FIPs'}, inplace=True)
    cleanfludf.rename(columns={'flu_season_week': 'season_week', 'location_name': 'state', 'location': 'FIPs', 'epiyear':'year', 'value':'hosp admissions'}, inplace=True)

    # Merge the two DataFrames on season, season_week, and location_name
    merged_df = pd.merge(cleanilidf, cleanfludf, on=['season', 'season_week', 'state','FIPs','year'], how='outer')

    # Sort the merged DataFrame for better readability
    merged_df = merged_df.sort_values(by=['season', 'season_week', 'state','FIPs','year'])

    # Display the merged DataFrame in Streamlit
    st.markdown("### Merged ILI and Flu Data by Season, Week, and State")
    st.dataframe(merged_df)

#PLOT
    # Function to plot individual charts for each variable
    def plot_location_charts(df, location, season, variable):
        location_df = df[(df['state'] == location) & (df['season'] == season)]
        return alt.Chart(location_df).mark_line(point=True).encode(
            x=alt.X('season_week:Q', title="Season Week"),
            y=alt.Y(f'{variable}:Q', title=variable),
            tooltip=['season_week', variable]
        ).properties(
            title=f"{location} - {season} - {variable}", width=2000, height=400
        )

    # Add Streamlit widgets to select states, seasons, and variables
    st.markdown("## ILI Data by State and Season")
    states = merged_df['state'].unique()  # Get the list of unique states
    selected_states = st.multiselect("Select state to display charts for:", states, default=states[:1])  # Default to the first state

    # Add Streamlit widget to select seasons
    available_seasons = merged_df['season'].unique()
    selected_seasons = st.multiselect(
        "Select flu seasons to display:", 
        available_seasons, 
        default=available_seasons[:1], 
        key="season_selector"  # Unique key for season selector
    )
    
    # Add Streamlit widget to select variables
    selected_variables = st.multiselect("Select variables to display:", merged_df.columns.tolist(), default=["ili_plus","ili_plus_a","ili_plus_b","hosp admissions"])  # Default to the 4 variables

    # Iterate through selected locations, seasons, and variables
    for location in selected_states:
        st.markdown(f"### Charts for {location}")
        for season in selected_seasons:
            # Skip empty data
            if merged_df[(merged_df['state'] == location) & (merged_df['season'] == season)].empty:
                continue

            # Plot charts for each variable selected
            st.markdown(f"#### Season: {season}")
            cols = st.columns(len(selected_variables))  # Create columns for each selected variable
            
            for idx, variable in enumerate(selected_variables):
                chart = plot_location_charts(merged_df, location, season, variable)
                cols[idx].altair_chart(chart, use_container_width=True)

    
     # Function to plot overlayed charts for selected states, seasons, and variables
    """ def plot_overlay_states_seasons(df, states, seasons, variables):
        # Filter data based on selected states, seasons, and variables
        filtered_df = df[(df['state'].isin(states)) & (df['season'].isin(seasons))]

        # Start with the first variable for overlayed chart
        overlay_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('season_week:Q', title='ILI Week'),
            y=alt.Y('ili_plus:Q', title='ILI Plus data'),  # Default y-axis for initial display
            color=alt.Color('state:N', title='State'),  # Differentiate by state
            strokeDash=alt.StrokeDash('season:N', title='Season'),  # Differentiate by season
            tooltip=['season_week', 'ili_plus', 'state', 'season']  # Tooltip details
        ).properties(
            title="Overlayed Admissions for Selected States and Seasons",
            width=800,
            height=400
        )

        # If there are multiple variables, overlay them
        for variable in variables:
            overlay_chart = overlay_chart.encode(
                y=alt.Y(f'{variable}:Q', title=variable)  # Dynamically change the y-axis based on variable
            )

        return overlay_chart
    
    # Check if selections are valid for overlay chart
    if selected_states and selected_seasons and selected_variables:
        st.markdown('## Overlay chart by state and season')
        overlay_chart = plot_overlay_states_seasons(merged_df, selected_states, selected_seasons, selected_variables)
        st.altair_chart(overlay_chart, use_container_width=True)
    else:
        st.error("Please select at least one state, one season, and one variable.")
 """