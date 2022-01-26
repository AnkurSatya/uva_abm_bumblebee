from model import BeeEvolutionModel
from agents import *
import numpy as np
import matplotlib.pyplot as plt

N_days = 20
daily_steps = 500

width = 30
height = 30

alpha = 0.5
queen_coeff = 1
worker_coeff = 10
drone_coeff = 5

coeffs = {"alpha":alpha, 
          Queen:queen_coeff,
          Worker:worker_coeff,
          Drone:drone_coeff}

num_hives = 3
initial_bees_per_hive = 3

# Initialisation of the model 
rng = np.random.default_rng(1)
model = BeeEvolutionModel(width, height, num_hives, initial_bees_per_hive, daily_steps, rng, coeffs, N_days)

# running N days
model.run_model()

data = model.datacollector.get_model_vars_dataframe()
print(data)

fig, ax = plt.subplots(nrows=2+num_hives)
data[['Total Workers', 'Total Queens', 'Total Drones']].plot(ax=ax[0])
data[['Total Fertilized Queens']].plot(ax=ax[1])
for i in range(num_hives):
    data[[f'Workers in Hive {i}', f'Queens in Hive {i}', f'Drones in Hive {i}']].plot(ax=ax[i+2])

for a in ax:
    a.grid()

plt.show()