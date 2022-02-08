from model import BeeEvolutionModel
import matplotlib.pyplot as plt
from agents import *
import pickle

allData = []

for i in range(50):
    model = BeeEvolutionModel(forager_royal_ratio=0.05, growth_factor=0.05, resource_variability=0.05, seed=i)
    model.run_model()
    data = model.datacollector.get_model_vars_dataframe()
    allData.append(data)

with open(f"results/50_runs_worst_low.pickle", 'wb') as f:
		pickle.dump(allData, f)