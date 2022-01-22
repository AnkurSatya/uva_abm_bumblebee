## Class for the Bee evolution model.
from mesa.space import MultiGrid
from collections import Counter
from itertools import product
from mesa import Model
from environment import *
from agents import *


class BeeEvolutionModel(Model):
    def __init__(self, width, height, num_hives, nectar_units, initial_bees_per_hive, daily_steps, rng, alpha, beta, gamma, N_days):
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
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, torus=False) #Torus should be false wrapping up the space does not make sense here.
        self.rng = rng
        self.grid_locations = set(product(range(self.height), range(self.width)))
        
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
        # self.schedule = RandomActivation(self)

    def get_initial_bee_type_ratio(self):
        """
        Evaluates the initial proportion of bee types for all the hives.
        """
        type_ratio = {}
        ratios = self.rng.uniform(0, 1, size=3)
        ratios /= sum(ratios)
        for i, bee_type in enumerate([Drone, Worker, Queen]):
            type_ratio[bee_type] = ratios[i]
        return type_ratio

    def setup_hives_and_bees(self):
        """
        Creates all hives and bees. Then sets them up in the environment.
        """
        hive_positions = [tuple(item) for item in self.rng.choice(list(self.grid_locations), size=self.num_hives, replace=False)]
        for i, pos in enumerate(hive_positions):
            new_hive = Hive(i+1, pos, 0)
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
        for agent in self.agents:
            if not isinstance(agent, FlowerPatch):
                self.nectar_units += agent.nectar_needed

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
        # if isinstance(agent,Bee):
        #     self.schedule.add(agent)
        
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

        # if isinstance(agent,Bee):
        #     self.schedule.remove(agent)
        # Remove agent from model
        self.agents.remove(agent)
        
    def step(self):
        '''
        Method that steps every agent. 
        
        Prevents applying step on new agents by creating a local list.
        '''
        #self.schedule.step()
        agent_list = list(self.agents)
        self.rng.shuffle(agent_list)
        for agent in agent_list:
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
                self.grid.place_agent(agent, agent.hive.pos)

    def feed_all_agents(self):
        # shuffling the agents before feeding
        for hive in self.hives:
            # get non-drone bees for the hive
            bees = [b for b in hive.bees if not isinstance(b, Drone)]
            self.rng.shuffle(bees)
            for b in bees:
                difference = b.nectar_needed - b.health_level
                if hive.nectar_units > difference:
                    b.health_level = b.nectar_needed
                    hive.nectar_units -= difference
        
    def new_offspring(self):
        '''
        this function will kill the starving agents and create the new ones
        '''
        for agent in list(self.agents):
            if isinstance(agent, Bee) and agent.health_level < agent.nectar_needed:
                # create new agent and remove old one
                new_agent = self.create_new_agent(self.rng.choice([Worker,Drone,Queen]), agent.pos, agent.hive)
                agent.hive.add_bee(new_agent)
                self.remove_agent(agent)

    def mutate_agents(self):
        '''
        this method will mutate the agents with health level != nectar_needed,
        the agents with health != nectar_needed will be killed and generated again in the new_offspring function
        '''
        coeffs = {Worker: self.alpha, Drone: self.beta, Queen: self.gamma}
        
        for agent in self.agents:
            # entering in the mutation process only if the bee has been feed.
            if isinstance(agent, Bee) and agent.health_level == agent.nectar_needed:    

                # find the probabilities of choosing each bee type based onencounters
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
                # there were no encounters, so avoid mutating
                if prob_sum == 0:
                    return

                agent_probs = {bee_type: (1-(prob/prob_sum))/2 for bee_type, prob in agent_probs.items()}

                # add new agent and remove old one
                new_agent = self.create_new_agent(
                    self.rng.choice(list(agent_probs.keys()),
                    p=list(agent_probs.values())), agent.pos, agent.hive)
                new_agent.last_resource = agent.last_resource
                agent.hive.add_bee(new_agent)
                self.remove_agent(agent)

    def run_multiple_days(self):
        # running N days
        for i in range(self.N_days):
            self.run_model()
            self.all_agents_to_hive()
            self.feed_all_agents()
            self.mutate_agents()
            self.new_offspring()

