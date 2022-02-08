from model import BeeEvolutionModel
import matplotlib.pyplot as plt
from agents import *
import pickle

allData = []

for i in range(50):
    model = BeeEvolutionModel(forager_royal_ratio=0.55, growth_factor=0.85, resource_variability=0.45, seed=i)
    model.run_model()
    data = model.datacollector.get_model_vars_dataframe()
    allData.append(data)

with open(f"results/50_runs_bestOverall_high.pickle", 'wb') as f:
		pickle.dump(allData, f)