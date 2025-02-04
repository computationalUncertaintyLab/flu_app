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


    ilidf = pd.DataFrame(ilidata)

    print(ilidf)

    st.markdown ("## ILIDATA")
    st.dataframe(ilidf)



