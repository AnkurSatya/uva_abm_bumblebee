from model import BeeEvolutionModel
import matplotlib.pyplot as plt
from agents import *
import pickle

'''
In the following file, multiple runs of the model are run in order to produce stats.
Each singlue run use a different seed.
'''

allData = []
number_of_runs = 1
for i in range(number_of_runs):
    model = BeeEvolutionModel(forager_royal_ratio=0.55, growth_factor=0.85, resource_variability=0.25, seed=i, daily_data_collection=True)
    model.run_model()
    data = model.datacollector.get_model_vars_dataframe()
    allData.append(data)

fig, ax = plt.subplots(nrows=2+model.num_hives)
data[['Total Workers', 'Total Queens', 'Total Drones']].plot(ax=ax[0])
data[['Total Fertilized Queens']].plot(ax=ax[1])
for i in range(model.num_hives):
    data[[f'Workers in Hive {i}', f'Queens in Hive {i}', f'Drones in Hive {i}']].plot(ax=ax[i+2])
for a in ax:
    a.grid()
plt.show()

# with open(f"results/50_runs_bestOverall_low.pickle", 'wb') as f:
# 		pickle.dump(allData, f)