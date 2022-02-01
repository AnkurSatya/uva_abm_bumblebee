from model import BeeEvolutionModel
import matplotlib.pyplot as plt
from agents import *

model = BeeEvolutionModel(alpha=0.5, forager_royal_ratio=0.2, growth_factor=0.5, seed=0)
model.run_model()
data = model.datacollector.get_model_vars_dataframe()
print(data)

fig, ax = plt.subplots(nrows=2+model.num_hives)
data[['Total Workers', 'Total Queens', 'Total Drones']].plot(ax=ax[0])
data[['Total Fertilized Queens']].plot(ax=ax[1])
for i in range(model.num_hives):
    data[[f'Workers in Hive {i}', f'Queens in Hive {i}', f'Drones in Hive {i}']].plot(ax=ax[i+2])
for a in ax:
    a.grid()
plt.show()