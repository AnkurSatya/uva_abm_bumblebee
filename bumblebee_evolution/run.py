from model import BeeEvolutionModel
import matplotlib.pyplot as plt
from agents import *
import pickle

'''
In the following file, multiple runs of the model are run in order to produce stats.
Each singlue run use a different seed.
'''

allData = []
number_of_runs = 50
for i in range(number_of_runs):
    model = BeeEvolutionModel(forager_royal_ratio=0.55, growth_factor=0.85, resource_variability=0.05, seed=i)
    model.run_model()
    data = model.datacollector.get_model_vars_dataframe()
    allData.append(data)

with open(f"results/50_runs_bestOverall_low.pickle", 'wb') as f:
		pickle.dump(allData, f)