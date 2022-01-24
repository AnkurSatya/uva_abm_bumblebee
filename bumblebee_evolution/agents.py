from environment import *
from mesa import Agent
import numpy as np


class Bee(Agent):
	def __init__(self, unique_id, model, pos, hive, nectar_needed):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			pos (tuple(int, int)): The position of the bee in the environment.
			hive (Hive): the original hive of the bee
			nectar_needed (int): nectar needed per day
		"""
		super().__init__(unique_id, model)

		self.hive = hive
		self.pos = pos
		self.nectar_needed = nectar_needed
		self.health_level = 0 # health is empty upon initialization
		self.isCollecting = False
		self.last_resource = None
		self.encounters = {
			Worker:{"own_hive":set(), "other_hive":set()},
			Drone:{"own_hive":set(), "other_hive":set()},
			Queen:{"own_hive":set(), "other_hive":set()}
		}

	def update_encounters(self):
		# self.pos contains int64 objects which mesa doesn't like, so we need to cast to int *sigh*
		cell_contents = self.model.grid.get_cell_list_contents((int(self.pos[0]), int(self.pos[1])))
		cell_contents.remove(self)
		for item in cell_contents:
			if isinstance(item, Bee):
				# check if bees originate from same hive
				if item.hive == self.hive:
					hive_category = "own_hive"
				else:
					hive_category = "other_hive"
				# adjust self encounters dictionary
				self.encounters[item.bee_type][hive_category].add(item.unique_id)
				# adjust other bee's encounters dictionary
				item.encounters[self.bee_type][hive_category].add(self.unique_id)

	def random_move(self):
		'''
		This method should get the neighbouring cells (Moore's neighbourhood), select one, and move the agent to this cell.
		'''
		try:
			neighbouring_cells = self.model.grid.get_neighborhood(self.pos, moore=True)
		except:
			import IPython; IPython.embed()
		if self.hive.pos in neighbouring_cells:
			neighbouring_cells.remove(self.hive.pos)

		# selecting new positiom
		new_pos = self.model.rng.choice(self.model.grid.get_neighborhood(self.pos, moore=True))

		# moving the agent to the new position
		self.model.grid.move_agent(self, tuple(new_pos))
		self.update_encounters()

	def check_cell_for_nectar(self, threshold=10): # TODO : update threshold value?
		'''
		This method should check if the cell is good enough to start collecting food.
		'''
		# content of the cell in the current position
		cell_concents = self.model.grid.get_cell_list_contents((int(self.pos[0]), int(self.pos[1])))
		flower_patch = [obj for obj in cell_concents if isinstance(obj, FlowerPatch)]
		if flower_patch and flower_patch[0].nectar_units > threshold:
			return flower_patch[0]
		else:
			return False

	def collect(self, flower_patch):
		'''
		This method should collect the nectar from the cell.
		'''
		amount_to_withdraw = min(self.nectar_needed - self.health_level, flower_patch.nectar_units)
		self.health_level += amount_to_withdraw
		flower_patch.withdraw_nectar(amount_to_withdraw)
		self.isCollecting = True

	def move_towards_hive(self):
		difference =  np.array(self.hive.pos) - np.array(self.pos)
		self.model.grid.move_agent(self, (self.pos[0]+np.sign(difference[0]), self.pos[1]+np.sign(difference[1])))
		if self.pos != self.hive.pos: # TODO : shouldn't count the hive members, right?
			self.update_encounters()

	def move_towards_resource(self):
		difference =  np.array(self.last_resource) - np.array(self.pos)
		self.model.grid.move_agent(self, (self.pos[0] + np.sign(difference[0]), self.pos[1] + np.sign(difference[1])))
		self.update_encounters()


class Worker(Bee):
	def __init__(self, unique_id, model, pos, hive, nectar_needed=236):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			pos (tuple(int, int)): The position of the bee in the environment.
			hive (Hive): the original hive of the bee
			nectar_needed (int): amount of nectar needed per day
		"""
		super().__init__(unique_id, model, pos, hive, nectar_needed)

		self.max_nectar = 44  # bumble bees carry average of ~25% their body weight, which is 150-200mg, so about 44mg
		self.stored_nectar = 0
		self.bee_type = Worker
	
	def drop_nectar(self):
		'''
		This method should drop the nectar in the hive.
		'''
		self.hive.nectar_units += self.stored_nectar
		self.stored_nectar = 0

	def collect(self, flower_patch):
		# worker bees cannot directly replenish their own health, that happens in the hive at end of day
		amount_to_withdraw = min(self.max_nectar-self.stored_nectar, flower_patch.nectar_units)
		flower_patch.withdraw_nectar(amount_to_withdraw)
		self.stored_nectar += amount_to_withdraw
		self.isCollecting = True

	def step(self):
		'''
		Worker behaviour in one step
		'''
		if self.stored_nectar == self.max_nectar: # If nectar stored is max, then either go back to the hive or drop the nectar
			if self.pos == self.hive.pos:
				self.drop_nectar()
			else:
				self.move_towards_hive()

		elif self.isCollecting == True:
			self.isCollecting = False
	  
		else: # neither full nor collecting, then the bee should move
			if self.last_resource:
				self.move_towards_resource()
			else: 
				# move the bee
				self.random_move()

			# we have just executed a random move, or have reached last_resource
			if not self.last_resource or self.pos == self.last_resource:
				flower_patch = self.check_cell_for_nectar()
				if flower_patch:
					# next timestep will be spent collecting
					self.collect(flower_patch)
				else:
					self.last_resource = None


