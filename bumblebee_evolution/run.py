from model import BeeEvolutionModel
from agents import *
import matplotlib.pyplot as plt

alpha = 0.5
queen_coeff = 0.1
worker_coeff = 0.7

model = BeeEvolutionModel(alpha, queen_coeff, worker_coeff)
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