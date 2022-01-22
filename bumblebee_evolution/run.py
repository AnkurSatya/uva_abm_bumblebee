from model import BeeEvolutionModel
import numpy as np

N_days = 20
daily_steps = 20

width = 50
height = 50

alpha = 1
beta = 1
gamma = 1

num_hives = 2
initial_bees_per_hive = 50
nectar_units = 10

# Initialisation of the model 
rng = np.random.default_rng(1)
model = BeeEvolutionModel(width, height, num_hives, nectar_units, initial_bees_per_hive, daily_steps, rng, alpha, beta, gamma, N_days)

# running N days
model.run_model()