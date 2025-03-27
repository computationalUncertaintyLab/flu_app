
import pandas as pd 
import numpy as np 

if __name__ == "__main__":

    d             = pd.read_csv("./ili_plus_hosp.csv")
    iliplus       = d.loc[ (d.variable=="ili_plus")]
    state_iliplus = iliplus.loc[ iliplus.location_name == "Pennsylvania" ] 

    N = 13*10**6 #This is roughly the number of people in PA (will fine tune later)
    state_iliplus.to_csv("./PA_data.csv")
    
    


    
