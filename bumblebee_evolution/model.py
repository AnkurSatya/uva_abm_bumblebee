from mesa.time import RandomActivation, BaseScheduler
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from collections import Counter
from itertools import product
from mesa import Model
from tqdm import tqdm
from agents import *


class BeeEvolutionModel(Model):
    def __init__(self, forager_royal_ratio, growth_factor, resource_variability,
                 seed, alpha=0.5, width=25, height=25, num_hives=3,
                 initial_bees_per_hive=3,
                 daily_steps=400, N_days=30,
                 daily_data_collection=False):
        """
        Args:
            forager_royal_ratio (float): coefficient for mutation
            growth_factor (float): specifies the growth strategy of hive 
            resource_variability (float): amount of resource variability
            seed (int): random seed
            alpha (float): emphasis between encounters from different hives
            width (int): width of the grid.
            height (int): height of the grid.
            num_hives (int): number of hives to be placed in the environment.
            initial_bees_per_hive (int): number of bees to be associated with a hive.
            daily_steps (int): number of steps to be run to simulate a day.
            N_days (int): number of days to run in a simulation
            daily_data_collection (boolean): whether to collect data daily
        """
        self.daily_data_collection = daily_data_collection
        self.N_days = N_days
        self.daily_steps = daily_steps
        self.step_count = 0
        self.parameters = {"alpha":alpha,
                           "forager_royal_ratio":forager_royal_ratio,
                           "growth_factor":growth_factor}
        self.resource_variability = resource_variability
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, torus=False) # Torus should be false wrapping up the space does not make sense here.
        self.grid_locations = set(product(range(self.height), range(self.width)))
        self.current_id = 0
        self.num_hives = num_hives

        # initialise random number generator
        self.rng = np.random.default_rng(seed)

        # default scheduler, used by batch runner for step counting
        self.schedule = BaseScheduler(self) 

        # create schedules
        self.schedule_bees_and_flower_patches = RandomActivation(self)
        self.schedule_hives = BaseScheduler(self)

        # set up bees and hives
        self.initial_bees_per_hive = initial_bees_per_hive
        self.initial_bee_type_ratio = {Drone:1/3, Worker:1/3, Queen:1/3}
        self.hives = self.setup_hives_and_bees()
        self.hive_positions = [h.pos for h in self.hives]

        # create list of random moves for speed up
        self.random_move_values = list(self.rng.uniform(0, 1, size=sum([len(h.bees) for h in self.hives])*self.daily_steps))

        # set up flower patches
        self.mean_nectar_units = self.get_env_nectar_needed() * 50
        self.setup_flower_patches()

        # data collection
        self.running = True
        model_reporters = {"Total Workers": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Worker)]),
                           "Total Queens": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Queen)]),
                           "Total Drones": lambda m: len([agent for agent in m.schedule_bees_and_flower_patches.agents if isinstance(agent, Drone)]),
                           "Total Fertilized Queens": lambda m: m.get_total_fertilized_queens()}

        for hive_i, hive in enumerate(self.hives):
            for bee_type in [Worker, Queen, Drone]:
                model_reporters[f"{bee_type.__name__}s in Hive {hive_i}"] = (
                    lambda m, b=bee_type, h=hive: m.get_bees_of_each_type(b, h))

        self.datacollector = DataCollector(model_reporters=model_reporters)
        if self.daily_data_collection:
            self.datacollector.collect(self)

    def setup_hives_and_bees(self):
        """
        Creates all hives and bees. Then sets them up in the environment.
        """
        hives = []
        hive_positions = [tuple(item) for item in self.rng.choice(list(self.grid_locations), size=self.num_hives, replace=False)]

        for _, pos in enumerate(hive_positions):
            new_hive = self.create_new_agent(Hive, pos)
            hives.append(new_hive)

            # add bees to new hive
            for bee_class, ratio in self.initial_bee_type_ratio.items():
                num_bees_of_type = max(1, int(ratio*self.initial_bees_per_hive))
                for _ in range(num_bees_of_type):
                    new_bee = self.create_new_agent(bee_class, pos, new_hive)
                    new_hive.add_bee(new_bee)
        return hives

    def get_env_nectar_needed(self):
        """
        Evaluates the nectar needed for the setting up the environment.
        """
        nectar = 0
        for agent in self.schedule_bees_and_flower_patches.agents:
            if isinstance(agent, Bee):
                nectar += agent.nectar_needed
        return nectar

    def setup_flower_patches(self):
        """
        Creates all the flower patches in the environment.
        """
        # construct set of cells not occupied by hives 
        hives_pos = {hive.pos for hive in self.hives}
        possible_flower_patch_locations = list(self.grid_locations - hives_pos)

        # number of desired flower patches
        num_flower_patches = self.height*self.width - len(hives_pos)
        nectar = max(0, self.rng.normal(self.mean_nectar_units, self.resource_variability*self.mean_nectar_units))
        nectar_for_one_patch = nectar/num_flower_patches

        # dictionary of flower patches and nectar quantities
        patch_choices = [tuple(x) for x in self.rng.choice(possible_flower_patch_locations, size=num_flower_patches, replace=True)]
        flower_patches = Counter(patch_choices)

        # create FlowerPatch agents
        for pos, count in flower_patches.items():
            self.create_new_agent(FlowerPatch, pos, nectar_for_one_patch*count)
            
    def create_new_agent(self, *argv):
        '''
        Method that enables us to add agents of a given type.
        '''        
        # Create a new agent of the given type
        agent_type = argv[0]
        agent = agent_type(self.next_id(), self, *argv[1:])
        self.grid.place_agent(agent, agent.pos)
        if agent_type == Hive:
            self.schedule_hives.add(agent)
        else:
            self.schedule_bees_and_flower_patches.add(agent)
        return agent

    def remove_agent(self, agent):
        '''
        Removes an agent from the environment.

        args:
            agent (Agent): agent to remove from the environment.
        '''
        # Remove agent
        self.grid.remove_agent(agent)
        if isinstance(agent, Hive):
            self.schedule_hives.remove(agent)
        else:
            self.schedule_bees_and_flower_patches.remove(agent)

    def step(self):
        '''
        Method that steps every agent. 
        '''
        self.step_count += 1
        self.schedule_bees_and_flower_patches.step()
        
        # end of day actions
        if self.step_count % self.daily_steps == 0:
            # create new flower patches
            for agent in self.schedule_bees_and_flower_patches.agents:
                if isinstance(agent, FlowerPatch):
                    self.remove_agent(agent)
            self.setup_flower_patches()
            self.schedule_hives.step()
            if self.daily_data_collection:
                self.datacollector.collect(self)

            # generate random move values for the next day
            self.random_move_values = list(self.rng.uniform(0, 1, size=sum([len(h.bees) for h in self.hives])*self.daily_steps))
            
            # end of simulation
            if self.step_count == self.N_days*self.daily_steps:
                self.datacollector.collect(self)
                self.running = False
                return

    def run_model(self):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for _ in tqdm(range(self.N_days)): 
            for _ in range(self.daily_steps):
                self.step()

    def get_bees_of_each_type(self, bee_type, hive=None):
        """
        Get the number of bees of the given type and optionally hive.

        Args:
            bee_type (class type): type of bees
            hive (Hive): calculate bees of this hive only
        """
        if self.step_count % self.daily_steps != 0:
            return
        if hive:
            return len([bee for bee in hive.bees if isinstance(bee, bee_type)])
        else:
            return len([agent for agent in self.schedule_bees_and_flower_patches.agents if isinstance(agent, bee_type)])

    def get_total_fertilized_queens(self):
        """
        Get the number of fertilized queens
        """
        if self.step_count % self.daily_steps == 0:
            return sum([h.number_fertilized_queens for h in self.hives])