class Drone(Bee):
	def __init__(self, unique_id, model, pos, hive, nectar_needed=236):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			pos (tuple(int, int)): The position of the bee in the environment.
			hive (Hive): the original hive of the bee.
			nectar_needed (int): amount of nectar needed per day.
		"""
		super().__init__(unique_id, model, pos, hive, nectar_needed)

		self.bee_type = Drone

	def step(self):
		"""
		Drone behaviour in one step
		"""
		# spend a timestep collecting food
		if self.isCollecting:
			self.isCollecting = False
			if self.health_level < self.nectar_needed and self.check_cell_for_nectar():
				self.last_resource = self.pos
			return

		# take a random step
		self.random_move()

		# if the bee is hungry and there is nectar in the current cell, consume
		if self.health_level < self.nectar_needed:
			flower_patch = self.check_cell_for_nectar()
			if flower_patch:
				self.collect(flower_patch)


class Queen(Bee):
	def __init__(self, unique_id, model, pos, hive, nectar_needed=740):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			pos (tuple(int, int)): The position of the bee in the environment.
			hive (Hive): the original hive of the bee.
			nectar_needed (int): amount of nectar needed per day.
		"""
		super().__init__(unique_id, model, pos, hive, nectar_needed)

		self.bee_type = Queen

	def mate(self, drone):
		self.hive.number_fertilized_queens += 1
		self.hive.remove_bee(self)
		self.model.remove_agent(self)
		drone.hive.remove_bee(drone)
		self.model.remove_agent(drone)

	def step(self):
		'''
		Defines behaviour for one timestep.
		'''
		# in hive and full on nectar, no action required
		if self.pos == self.hive.pos and self.health_level == self.nectar_needed:
			return

		# spend a timestep collecting resources, no movement
		elif self.isCollecting:
			self.isCollecting = False
			return

		# movement required, determine direction
		if self.health_level == self.nectar_needed:
			# store last_resource if nectar is available before returning to hive
			if self.check_cell_for_nectar():
				self.last_resource = self.pos
			self.move_towards_hive()
		else:
			# move towards last_resource if available
			if self.last_resource:
				self.move_towards_resource()
			# otherwise random walk
			else:
				self.random_move()

		# gather cell contents after moving
		cur_cell_contents = self.model.grid.get_cell_list_contents((int(self.pos[0]), int(self.pos[1])))

		# did not mate, and we have just executed a random move, or have reached last_resource and need more nectar
		if self.health_level < self.nectar_needed:
			if not self.last_resource or self.pos == self.last_resource:
				flower_patch = self.check_cell_for_nectar()
				if flower_patch:
					# next timestep will be spent collecting
					self.collect(flower_patch)
				else:
					self.last_resource = None


