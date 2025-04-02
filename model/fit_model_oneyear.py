import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import minimize

d = pd.read_csv("PA_data.csv")

# The year to fit the model for
year = 2017

# Filter the data for the specified year
data = d[d['year'] == year][['week', 'y']]
data.columns = ['times', 'infections']

# Parameters
n = 1000  # Number of people in the system

# SIR differential equations
def sir(t,y, beta, gamma,n):
    s,i, r, c = y
    ds_dt = -beta*s*i/n
    di_dt = beta*s*i/n - gamma*i
    dr_dt = gamma*i
    
    dc_dt = beta*s*i/n            #--incident cases (why?)
    return [ds_dt, di_dt, dr_dt, dc_dt]

# SSE function
def SSE(params, data, n):
    beta, gamma = params
    initial_conditions = (999., 1., 0., 0)
    start = min(data.times)
    end = max(data.times)

    solution = solve_ivp( fun = sir
                     , t_span = (start,end)
                     , y0     = initial_conditions
                     , t_eval = data.times.values  #<--evaluate our solution at all the x values we have in the data
                     , args   = (beta, gamma,n))
    
    prevalent_infections = solution.y[1, :]
    return np.mean( (prevalent_infections - data.infections.values)**2 ) #--Compute the SSE

# Minimize SSE
results = minimize( lambda x: SSE(x,data=data,n=1000), x0=np.array([2,1])  )

# Parameters
beta, gamma = results.x
initial_conditions = (999., 1., 0., 0)

solution = solve_ivp( fun = sir
                     , t_span = (min(data.times),max(data.times))
                     , y0     = initial_conditions
                     , t_eval = data.times.values  #<--evaluate our solution at all the x values we have in the data
                     , args   = (beta, gamma,n))

# Plot
prevalent_infections = solution.y[1, :]
week_labels = np.arange(1, len(data.times) + 1)

plt.scatter(week_labels, data.infections.values, s=5, label='Data')
plt.plot(week_labels, prevalent_infections)
plt.xlabel('week')
plt.ylabel('iliplus')
plt.show()
