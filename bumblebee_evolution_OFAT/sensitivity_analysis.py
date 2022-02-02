from SALib.sample import saltelli
from batchrunner import BatchRunnerMP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from model import BeeEvolutionModel
from agents import *

problem = {
    'num_vars': 3,
    'names': ['alpha', 'forager_royal_ratio', 'growth_factor'],
    'bounds': [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]],
    'nominal_value': [0.5, 0.5, 0.5]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 1 #10
max_steps = 400 #400
distinct_samples = 5 #40
seed = 20

# Set the outputs
model_reporters = {"Total Workers": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Worker)]),
                   "Total Queens": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Queen)]),
                   "Total Drones": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Drone)]),
                   "Total Fertilized Queens": lambda m: m.get_total_fertilized_queens()}

data = {}

for i, var in enumerate(problem['names']):
    # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
    samples = np.linspace(*problem['bounds'][i], num=distinct_samples)
    
    fixed_parameters = {}
    for j, var_ in enumerate(problem['names']):
        if j != i:
            fixed_parameters[var_] = problem['nominal_value'][j]
    fixed_parameters["seed"] = seed
    
    variable_parameters=[{var: sample} for sample in samples]
    
    batch = BatchRunnerMP(BeeEvolutionModel, 
                        fixed_parameters=fixed_parameters,
                        iterations=replicates,
                        variable_parameters=variable_parameters,
                        model_reporters=model_reporters,
                        display_progress=True)
    
    batch.run_all()
    
    data[var] = batch.get_model_vars_dataframe()
#     data[var] = batch.get_collector_model
    