## Class for the Bee evolution model.
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from collections import Counter
from itertools import product
from mesa import Model
from agents import *
    

class BeeEvolutionModel(Model):
    def __init__(self, width, height, num_hives, initial_bees_per_hive, daily_steps, rng, coefficients, N_days):
        """
        Args:
            width (int): width of the grid.
            height (int): height of the grid.
            num_hives (int): number of hives to be placed in the environment.
            initial_bees_per_hive (int): number of bees to be associated with a hive.
            daily_steps (int): number of steps to be run to simulate a day.
            rng: a numpy random number generator
        """
        self.running = True
        self.N_days = N_days
        self.coefficients = coefficients
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, torus=False) # Torus should be false wrapping up the space does not make sense here.
        self.rng = rng
        self.grid_locations = set(product(range(self.height), range(self.width)))
        
        self.num_hives = num_hives

        self.initial_bees_per_hive = initial_bees_per_hive
        self.initial_bee_type_ratio = self.get_initial_bee_type_ratio()

        self.daily_steps = daily_steps

        self.hives = []
        self.flower_patches = []
        self.n_agents = 0
        self.agents = []

        self.setup_hives_and_bees()
        self.nectar_units = self.get_env_nectar_needed() * 10 # TODO : 50 is multiplicative factor for carrying capacity of env w.r.t. initial population sizes
        self.setup_flower_patches()

        self.step_count = 0
        self.n_days_passed = 0

        # Data collection #
        model_reporters={"Total Workers": lambda m: m.get_bees_of_each_type(Worker),
                         "Total Queens": lambda m: m.get_bees_of_each_type(Queen),
                         "Total Drones": lambda m: m.get_bees_of_each_type(Drone),
                         "Total Fertilized Queens": lambda m: m.get_total_fertilized_queens()}

        for hive_i, hive in enumerate(self.hives):
            for bee_type in [Worker, Queen, Drone]:
                model_reporters[f"{bee_type.__name__}s in Hive {hive_i}"] = (
                    lambda m, b=bee_type, h=hive: m.get_bees_of_each_type(b, h))

        self.datacollector = DataCollector(model_reporters=model_reporters)
        self.datacollector.collect(self)

    def get_initial_bee_type_ratio(self):
        """
        Evaluates the initial proportion of bee types for all the hives.
        """
        ratios = self.rng.uniform(0, 1, size=3)
        ratios /= sum(ratios)
        return {Drone:ratios[0], Worker:ratios[1], Queen:ratios[2]}

    def setup_hives_and_bees(self):
        """
        Creates all hives and bees. Then sets them up in the environment.
        """
        hive_positions = [tuple(item) for item in self.rng.choice(list(self.grid_locations), size=self.num_hives, replace=False)]
        for _, pos in enumerate(hive_positions):

            new_hive = self.create_new_agent(Hive, pos, 0)
            self.hives.append(new_hive)

            # add bees to new hive
            for bee_class, ratio in self.initial_bee_type_ratio.items():
                num_bees_of_type = max(1, int(ratio*self.initial_bees_per_hive))
                for _ in range(num_bees_of_type):
                    new_bee = self.create_new_agent(bee_class, pos, new_hive)
                    new_hive.add_bee(new_bee)
            
    def get_env_nectar_needed(self):
        """
        Evaluates the nectar needed for the setting up the environment.
        """
        nectar = 0
        for agent in self.agents:
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
        nectar_for_one_patch = self.nectar_units/num_flower_patches

        # dictionary of flower patches and nectar quantities
        patch_choices = [tuple(x) for x in self.rng.choice(possible_flower_patch_locations, size=num_flower_patches, replace=True)]
        flower_patches = Counter(patch_choices)

        # create FlowerPatch agents
        for pos, count in flower_patches.items():
            self.create_new_agent(FlowerPatch, pos, nectar_for_one_patch*count)

    # This function is incorrect because of two reasons:
    # 1. If we want to create a new bee type agent, we need to pass more agruments to this function as needed by
    #    Bee(). 
    # 2. This function can't be used for all type of bee agents since they have different arguments requirement.
    # 3. Since this obviously can't be used for creating flower_patch agents, its name should be changed.

    # ToDo: Fix this function and wherever it is being referred to.
    # STATUS: Fixed now.
    def create_new_agent(self, *argv):
        '''
        Method that enables us to add agents of a given type.
        '''
        self.n_agents += 1
        
        # Create a new agent of the given type
        agent_type = argv[0]
        agent = agent_type(self.n_agents, self, *argv[1:])
        
        # Place the agent on the grid
        self.grid.place_agent(agent, agent.pos)

        # And add the agent to the model so we can track it
        self.agents.append(agent)

        return agent

    def remove_agent(self, agent):
        '''
        Removes an agent from the environment.
        '''
        self.n_agents -= 1

        # Remove agent from the hive if agent is a bee
        if isinstance(agent, Bee):
            agent.hive.remove_bee(agent)
        
        # Remove agent from grid
        self.grid.remove_agent(agent)

        # Remove agent from model
        self.agents.remove(agent)

    def step(self):
        '''
        Method that steps every agent. 
        Prevents applying step on new agents by creating a local list.
        '''
        self.step_count += 1
        agent_list = list(self.agents)
        self.rng.shuffle(agent_list)
        for agent in agent_list:
            if agent.pos and not isinstance(agent, Hive):
                agent.step()
        for hive in self.hives:
            hive.step()

        if self.step_count % self.daily_steps == 0:
            self.n_days_passed += 1

        self.datacollector.collect(self)

    def run_model(self):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for _ in range(self.N_days):
            for _ in range(self.daily_steps):
                self.step()

    def get_bees_of_each_type(self, bee_type, hive=None):
        """
        Get the number of bees of the given type and optionally hive.
        """
        if self.step_count % self.daily_steps != 0:
            return
        if hive:
            return len([bee for bee in hive.bees if isinstance(bee, bee_type)])
        else:
            return len([agent for agent in self.agents if isinstance(agent, bee_type)])

    def get_total_fertilized_queens(self):
        if self.step_count % self.daily_steps == 0:
            return sum([h.number_fertilized_queens for h in self.hives])