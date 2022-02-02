from batchrunner import BatchRunnerMP
from model import BeeEvolutionModel
from SALib.sample import saltelli
from agents import *
import argparse
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('--seed', required=True, help='Enter your random seed. GET IT RIGHT. PLZ.')
args = parser.parse_args()
seed = int(args.seed)

# We define our variables and bounds
problem = {
    'num_vars': 3,
    'names': ['forager_royal_ratio', 'growth_factor', "resource_variability"],
    'bounds': [[0.0, 1.0], [0.0, 1.0], [0.0, 0.5]]
}

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 1
distinct_samples = 512

# We get all our samples here
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=False)

tuples = set()
for i in range(len(param_values)):
	tuples.add(tuple(param_values[i]))
print(f"Running {replicates} replicate(s) for {len(tuples)} unique parameter combinations")

variable_parameters = [
	{"forager_royal_ratio":param_values[i][0], 
	 "growth_factor":param_values[i][1], 
	 "resource_variability":param_values[i][2]}
	 for i in range(len(param_values))
]

# variable_parameters = {"alpha":list(set([row[0] for row in param_values])),
# 					   "forager_royal_ratio":list(set([row[1] for row in param_values])),
# 					   "growth_factor":list(set([row[2] for row in param_values]))}


if __name__ == '__main__':
        batch = BatchRunnerMP(BeeEvolutionModel,
                                                  fixed_parameters={"seed":seed},
                                                  iterations=replicates,
                              variable_parameters=variable_parameters,
                                                  display_progress=True)
        batch.run_all()

        data = batch.get_collector_model()
        with open(f"results/data_{seed}.pickle", 'wb') as f:
                pickle.dump(data, f)
