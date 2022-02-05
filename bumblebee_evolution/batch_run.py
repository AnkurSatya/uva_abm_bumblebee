from batchrunner import BatchRunnerMP
from model import BeeEvolutionModel
from SALib.sample import saltelli
from agents import *
import argparse
import pickle

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--seed', required=True, help='Enter your random seed. GET IT RIGHT. PLZ.')
	args = parser.parse_args()
	seed = int(args.seed)

	# We define our variables and bounds, then with a saltelli sample the we generate 512 dinstinct values for each parameter
	# the sample is in the file variable_parameters.pickle

	# problem = {
	# 	'num_vars': 3,
	# 	'names': ['forager_royal_ratio', 'growth_factor', "resource_variability"],
	# 	'bounds': [[0.0, 1.0], [0.0, 1.0], [0.0, 0.5]]
	# }

	# Set the repetitions
	replicates = 1
	
	# load preset saltelli sample of parameters
	with open("variable_parameters.pickle", "rb") as f:
		variable_parameters = pickle.load(f)

	batch = BatchRunnerMP(BeeEvolutionModel,
						fixed_parameters={"seed":seed},
						iterations=replicates,
						variable_parameters=variable_parameters,
						display_progress=True)
	batch.run_all()

  # collection of the data
	data = batch.get_collector_model()
	with open(f"results/data_{seed}.pickle", 'wb') as f:
		pickle.dump(data, f)

if __name__ == "__main__":
	main()
