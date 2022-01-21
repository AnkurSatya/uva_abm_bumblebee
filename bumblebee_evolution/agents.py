from environment import *
from mesa import Agent
import numpy as np
import random

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
		self.health_level = nectar_needed # health is full upon initialization
		self.isCollecting = False
		self.last_resource = None
		self.encounters = {
			Worker:{"own_hive":set(), "other_hive":set()},
			Drone:{"own_hive":set(), "other_hive":set()},
			Queen:{"own_hive":set(), "other_hive":set()}
		}

	def update_encounters(self, bee_type):
		cell_contents = self.model.grid.get_cell_list_contents([self.pos])
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
				item.encounters[bee_type][hive_category].add(self.unique_id)

	def random_move(self, bee_type):
		'''
		This method should get the neighbouring cells (Moore's neighbourhood), select one, and move the agent to this cell.
		'''
		neighbouring_cells = self.model.grid.get_neighborhood(self.pos, moore=True)
		if self.hive.pos in neighbouring_cells:
			neighbouring_cells.remove(self.hive.pos)

		# selecting new positiom
		new_pos = random.choice(self.model.grid.get_neighborhood(self.pos, moore=True))

		# moving the agent to the new position
		self.model.grid.move_agent(self, new_pos)
		self.update_encounters(bee_type)

	def check_cell_for_nectar(self, threshold=10): # TODO : update threshold value?
		'''
		This method should check if the cell is good enough to start collecting food.
		'''
		# content of the cell in the current position
		cell_concents = self.model.grid.get_cell_list_contents([self.pos])
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

	def move_towards_hive(self, bee_type):
		difference = np.array(self.pos) - np.array(self.hive.pos)
		self.model.grid.move_agent(self, (np.sign(difference[0]), np.sign(difference[1])))
		if self.pos != self.hive.pos: # TODO : shouldn't count the hive members, right?
			self.update_encounters(bee_type)

	def move_towards_resource(self, bee_type):
		difference = np.array(self.pos) - np.array(self.last_resource)
		self.model.grid.move_agent(self, (np.sign(difference[0]), np.sign(difference[1])))
		self.update_encounters(bee_type)


class Worker(Bee):
	def __init__(self, unique_id, model, hive, pos, nectar_needed=236):
		"""
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee
            pos (tuple(int, int)): The position of the bee in the environment.
			nectar_needed (int): amount of nectar needed per day
        """
		super().__init__(unique_id, model, pos, hive, nectar_needed)

		self.name = "Worker"
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
				self.move_towards_hive(self.bee_type)

		elif self.isCollecting == True:
			self.isCollecting = False
      
		else: # neither full nor collecting, then the bee should move
			if self.last_resource:
				self.move_towards_resource(self.bee_type)
			else: 
				# move the bee
				self.random_move(self.bee_type)

			# we have just executed a random move, or have reached last_resource
			if not self.last_resource or self.pos == self.last_resource:
				flower_patch = self.check_cell_for_nectar()
				if flower_patch:
					# next timestep will be spent collecting
					self.collect(flower_patch)
				else:
					self.last_resource = None


class Drone(Bee):
	def __init__(self, unique_id, model, hive, pos, nectar_needed=236):
		"""
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee.
            pos (tuple(int, int)): The position of the bee in the environment.
			nectar_needed (int): amount of nectar needed per day.
        """
		super().__init__(unique_id, model, pos, hive, nectar_needed)

		self.name = "Drone"
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
		self.random_move(self.bee_type)

		# if the bee is hungry and there is nectar in the current cell, consume
		if self.health_level < self.nectar_needed:
			flower_patch = self.check_cell_for_nectar()
			if flower_patch:
				self.collect(flower_patch)


class Queen(Bee):
	def __init__(self, unique_id, model, hive, pos, nectar_needed=740, fertilized=False, isMating=False):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee.
			pos (tuple(int, int)): The position of the bee in the environment.
			nectar_needed (int): amount of nectar needed per day.
			fertilized (bool): whether queen has been fertilized or not.
			isMating (bool): indicates whether queen is currently mating.
		"""
		super().__init__(unique_id, model, pos, hive, nectar_needed)

		self.name = "Queen"
		self.fertilized = fertilized
		self.isMating = isMating
		self.bee_type = Queen

	def mate(self, drone):
		self.fertilized = True
		self.model.grid.remove_agent(drone)

	def step(self):
		'''
		Defines behaviour for one timestep.
		'''
		# in hive and full on nectar, no action required
		if self.pos == self.hive.pos and self.health_level == self.nectar_needed:
			return

		# spend a timestep mating, no movement
		if self.isMating:
			self.isMating = False
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
			self.move_towards_hive(self.bee_type)
		else:
			# move towards last_resource if available
			if self.last_resource:
				self.move_towards_resource(self.bee_type)
			# otherwise random walk
			else:
				self.random_move(self.bee_type)

		# gather cell contents after moving
		cur_cell_contents = self.model.grid.get_cell_list_contents([self.pos])

		# prioritize possibility of mating with drone from different hive
		if not self.fertilized:
			drones = [item for item in cur_cell_contents if isinstance(item, Drone) and item.hive != self.hive]
			if len(drones):
				# next timestep will be spent mating
				self.mate(random.choice(drones))
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

		self.base_replenishing_quantity = 0.1

		# This should be proportional to the initial nectar quantity of the flower patch because 
		# different flower patch may have different initial quantity due to the way the flower 
		# patches are set up. So, a flower patch having a greater initial nectar units represent
		# a bigger plant. Hence, the replenishing quantity per time step should be greater.
		self.replenishing_quantity = self.base_replenishing_quantity

	def update_flower_patch(self, more_nectar):
		self.nectar_units += more_nectar
		self.max_nectar_units = self.nectar_units
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