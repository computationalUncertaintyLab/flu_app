#kam,luo,mcandrew


import streamlit as st

if __name__ == "__main__":

    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Welcome to Streamlit! 👋")

    st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        Streamlit is an open-source app framework built specifically for
        Machine Learning and Data Science projects.
        **👈 Select a demo from the sidebar** to see some examples
        of what Streamlit can do!
        ### Compare state
        - On this page, you can compare the data for different states on the same chart with the same scale for all data. 
        ### Compare state indpt y
        - On this page, you can compare the data for different states on the same chart.
        """
    )
