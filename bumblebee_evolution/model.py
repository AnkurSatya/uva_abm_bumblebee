## Class for the Bee evolution model.
from mesa import Model
from mesa.space import MultiGrid
from environment import *
from agents import *
import numpy as np


class BeeEvolutionModel(Model):
    def __init__(self, width, height, num_hives, nectar_units, initial_bees_per_hive, daily_steps, rng):
        """
        Args:
            width (int): width of the grid.
            height (int): height of the grid.
            num_hives (int): number of hives to be placed in the environment.
            initial_bees_per_hive (int): number of bees to be associated with a hive.
            daily_steps (int): number of steps to be run to simulate a day.
            rng: a numpy random number generator
        """
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, torus=False) #Torus should be false wrapping up the space does not make sense here.
        self.rng = rng
        
        self.num_hives = num_hives
        self.nectar_units = nectar_units

        self.initial_bees_per_hive = initial_bees_per_hive
        self.initial_bee_type_ratio = self.get_initial_bee_type_ratio()

        self.daily_steps = daily_steps

        self.hives = []
        self.flower_patches = []
        self.n_agents = 0
        self.agents = []

        self.setup_hives_and_bees()
        self.get_env_nectar_needed()
        self.setup_flower_patches()

    def get_initial_bee_type_ratio(self):
        """
        Evaluates the initial proportion of bee types for all the hives.
        """
        type_ratio = {}
        
        ratios = [self.rng.uniform(0, 1) for _ in range(3)]
        ratios = [ratio/sum(ratios) for ratio in ratios]

        for i, bee_type in enumerate([Drone, Worker, Queen]):
            type_ratio[bee_type] = ratios[i]

        return type_ratio

    def setup_hives_and_bees(self):
        """
        Creates all hives and bees. Then sets them up in the environment.
        """
        for i in range(self.num_hives):
            pos = (self.rng.integers(low=0, high=self.width), 
                   self.rng.integers(low=0, high=self.height))

            new_hive = Hive(i+1, pos, 0, [])
            self.hives.append(new_hive)
            hive_associated_bees = []

            for bee_class, ratio in self.initial_bee_type_ratio:
                num_bees_of_type = round(ratio*self.initial_bees_per_hive)

                for j in range(num_bees_of_type):
                    new_bee = self.new_agent(bee_class, new_hive, pos)
                    hive_associated_bees.append(new_bee)

            new_hive.bees = hive_associated_bees
            

    def get_env_nectar_needed(self):
        """
        Evaluates the nectar needed for the setting up the environment.
        """
        for agent in self.agents:
            if not isinstance(agent, FlowerPatch):
                self.nectar_units += agent.nectar_needed

    def setup_flower_patches(self):
        """
        Creates all the flower patches in the environment.
        """
        hives_pos = {hive.pos for hive in self.hives}
        num_cells_for_flower_patch = self.height*self.width - len(hives_pos)
        nectar_for_one_patch = self.nectar_units/num_cells_for_flower_patch

        for _ in num_cells_for_flower_patch:
            while(1):
                pos = (self.rng.randrange(self.width), self.rng.randrange(self.height))
                if pos not in hives_pos:
                    break

            cell_concents = self.grid.get_cell_list_contents([pos])
            flower_patch = [obj for obj in cell_concents if isinstance(obj, FlowerPatch)]
            if flower_patch:
                flower_patch[0].update_flower_patch(nectar_for_one_patch)
            else:
                self.new_agent(FlowerPatch, pos, nectar_for_one_patch)

    # This function is incorrect because of two reasons:
    # 1. If we want to create a new bee type agent, we need to pass more agruments to this function as needed by
    #    Bee(). 
    # 2. This function can't be used for all type of bee agents since they have different arguments requirement.
    # 3. Since this obviously can't be used for creating flower_patch agents, its name should be changed.

    # ToDo: Fix this function and wherever it is being referred to.
    # STATUS: Fixed now.
    def new_agent(self, *argv):
        '''
        Method that enables us to add agents of a given type.
        '''
        self.n_agents += 1
        
        # Create a new agent of the given type
        agent_type = argv[0]
        new_agent = agent_type(self.n_agents, self, *argv[1:])
        
        # Place the agent on the grid
        self.grid.place_agent(new_agent, new_agent.pos)
        
        # And add the agent to the model so we can track it
        self.agents.append(new_agent)

        return new_agent

    def remove_agent(self, agent):
        '''
        Removes the bee agent from the environment.
        '''
        self.n_agents -= 1

        # Remove agent from the associated hive.
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
        for agent in list(self.agents):
            agent.step()

    def run_model(self):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for _ in range(self.daily_steps):
            self.step()

    def all_agents_to_hive(self):
        """
        Move all bee agents (drones excluded) back to their hives.
        """
        for agent in list(self.agents):
            if isinstance(agent, Worker) or isinstance(agent, Queen):
                agent.pos = agent.hive.pos

    def feed_all_agents(self):
        # shuffling the agents before feeding
        self.rng.shuffle(self.agents)

        for agent in list(self.agents):
            if isinstance(agent, Worker) or isinstance(agent, Queen):
                difference = agent.nectar_needed - agent.health_level
                if agent.hive.nectar_units > difference:
                    agent.health_level += difference
                    agent.hive.nectar_units -= difference
                else:
                    agent.health_level += agent.hive.nectar_units
                    agent.hive.nectar_units = 0
                
    def new_offspring(self):
        '''
        this function will kill the starving agents and create the new ones
        '''
        for agent in list(self.agents):
            if isinstance(agent, Bee) and agent.health_level < agent.nectar_needed:
                # storing old properties
                agent_hive = agent.hive
                pos = agent.pos
                # removing old agent and creating new one with old properties
                self.remove_agent(agent)
                self.new_agent(self.rng.choice([Worker,Drone,Queen]), agent_hive, pos)

    def mutate_agents(self, alpha, beta, gamma):
        '''
        this method will mutate the agents with health level != 0,
        the agents with zero health will be killed and generated again in the new_offspring function
        '''
        coeffs = {Worker: alpha, Drone: beta, Queen: gamma}
        
        for agent in self.agents:
            if agent.health != 0:    

                # find the probabilities of choosing each bee type based on
                # encounters
                agent_probs = {}

                for bee_type, encounters in agent.encounters.items():
                    own_hive = len(encounters['own_hive'])
                    other_hive = len(encounters['other_hive'])

                    # calculating with encounter numbers instead of proportions
                    # here; probabilities are normalised later, so this approach
                    # is equivalent
                    agent_probs[bee_type] = (coeffs[bee_type]*own_hive 
                                             + (1-coeffs[bee_type])*other_hive)

                # 1. normalise into probabilities by dividing by sum
                # 2. make probabilities 'inversely' (loosely speaking) proportional
                #    to the original ones by substracting from 1 and dividing by
                #    2 to make sure they again add up to 1
                prob_sum = sum(agent_probs.values())
                agent_probs = {bee_type: (1-(prob/prob_sum))/2 for bee_type, prob in agent_probs.items()}

                # saving agent attributes
                last_resource = agent.last_resource
                agent_hive = agent.hive
                pos = agent.pos
                self.remove_agent(agent)
                # adding new agent and old properties
                new_agent = self.new_agent(
                    self.rng.choice(list(agent_probs.keys()), p=list(agent_probs.values())), 
                    agent_hive, pos)
                new_agent.last_resource = last_resource

