## Class for the Bee evolution model.
from mesa import Model
from mesa.space import MultiGrid
from environment import *
from agents import *
import numpy as np


class BeeEvolutionModel(Model):
    def __init__(self, width, height, num_hives, nectar_units, initial_bees_per_hive, initial_bee_type_ratio):
        """
        Args:
            width (int): width of the grid.
            height (int): height of the grid.
            num_hives (int): number of hives to be placed in the environment.
            initial_bees_per_hive (int): number of bees to be associated with a hive.
            initial_bee_type_ratio (dict): {MaleBee: 0.3, WorkerBee: 0.6, QueenBee: 0.1} 
        """
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, torus=False) #Torus should be false wrapping up the space does not make sense here.
        
        self.num_hives = num_hives
        self.nectar_units = nectar_units

        self.initial_bees_per_hive = initial_bees_per_hive
        self.initial_bee_type_ratio = initial_bee_type_ratio

        self.hives = []
        self.flower_patches = []
        self.n_agents = 0
        self.agents = []


        self.pos_flower_patch_dict = {}

        #TODO:
        # 1. Keep a dictionary which has key as a grid cell and the value as the flower patch object
        # 2. A function to return the flower patch agent at a cell

        self.setup_hives_and_bees()
        self.setup_flower_patches()

    def setup_hives_and_bees(self):
        """
        Creates all hives and bees. Then sets them up in the environment.
        """
        for i in range(self.num_hives):
            pos = None #Decide how to evaluate the position of a new hive

            hive_associated_bees = []
            tmp = self.initial_bees_per_hive
            for bee_class, ratio in self.initial_bee_type_ratio:
                num_bees_of_type = min(tmp, ratio*self.initial_bees_per_hive)
                tmp -= num_bees_of_type

                for j in range(num_bees_of_type):
                    new_bee = self.new_agent(bee_class, pos)
                    hive_associated_bees.append(new_bee)

            new_hive = Hive(i+1, pos, 0, hive_associated_bees)
            self.hives.append(new_hive)

    def setup_flower_patches(self):
        """
        Creates a flower patch and sets it up.
        """
        ## Evaluate position to set up
        ## Decide on the nectar quantity needed.
        ## Add the following (key, value) pair (pos, FlowerPatch object) to self.pos_flower_patch_dict
        pass

    def new_agent(self, agent_type, pos):
        '''
        Method that enables us to add agents of a given type.
        '''
        self.n_agents += 1
        
        # Create a new agent of the given type
        new_agent = agent_type(self.n_agents, self, pos)
        
        # Place the agent on the grid
        self.grid.place_agent(new_agent, pos)
        
        # And add the agent to the model so we can track it
        self.agents.append(new_agent)

        return new_agent
        
    def remove_agent(self, agent):
        '''
        Method that enables us to remove passed agents.
        '''
        self.n_agents -= 1
        
        # Remove agent from grid
        self.grid.remove_agent(agent)
        
        # Remove agent from model
        self.agents.remove(agent)
        # TODO:
        # create a function in environment to remove the agent from the hive
        # self.agent.hive.

    def get_flower_patch(self, pos):
        if pos in self.pos_flower_patch_dict:
            return self.pos_flower_patch_dict[pos]
        else:
            return None
        
    def step(self):
        '''
        Method that steps every agent. 
        
        Prevents applying step on new agents by creating a local list.
        '''
        for agent in list(self.agents):
            agent.step()

    def run_model(self, daily_steps):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(daily_steps):
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
                new_agent = self.new_agent(np.random.choice([Worker,Drone,Queen], p = [0.34, 0.33, 0.33]), pos)
                new_agent.hive = agent_hive

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
                new_agent = self.new_agent(np.random.choice([Worker,Drone,Queen], p = [worker_prob, drone_prob, queen_prob]), pos)
                new_agent.last_resource = last_resource
                new_agent.hive = agent_hive
