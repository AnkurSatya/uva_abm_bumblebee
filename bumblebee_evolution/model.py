## Class for the Bee evolution model.
from mesa import Model
from mesa.space import MultiGrid
from environment import *
from agents import *
import numpy as np
import random


class BeeEvolutionModel(Model):
    def __init__(self, width, height, num_hives, nectar_units, initial_bees_per_hive, daily_steps):
        """
        Args:
            width (int): width of the grid.
            height (int): height of the grid.
            num_hives (int): number of hives to be placed in the environment.
            initial_bees_per_hive (int): number of bees to be associated with a hive.
            daily_steps (int): number of steps to be run to simulate a day.
        """
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, torus=False) #Torus should be false wrapping up the space does not make sense here.
        
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
        tmp = 1.0
        for bee_type in [Drone, Worker, Queen]:
            ratio = random.uniform(0, tmp)
            ratio[bee_type] = ratio
            tmp-= ratio
        return type_ratio

    def setup_hives_and_bees(self):
        """
        Creates all hives and bees. Then sets them up in the environment.
        """
        for i in range(self.num_hives):
            pos = (self.random.randrange(self.width), self.random.randrange(self.height))

            new_hive = Hive(i+1, pos, 0, [])
            self.hives.append(new_hive)
            hive_associated_bees = []

            tmp = self.initial_bees_per_hive
            for bee_class, ratio in self.initial_bee_type_ratio:
                num_bees_of_type = min(tmp, ratio*self.initial_bees_per_hive)
                tmp -= num_bees_of_type

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
        Creates a flower patch and sets it up.
        """
        hives_pos = {hive.pos for hive in self.hives}
        num_cells_for_flower_patch = self.height*self.width - len(hives_pos)
        nectar_for_one_patch = self.nectar_units/num_cells_for_flower_patch

        for _ in num_cells_for_flower_patch:
            while(1):
                pos = (self.random.randrange(self.width), self.random.randrange(self.height))
                if pos not in hives_pos:
                    break

            cell_concents = self.grid.get_cell_list_contents([pos])
            flower_patch = [obj for obj in cell_concents if isinstance(obj, FlowerPatch)]
            if flower_patch:
                flower_patch[0].flower_patch_size += 1
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
        Method that enables us to remove passed agents.
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
        # move all the agents back to the hive
        for agent in list(self.agents):
            while agent.pos == agent.hive.pos:
                agent.back_to_hive()

    def feed_all_agents(self):
        # shuffling the agents before feeding
        self.random.shuffle(self.agents)

        for agent in list(self.agents):
            if not isinstance(agent, Drone):
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
            if agent.health_level == 0:
                # storing old properties
                agent_hive = agent.hive
                pos = agent.pos
                # removing old agent and creating new one with old properties
                self.remove_agent(agent)
                self.new_agent(np.random.choice([Worker,Drone,Queen], p = [0.34, 0.33, 0.33]), agent_hive, pos)
                # new_agent.hive = agent_hive

    def mutate_agents(self, alpha, beta, gamma):
        '''
        this method will mutate the agents with health level != 0,
        the agents with health will be killed and generated again in the new_offspring function
        '''
        for agent in self.agents:
            if agent.health != 0:    
                # initialise an array with all the agent interactions,
                # it will be [workersOfMyHive, workersOfAnother, dronesOfMyHive, dronesOfAnother, ....]
                agent_interactions = []
                for key in agent.encounters.values():
                    for set in key.values():
                        agent_interactions.append(len(set))
                # finding the probabilities 
                # TODO: improve this part
                worker_prob = (alpha * agent_interactions[0] + (1-alpha) * agent_interactions[1])/sum(agent_interactions)
                drone_prob = (beta * agent_interactions[2] + (1-beta) * agent_interactions[3])/sum(agent_interactions)
                queen_prob = (gamma * agent_interactions[4] + (1-gamma) * agent_interactions[5])/sum(agent_interactions)
                prob_sum = queen_prob + drone_prob + worker_prob
                worker_prob /= prob_sum
                drone_prob /= prob_sum
                queen_prob /= prob_sum
                # saving agent attributes
                last_resource = agent.last_resource
                agent_hive = agent.hive
                pos = agent.pos
                self.remove_agent(agent)
                # adding new agent and old properties
                new_agent = self.new_agent(np.random.choice([Worker,Drone,Queen], p = [worker_prob, drone_prob, queen_prob]), agent_hive, pos)
                new_agent.last_resource = last_resource
                # new_agent.hive = agent_hive
