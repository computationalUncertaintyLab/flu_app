# compare states in a specified season

#kam, luo, mcandrew

import streamlit as st
import numpy as np
import pandas as pd
from epiweeks import Week
import altair as alt
from produce_data import produce_data

if __name__ == "__main__":
    
    #-- Merge ILI and hospital data
    ili_plus_hosp = produce_data()

    # Add Streamlit widgets to select states and seasons
    st.markdown("## ILI Data by State and Season")
    states = ili_plus_hosp['location_name'].unique()  # Get the list of unique states
    selected_states = st.multiselect(
        label="Select state to display charts for:",
        options=states,
        default=states[0]  # Default to the first state
    )

    # Add Streamlit widget to select seasons
    available_seasons = ili_plus_hosp['season'].unique()
    selected_seasons = st.multiselect(
        label="Select flu seasons to display:",
        options=available_seasons,
        default=available_seasons
    )

    # Add widget to select the variable (hospital admissions, ili_plus, ili, or ilib)
    variables = ['hospitalizations', 'ili_plus', 'ili_plus_a', 'ili_plus_b']
    selected_variables = st.multiselect(
        label="Select the data variables to display:",
        options=variables,
        default=variables  # Default to all variables
    )
    
    selected_data = ili_plus_hosp.loc[
        (ili_plus_hosp.location_name.isin(selected_states)) & 
        (ili_plus_hosp.season.isin(selected_seasons)) & 
        (ili_plus_hosp.variable.isin(selected_variables))
    ]

    chart = alt.Chart(selected_data).mark_line(point=True).encode(
        x=alt.X("season_week:O", title="Week"),
        y=alt.Y("y:Q", title=None),
        color="location_name:N"
    ).properties(
        width=200,
        height=200
    ).facet(
        column="variable:N",
        row="season:N"
    ).resolve_scale(
        y='independent'  # Use independent scales for each y-axis
    )

    st.altair_chart(chart)
