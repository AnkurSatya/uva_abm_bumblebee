from batchrunner import BatchRunnerMP
from model import BeeEvolutionModel
from agents import *
import argparse
import pickle

def main():

	"""
	This function should run the model for the global sensitivity anlysis, using the datafile
	variable_parameters.pickle.

	In that file there are all the set of parameters produced using the saltelli sample.
	When clled, this file require to enter the random seed.
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument('--seed', required=True, help='Enter your random seed.')
	args = parser.parse_args()
	seed = int(args.seed)

	
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
