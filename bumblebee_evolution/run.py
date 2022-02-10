from model import BeeEvolutionModel
import matplotlib.pyplot as plt

'''
This script runs a single simulation and presents the results graphically.
'''

model = BeeEvolutionModel(forager_royal_ratio=0.55, growth_factor=0.85, resource_variability=0.05, seed=1, daily_data_collection=True)
model.run_model()
data = model.datacollector.get_model_vars_dataframe()

fig, ax = plt.subplots(nrows=1, ncols=2+model.num_hives, figsize=(20,4))
data[['Total Workers', 'Total Queens', 'Total Drones']].plot(ax=ax[0])
data[['Total Fertilized Queens']].plot(ax=ax[1])
for i in range(model.num_hives):
    data[[f'Workers in Hive {i}', f'Queens in Hive {i}', f'Drones in Hive {i}']].plot(ax=ax[i+2], legend=False)
    ax[i+2].set_title(f"Hive {i+1}")
    ax[i+2].legend(('Workers', 'Queens', 'Drones'))

for a in ax:
    a.set_xlabel('Days')
    a.set_ylabel('Count')
    a.grid()

plt.show()
