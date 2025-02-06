# compare states in a specified season

#kam, luo, mcandrew

import streamlit as st
import numpy as np
import pandas as pd
from epiweeks import Week
import matplotlib.pyplot as plt
import altair as alt

if __name__ == "__main__":

    #--merge ili and hosp data
    @st.cache_data
    def produce_data():
        # Set the working directory for hospital admission 
        file_path_hosp = "https://raw.githubusercontent.com/cdcepi/FluSight-forecast-hub/refs/heads/main/target-data/target-hospital-admissions.csv"

        # Set the working directory for ilidata 
        file_path_ili = "https://raw.githubusercontent.com/computationalUncertaintyLab/iliplus/refs/heads/main/ili_plus.csv"

        # Read the CSV file for ili 
        ilidata = pd.read_csv(file_path_ili)

        #cleaning offseason out of "season" column 
        ilidata = ilidata[ilidata["season"] != "offseason"]

        #removing the epiweek column 
        ilidata = ilidata.drop(columns=['epiweek'])

        #function for season week instead of epiweek 
        def ili_season_week(row):
            from epiweeks import Week

            if row.week <=20:
                start_week = Week(row.year-1,40)
            elif row.week>20:
                start_week = Week(row.year,40)

            num_weeks = 0
            row_week  = Week(row.year,row.week)
            while start_week < row_week:
                start_week = start_week+1
                num_weeks+=1
            return num_weeks

        # st.markdown ("### Cleaned ili in order of epiyear weeks")
        ilidata['season_week'] = ilidata.apply(ili_season_week, axis=1)
        ilidata                = ilidata.sort_values(by=['season', 'season_week'])

        #--add dtaret date and end date
        def add_start_and_end_date(row):
            from epiweeks import Week
            ew = Week(row.year,row.week)
            start_date = ew.startdate()
            end_date   = ew.enddate()
            row["start_date"] = start_date.strftime("%Y-%m-%d")
            row["end_date"]   = end_date.strftime("%Y-%m-%d")
            return row
        ilidata = ilidata.apply(add_start_and_end_date,1)

        hospdata = pd.read_csv(file_path_hosp)
        
        ili_plus_hosp = ilidata.merge(hospdata, left_on=['location','location_name','end_date'], right_on = ['location','location_name','date'] , how='left')
        ili_plus_hosp = ili_plus_hosp.rename(columns = {"value":"hospitalizations"})
        
        ili_plus_hosp = ili_plus_hosp.melt( id_vars = ["location","location_name","season","year","week","season_week"] , value_vars = ["ili_plus","ili_plus_a","ili_plus_b","hospitalizations"] ,  value_name="y" )

        return ili_plus_hosp
    ili_plus_hosp = produce_data()

    # Add Streamlit widgets to select states and seasons
    st.markdown("## ILI Data by State and Season")
    states          = ili_plus_hosp['location_name'].unique()  # Get the list of unique states
    selected_states = st.multiselect(label = "Select state to display charts for:"
                                     ,options = states
                                     ,default = states[0])  # Default to the first state

    # Add Streamlit widget to select seasons
    available_seasons = ili_plus_hosp['season'].unique()
    selected_seasons  = st.multiselect(
        label = "Select flu seasons to display:"
        , options = available_seasons
        , default=available_seasons
    )

    #Add widget to select the variable (hospital admissions, ili_plus, ili, or ilib)
    variables          = ['hospitalizations', 'ili_plus', 'ili_plus_a', 'ili_plus_b']
    selected_variables = st.multiselect(
        label   = "Select the data variables to display:"
        ,options = variables
        ,default = variables  # Default to all variables
    )
    
    selected_data = ili_plus_hosp.loc[ (ili_plus_hosp.location_name.isin(selected_states)) & (ili_plus_hosp.season.isin(selected_seasons)) & (ili_plus_hosp.variable.isin(selected_variables))  ]

    # Create a chart for each selected variable
    for variable in selected_variables:
        variable_data = selected_data[selected_data.variable == variable]
        chart = alt.Chart(variable_data).mark_line().encode(
            x=alt.X("season_week:O", title="Season + Week"),
            y=alt.Y("y:Q", title=variable),
            color=alt.Color("location_name:N", title="State"),
        ).properties(
            width=200,
            height=200,
        )
        
        st.altair_chart( chart )




