from mesa import Agent
import numpy as np

'''
In this file, there are all the agents used for the project. 
1) general Bee agent from which the Queen, Worker and Drone class hinerit the common methods and attributes
2) Worker class
3) Drone class
4) Queen class
5) Flower patch class
6) Hive class
'''

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
		self.isCollecting = False # false if the bee is not collecting, when it finds a good resource will be switched to true
		self.last_resource = None # store the last good resource for the bee, since the bumblebees will always return there if it was a good resource
		# dictionary with all the encounters made by a bee, in the dictionary, all the unique_ids will be stored in order to avoit to count the same bee twice
		self.encounters = {
			Worker:{"own_hive":set(), "other_hive":set()},
			Drone:{"own_hive":set(), "other_hive":set()},
			Queen:{"own_hive":set(), "other_hive":set()}
		}

	def update_encounters(self):
		'''
		This method should check and increment the encounters of a bee
		'''
		# if bee is in hive, don't record encounters
		if self.pos in self.model.hive_positions:
			return

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
		neighbouring_cells = self.model.grid.get_neighborhood(self.pos, moore=True)
		if self.hive.pos in neighbouring_cells:
			neighbouring_cells.remove(self.hive.pos)

		# selecting new position
		new_pos =  neighbouring_cells[int(self.model.random_move_values.pop()*len(neighbouring_cells))]

		# moving the agent to the new position
		self.model.grid.move_agent(self, tuple(new_pos))
		self.update_encounters()

	def check_cell_for_nectar(self, threshold=0): # it is possible to use a different treshold value in order to make a bee more selective
		'''
		This method should check if the cell is good enough to start collecting food.
		'''
		# content of the cell in the current position
		cell_contents = self.model.grid.get_cell_list_contents((int(self.pos[0]), int(self.pos[1])))
		for item in cell_contents:
			if isinstance(item, FlowerPatch):
				if item.nectar_units > threshold:
					return item
				else:
					return False
		return False

	def collect(self, flower_patch):
		'''
		This method should collect the nectar from the cell. The bee will collect all the nectar that it needs to eat or all the nectar in the flower

		Args:
			flower_patch(FlowerPatch): collect nectar from this flower patch
		'''
		amount_to_withdraw = min(self.nectar_needed - self.health_level, flower_patch.nectar_units)
		self.health_level += amount_to_withdraw
		flower_patch.withdraw_nectar(amount_to_withdraw)
		self.isCollecting = True

	def move_towards_hive(self):
		'''
		When called, this method will move the bee to its own hive one step at a time, as well as updating the encounters in the meantime
		'''
		difference =  np.array(self.hive.pos) - np.array(self.pos) # find direction 
		# moving the agent to the new position
		self.model.grid.move_agent(self, (self.pos[0]+np.sign(difference[0]), self.pos[1]+np.sign(difference[1]))) 
		# updating encounters
		self.update_encounters() 

	def move_towards_resource(self):
		'''
		Take one step towards the saved position of the last seen resource.
		'''
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
		self.stored_nectar = 0 # initialising the stored nectar to 0
		self.bee_type = Worker

	def drop_nectar(self):
		'''
		This method drops the nectar in the hive.
		'''
		self.hive.nectar_units += self.stored_nectar
		self.stored_nectar = 0

	def collect(self, flower_patch):
		'''
		This method should collect the nectar from a flower patch
		Args: 
			flower_patch (FlowerPatch): the flower patch agent on which the bee is.
		'''
		# worker bees cannot directly replenish their own health, that happens in the hive at end of day
		amount_to_withdraw = min(self.max_nectar-self.stored_nectar, flower_patch.nectar_units)
		# removing the nectar from the flower patch
		flower_patch.withdraw_nectar(amount_to_withdraw)
		self.stored_nectar += amount_to_withdraw
		#??setting isCollecting to True, this is done because now that the bee collected the nectar, 
		# will spend the next step frozen
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
		'''
		Mate with a drone.

		Args:
			drone (Drone): drone to mate with.
		'''
		self.hive.number_fertilized_queens += 1

		# drone and queen are removed after mating
		self.hive.remove_bee(self)
		self.model.remove_agent(self)
		drone.hive.remove_bee(drone)
		self.model.remove_agent(drone)

	def step(self):
		'''
		Defines queen behaviour for one timestep.
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
		for item in cur_cell_contents:
			if isinstance(item, Drone) and item.hive != self.hive:
				self.mate(item)
				return

		# did not mate, and we have just executed a random move, or have reached last_resource and need more nectar
		if self.health_level < self.nectar_needed:
			if not self.last_resource or self.pos == self.last_resource:
				flower_patch = self.check_cell_for_nectar()
				if flower_patch:
					# next timestep will be spent collecting
					self.collect(flower_patch)
				else:
					self.last_resource = None


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
		self.replenishing_quantity = self.max_nectar_units / self.model.daily_steps

	def withdraw_nectar(self, nectar_drawn):
		"""
		Reduces the nectar quantity by the withdrawn amount.
		Args:
			nectar_drawn (float): nectar withdrawn by a bee.
		"""
		self.nectar_units -= nectar_drawn

	def step(self):
		"""
		Actions to be taken for a flower patch at every time step. 
		1. replenish the flower patch with nectar.
		"""
		self.nectar_units = min(self.max_nectar_units, self.nectar_units + self.replenishing_quantity)


class Hive(Agent):
	def __init__(self, unique_id, model, pos):
		"""
		Args:
			unique_id (int): unique_id for the hive.
			pos (tuple(int, int)): position of the hive in the environment.
		"""
		super().__init__(unique_id, model)
		self.pos = pos
		self.nectar_units = 0
		self.bees = []
		self.number_fertilized_queens = 0

	def add_bee(self, bee):
		"""
		Adds a bee to the hive.
		Args:
			bee (Bee): bee to be added to the hive.
		"""
		self.bees.append(bee)

	def remove_bee(self, bee):
		"""
		Removes the bee from the hive.
		Args:
			bee (Bee): bee to be removed from the hive.
		"""
		self.bees.remove(bee)

	def bees_to_hive(self):
		'''
		Move all bees back to the hive.
		'''
		for b in self.bees:
			if not isinstance(b, Drone):
				self.model.grid.move_agent(b, self.pos)

	def feed_and_kill_bees(self):
		'''
		Feed the bees and kill the ones that didn't reach the nectar required for one day
		'''
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
		Mutate bees.
		'''
		coeffs = self.model.parameters

		for b in list(self.bees):
			# find the probabilities of choosing each bee type based on encounters
			agent_counts = {}
			for bee_type, encounters in b.encounters.items():
				agent_counts[(bee_type, "own")] = len(encounters['own_hive'])
				agent_counts[(bee_type, "other")] = len(encounters['other_hive'])
			
			total_bees_encountered = sum(agent_counts.values())
			
			if total_bees_encountered == 0:
				b.health_level = 0
				continue

			# Computing the probabilities from the encounters made by a bee
			agent_counts = {key:value/total_bees_encountered for key, value in agent_counts.items()}
			agent_probs = {
				Worker: coeffs["forager_royal_ratio"] * (1 - (coeffs["alpha"]*agent_counts[(Worker, "own")] + (1-coeffs["alpha"])*agent_counts[(Worker, "other")])),
				Drone : ((1 - coeffs["forager_royal_ratio"])/2) * (1-(coeffs["alpha"]*agent_counts[(Drone, "own")]) + (1-coeffs["alpha"])*agent_counts[(Queen, "other")]),
				Queen : ((1 - coeffs["forager_royal_ratio"])/2) * (1-(coeffs["alpha"]*agent_counts[(Queen, "own")]) + (1-coeffs["alpha"])*agent_counts[(Drone, "other")])
			}

			# normalise into probabilities by dividing by sum
			prob_sum = sum(agent_probs.values())
			if prob_sum == 0:
				b.health_level = 0
				continue
			agent_probs = {bee_type: prob/prob_sum for bee_type, prob in agent_probs.items()}

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
		"""
		Spawn new bees. 

		The amount of bees spawned depends on the growth_factor and on the
		amount of nectar in the hive.
		"""
		allocated_growth_nectar = self.nectar_units*self.model.parameters["growth_factor"]
		while allocated_growth_nectar > 0:
			new_agent = self.model.create_new_agent(
				self.model.rng.choice([Worker, Drone, Queen]), self.pos, self)
			self.add_bee(new_agent)
			allocated_growth_nectar -= new_agent.nectar_needed
			self.nectar_units = max(0, self.nectar_units - new_agent.nectar_needed)

	def step(self):
		"""
		Single step for the hive. This method is called at the end of each day.
		"""
		self.feed_and_kill_bees()
		self.generate_next_generation()
		self.bees_to_hive()
		self.spawn_new_bees()