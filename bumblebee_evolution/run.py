from model import BeeEvolutionModel
import numpy as np
import matplotlib.pyplot as plt
import time

N_days = 10
daily_steps = 1000

width = 50
height = 50

alpha = 0.8
beta = 0.2
gamma = 0.2

num_hives = 4
initial_bees_per_hive = 50
nectar_units = 10

# Initialisation of the model 
rng = np.random.default_rng(1)
model = BeeEvolutionModel(width, height, num_hives, initial_bees_per_hive, daily_steps, rng, alpha, beta, gamma, N_days)

# running N days
start = time.time()
model.run_model()
end = time.time()
print((end-start)/60)
data = model.datacollector.get_model_vars_dataframe()
print(data)
'''plt.plot(data)
plt.legend()
plt.show()'''