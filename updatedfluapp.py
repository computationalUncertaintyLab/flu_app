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

#ilidf 
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
    
    st.markdown ("### Cleaned ili in order of epiyear weeks")
    cleanilidf['ili_week'] = cleanilidf.apply(ili_season_week, axis=1)
    cleanilidf = cleanilidf.sort_values(by=['season', 'ili_week'])
    st.dataframe(cleanilidf)

#fludf
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

#combining the two data frames
    # Rename columns to match for merging
    cleanilidf = cleanilidf.rename(columns={'ili_week': 'season_week'})
    cleanfludf = cleanfludf.rename(columns={'flu_season_week': 'season_week'})

    # Outer merge to preserve all ILI data, even if flu data doesn't exist for older seasons
    combined_df = pd.merge(cleanilidf, cleanfludf, on=['season', 'season_week'], how='outer')

    # Sort and display
    combined_df = combined_df.sort_values(by=['season', 'season_week'])

    # Optional: Fill missing values if needed
    # combined_df.fillna(0, inplace=True)

    st.markdown("### Combined Data (Preserving All ILI Data)")
    st.dataframe(combined_df)

#MERGE 
    # Rename columns to ensure consistency for merging
    cleanilidf.rename(columns={'ili_week': 'season_week', 'location_name': 'state', 'location': 'FIPs'}, inplace=True)
    cleanfludf.rename(columns={'flu_season_week': 'season_week', 'location_name': 'state', 'location': 'FIPs'}, inplace=True)

    # Merge the two DataFrames on season, season_week, and location_name
    merged_df = pd.merge(cleanilidf, cleanfludf, on=['season', 'season_week', 'state','FIPs'], how='outer')

    # Sort the merged DataFrame for better readability
    merged_df = merged_df.sort_values(by=['season', 'season_week', 'state','FIPs'])

    # Display the merged DataFrame in Streamlit
    st.markdown("### Merged ILI and Flu Data by Season, Week, and State")
    st.dataframe(merged_df)



  



    








