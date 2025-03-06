#kam,luo,mcandrew


import streamlit as st

if __name__ == "__main__":

    st.set_page_config(
        page_title="Flu App",
        page_icon="🦠",
    )

    st.write("# Welcome to Flu App Dashboard! 🦠")

    st.sidebar.success("Select a chart type above.")

    st.markdown(
        """
        ## General
        - This FluApp provides visualizations for ILI+ (influenza-like illness) data and hospitalization data.
        - There are 4 different types of visualizations with different x and y axises that you can choose from to help you visualize the data you need. 
        ###### Compare states
        - This page allows you to compare data from multiple states on a single chart using a consistent scale for all data points.
        ###### Compare state (Independent y-axis)
        - This page enables you to compare data from different states on the same chart, but with each dataset using its own Y-axis scale for better visualization.
        ###### Updatedfluapp 
        - Each chart has its own independent Y-axis, but only within a single state. Data from different seasons is overlaid on the same chart for easier comparison across time.
        """
    )

    st.markdown(
        """
        ## Terms
        #### Season + week
        - Represents the epidemiological week (EpiWeek), adjusted to align with the flu season, starting from Week 40 and continuing until the end of the season. 
        """
    )
