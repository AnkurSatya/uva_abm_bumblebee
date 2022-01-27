from batchrunner import BatchRunnerMP
from model import BeeEvolutionModel
from SALib.sample import saltelli
import pandas as pd
from agents import *

# We define our variables and bounds
problem = {
    'num_vars': 3,
    'names': ['alpha', 'forager_royal_ratio', 'growth_factor'],
    'bounds': [[0.5, 1.0], [0.0, 1.0], [0.0, 1.0]]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 1
distinct_samples = 1

# Set the outputs
model_reporters = {"Total Workers": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Worker)]),
				   "Total Queens": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Queen)]),
				   "Total Drones": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Drone)]),
				   "Total Fertilized Queens": lambda m: m.get_total_fertilized_queens()}

# We get all our samples here
param_values = saltelli.sample(problem, distinct_samples)
print(param_values)
batch = BatchRunnerMP(BeeEvolutionModel,
					  iterations=replicates,
                      variable_parameters={
						  "alpha":[row[0] for row in param_values],
						  "forager_royal_ratio":[row[1] for row in param_values],
						  "growth_factor":[row[2] for row in param_values]},
                      model_reporters=model_reporters,
					  display_progress=True)

count = 0
data = pd.DataFrame(index=range(replicates*len(param_values)), 
                                columns=['alpha', 'forager_royal_ratio', 'growth_factor'])

data['Run'], data['Total Workers'], data['Total Queens'], data['Total Drones'], data['Total Fertilized Queens'] = None, None, None, None, None

batch.run_all()

import IPython; IPython.embed()

for i in range(replicates):
    for vals in param_values: 
        # Transform to dict with parameter names and their values
        variable_parameters = {}
        for name, val in zip(problem['names'], vals):
            variable_parameters[name] = val

        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]
        iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
        data.iloc[count, 0:3] = vals
        data.iloc[count, 3:6] = iteration_data
        count += 1
        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')