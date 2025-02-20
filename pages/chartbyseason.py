import streamlit as st
import numpy as np
import pandas as pd
from epiweeks import Week
import matplotlib.pyplot as plt
import altair as alt

from produce_data import produce_data

if __name__ == "__main__":

     #--merge ili and hosp data
    ili_plus_hosp = produce_data()

#PLOT
     # Add Streamlit widgets to select states
    st.markdown("## ILI Data by Season")
    states = ili_plus_hosp['location_name'].unique()  # Get the list of unique states
    selected_states = st.multiselect("Select state to display charts for:"
                                     , states, default=states[:1])  # Default to the first state
    
    # Add Streamlit widget to select seasons
    available_seasons = ili_plus_hosp['season'].unique()
    selected_seasons = st.multiselect(
       label =  "Select flu seasons to display:", 
       options = available_seasons, 
       default=available_seasons 
    #key="season_selector"  # Unique key for season selector
    )

    #Add widget to select the variable (hospital admissions, ili_plus, ili, or ilib)
    variables          = ['hospitalizations', 'ili_plus', 'ili_plus_a', 'ili_plus_b']
    selected_variables = st.multiselect(
        label   = "Select the data variables to display:"
        ,options = variables
        ,default = variables  # Default to all variables
    )

    selected_data = ili_plus_hosp.loc[ (ili_plus_hosp.location_name.isin(selected_states)) & (ili_plus_hosp.season.isin(selected_seasons)) & (ili_plus_hosp.variable.isin(selected_variables))  ]


    def plot_location_charts(df, location, season, variable):
        location_df = df[(df['location_name'] == location) & (df['season'] == season) & (df['variable'] == variable)]
        if location_df.empty:
            return None

        return alt.Chart(location_df).mark_line(point=True).encode(
            x=alt.X('season_week:Q', title="Season Week"),
            y=alt.Y('y:Q', title=variable),
            tooltip=['season_week', 'y']
        ).properties(
            title=f"{variable}",
            width=600,
            height=200
        )

    # Iterate through selected locations, seasons, and variables
    for location in selected_states:
        st.markdown(f"### Charts for {location}")

        for season in selected_seasons:
            st.markdown(f"#### Season: {season}")

            # Create columns for variables
            cols = st.columns(len(selected_variables))

            for idx, variable in enumerate(selected_variables):
                chart = plot_location_charts(ili_plus_hosp, location, season, variable)

                if chart is not None:
                    cols[idx].altair_chart(chart, use_container_width=True)
                else:
                    cols[idx].markdown(f"No data available for {variable}")