"""Class for the flower patches which contain the food source, nectar."""
class FlowerPatch(Agent):
	def __init__(self, unique_id, model, pos, nectar_units):
		"""
		Args:
			unique_id: a unique id for the flower patch.
			model: the model object.
			pos (tuple(int, int)): position of the flower patch in the environment.
			nectar_units (float): nectar in the flower patch at the beginning of model run.
		"""
		super().__init__(unique_id, model)
		self.pos = pos
		self.max_nectar_units = nectar_units
		self.nectar_units = nectar_units

		#represents how many times the 'pos' of this flower patch was sampled during the setting up of the environment.
		self.flower_patch_size = 1
		self.base_replenishing_quantity = self.max_nectar_units / self.model.daily_steps

		# This should be proportional to the initial nectar quantity of the flower patch because 
		# different flower patch may have different initial quantity due to the way the flower 
		# patches are set up. So, a flower patch having a greater initial nectar units represent
		# a bigger plant. Hence, the replenishing quantity per time step should be greater.
		self.replenishing_quantity = self.base_replenishing_quantity

	def update_flower_patch(self, more_nectar):
		"""
		Increases the size of the flower patch by an amount given by more_nectar
		"""
		self.flower_patch_size +=1 
		self.nectar_units += more_nectar
		self.max_nectar_units += more_nectar
		self.replenishing_quantity = self.base_replenishing_quantity * self.flower_patch_size

	def withdraw_nectar(self, nectar_drawn):
		"""
		Reduces the nectar quantity by the withdrawn amount.
		Args:
			nectar_drawn (float): nectar withdrawn by a bee.
		"""
		self.nectar_units = max(0, self.nectar_units-nectar_drawn)

	def step(self):
		"""
		Actions to be taken for a flower patch at every time step. 
		1. replenish the flower patch with nectar.
		"""
		self.nectar_units = min(self.max_nectar_units, self.nectar_units + self.replenishing_quantity)


"""Class for the hives"""
class Hive(Agent):
	def __init__(self, unique_id, model, pos, nectar_units):
		"""
		Args:
			unique_id (int): unique_id for the hive.
			pos (tuple(int, int)): position of the hive in the environment.
			nectar_units (float): nectar in the hive at the beginning of model run.
		"""
		super().__init__(unique_id, model)
		self.pos = pos
		self.max_nectar_units = nectar_units
		self.nectar_units = nectar_units
		self.bees = set()
		self.timestep_counter = 0
		self.number_fertilized_queens = 0

	def add_bee(self, bee):
		"""
		Adds a bee to the hive.
		Args:
			bee (Bee): bee to be added to the hive.
		"""
		self.bees.add(bee)

	def remove_bee(self, bee):
		"""
		Removes the bee from the hive.
		Args:
			bee (Bee): bee to be removed from the hive.
		"""
		self.bees.discard(bee)

	def bees_to_hive(self):
		for b in list(self.bees):
			if not isinstance(b, Drone):
				self.model.grid.move_agent(b, self.pos)

	def feed_and_kill_bees(self):
		# shuffling the agents before feeding
		bees = list(self.bees)
		self.model.rng.shuffle(bees)
		for b in bees:
			# kill drones if they did not find enough food
			if isinstance(b, Drone):
				if b.health_level < b.nectar_needed:
					self.remove_bee(b)
					self.model.remove_agent(b)
			else:
				# difference is how much nectar the bee needs to survive
				difference = b.nectar_needed - b.health_level
				# if hive nectar is at least difference, remove difference units form hive nectar
				if difference <= self.nectar_units:
					self.nectar_units -= difference
				else:
					# not enough stored nectar to feed bee, so it dies
					self.remove_bee(b)
					self.model.remove_agent(b)

	def generate_next_generation(self):
		'''
		this method will mutate the agents with health level != nectar_needed,
		the agents with health != nectar_needed will be killed and generated again in the new_offspring function
		'''
		coeffs = {Worker: self.model.alpha, Drone: self.model.beta, Queen: self.model.gamma}

		for b in list(self.bees):
			# find the probabilities of choosing each bee type based onencounters
			agent_probs = {}
			for bee_type, encounters in b.encounters.items():
				own_hive = len(encounters['own_hive'])
				other_hive = len(encounters['other_hive'])

				# calculating with encounter numbers instead of proportions
				# here; probabilities are normalised later, so this approach
				# is equivalent
				agent_probs[bee_type] = (coeffs[bee_type]*own_hive + (1-coeffs[bee_type])*other_hive)

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
			new_agent = self.model.create_new_agent(
				self.model.rng.choice(list(agent_probs.keys()),
				p=list(agent_probs.values())), b.pos, b.hive)
			new_agent.last_resource = b.last_resource
			new_agent.isCollecting = False
			b.hive.add_bee(new_agent)
			self.model.remove_agent(b)
			b.hive.remove_bee(b)

	def spawn_new_bees(self):
		while self.nectar_units > 0:
			new_agent = self.model.create_new_agent(
				self.model.rng.choice([Worker, Drone, Queen]), self.pos, self)
			self.add_bee(new_agent)
			self.nectar_units = max(0, self.nectar_units - new_agent.nectar_needed)

	def step(self):
		self.timestep_counter += 1
		if (self.timestep_counter) % self.model.daily_steps == 0:
			self.feed_and_kill_bees()
			self.generate_next_generation()
			self.bees_to_hive()
			self.spawn_new_bees()