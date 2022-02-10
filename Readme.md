The bumblebee_evolution folder contains the code for the project of group 16, for the Agent Based Modelling course in the University of Amsterdam.
The goal of the project is to study, using an agent based model, the reproductive succes of the bumblebees, in the scenario in which they are able to switch role at the end of the day.

In particular every bee will take account of the encountered bees during the day (from both its hive and the other hives).

In the code, 4 parameters are crucial:

1. the ratio between workers and males/queens (so-called "forager_royal_ratio")
2. the weight that a bee gives to the bee of its own hive (so-called "alpha")
3. the percentage of nectar used at the end of the day to create new offspring (so-called "growth_factor")
4. the resource variability in the environment
   Moreover, it's possible to change other variables in the code, such as the grid-size, the time-steps or the number of hives. As
   well as the total amount of nectar in the environment and its variability in the simulation.

## Code instructions:

The code is structured as follow:

**agents.py** : all the entities of the model are defined here (bees, hives and flower patches).

**batch_run.py** : in this file the model is executed for multiple values of the parameters (in variable_parameters.pickle)
sampled using the Saltelli sample in order to perform the global sensitivity analysis.

**batchrunner.py** : imported file from MESA library, with changes in line 404 in order to import the set of parameters from the saltelli sample, and to parallelize the code.

**model.py** : the logic of model is defined in this file.

**run.py** : here the model can be executed for just one "season".

**sensitivity_analysis.ipynb** : OFAT sensitivity analysis.

**results/Global Sensitivity Analysis.ipynb** : global sensitivity analysis.

**visualisation.py** : running this file it's possible to visualise the behaviour of the model.

To download the very latest source, run:

`git clone https://github.com/AnkurSatya/uva_abm_bumblebee.git`

Before running any code, make sure the required packages are installed:

`pip install -r requirements.txt`
