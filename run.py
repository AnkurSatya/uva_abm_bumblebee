from mesa import Model
from mesa.space import MultiGrid
from bumblebee_evolution.environment import *
from bumblebee_evolution.agents import *
from bumblebee_evolution.model import *

# Initialise the environment
N_days = 90
alpha = 1
beta = 1
gamma = 1
width = 10
height = 10
num_hives = 10
nectar_units = 10
initial_bees_per_hive = 10
daily_steps = 10

rng = np.random.default_rng(0)

# Initialisation of the model 
model = BeeEvolutionModel(width, height, num_hives, nectar_units, initial_bees_per_hive, daily_steps, rng)

# running N days
for i in range(N_days):
   
    '''
    when the day is over
    '''
  
    model.run_model()
    model.all_agents_to_hive()
    model.feed_all_agents()
    model.mutate_agents(alpha,beta,gamma)
    model.new_offspring()

 
