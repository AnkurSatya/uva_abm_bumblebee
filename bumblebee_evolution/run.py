from model import BeeEvolutionModel
from agents import *
import numpy as np
import matplotlib.pyplot as plt

N_days = 60
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
plt.plot(data)
plt.legend()
plt.show()