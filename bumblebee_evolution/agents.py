from xml.etree.ElementInclude import include
from environment import *
from mesa import Agent
import numpy as np
import random

class Bee(Agent):
	def __init__(self, unique_id, model, pos, hive, health):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			pos (tuple(int, int)): The position of the bee in the environment.
			hive (Hive): the original hive of the bee
			health (int): amount of nectar needed per day
		"""
		super().__init__(unique_id, model)

		self.hive = hive
		self.pos = pos
		self.isCollecting = False
		self.health_level = health
		self.last_resource = None

	def random_move(self):
		'''
		This method should get the neighbouring cells (Moore's neighbourhood), select one, and move the agent to this cell.
		'''
		# selecting new positiom
		new_pos = random.choice(self.model.grid.get_neighborhood(self.pos, moore=True))
		
		# TODO : need to avoid randomly moving back to the hive, or outside of the grid?

		# moving the agent to the new position
		self.model.grid.move_agent(self, new_pos)

	def check_cell(self, threshold):
		'''
		This method should check if the cell is good enough to start collecting food.
		'''
		# content of the cell in the current position
		cell_concents = self.model.grid.get_cell_list_contents([self.pos])
		flowers_patch = [obj for obj in cell_concents if isinstance(obj, FlowerPatch)][0]
		if flowers_patch.nectar_level > threshold: # set the number to the treshold
			self.isCollecting = True

	def collect(self, flower_patch):
		'''
		This method should collect the nectar from the cell.
		'''
		self.health_level += 4672462 # set this number
		flower_patch.withdraw_nectar(4672462) # set this number 
		self.isCollecting = True

	def back_to_hive(self):
		difference = self.pos - self.hive.pos
		self.model.grid.move_agent(self, (np.sign(difference[0]), np.sign(difference[1])))

	def towards_resource(self):
		difference = self.pos - self.last_resource
		self.model.grid.move_agent(self, (np.sign(difference[0]), np.sign(difference[1])))


class Worker(Bee):
	def __init__(self, unique_id, model, hive, pos, health=236):
		"""
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee
            pos (tuple(int, int)): The position of the bee in the environment.
			health (int): amount of nectar needed per day
        """
		super().__init__(unique_id, model, hive, pos, health)

		self.name = "Worker"
		self.max_nectar = 40 # set this number
		self.nectar_needed = health
		self.stored_nectar = 0
	
	def drop_nectar(self):
		'''
		This method should drop the nectar in the hive.
		'''
		self.hive.nectar_units += self.stored_nectar
		self.stored_nectar = 0

	def step(self):
		'''
		'''
		if self.stored_nectar == self.max_nectar: # If nectar stored is max, then either go back to the hive or drop the nectar
			if self.pos == self.hive_pos:
				self.drop_nectar()
			else:
				self.back_to_hive()

		elif self.isCollecting == True:
			self.isCollecting = False
		else: # Not full neither collecting, then the bee should move
			if self.last_resource != self.hive_pos: # if position is saved, then go there
				self.towards_resource()
				self.check_cell(478297429) # set the treshold
			else: 
				# Moving the bee
				self.random_move()
				self.check_cell(478297429) # set the treshold to a different value


class Drone(Bee):
	def __init__(self, unique_id, model, hive, pos, health=236):
		"""
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee.
            pos (tuple(int, int)): The position of the bee in the environment.
			health (int): amount of nectar needed per day.
        """
		super().__init__(unique_id, model, pos, hive, health)

		self.name = "Drone"
		self.nectar_needed = health


class Queen(Bee):
	def __init__(self, unique_id, model, hive, pos, health=740, fertilized=False, isMating=False):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee.
			pos (tuple(int, int)): The position of the bee in the environment.
			health (int): amount of nectar needed per day.
			fertilized (bool): whether queen has been fertilized or not.
			isMating (bool): indicates whether queen is currently mating.
		"""
		super().__init__(unique_id, model, hive, pos, health)

		self.name = "Queen"
		self.nectar_needed = health
		self.fertilized = fertilized
		self.isMating = isMating

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
			cur_cell_contents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=0)
			flower_patch = [item for item in cur_cell_contents if isinstance(item, FlowerPatch)]
			if flower_patch:
				flower_patch = flower_patch[0]
				#  # TODO : condition for storing last_resource may need to be modified
				if flower_patch.nectar_units > 0:
					self.last_resource = self.pos
			return

		# movement required, determine direction
		if self.health_level == self.nectar_needed:
			self.back_to_hive()
		else:
			# move towards last_resource if available
			if self.last_resource:
				self.towards_resource()
			# otherwise random walk
			else:
				self.random_move()

		# gather cell contents after moving
		cur_cell_contents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=0)

		# prioritize possibility of mating with drone from different hive
		if not self.fertilized:
			drones = [item for item in cur_cell_contents if isinstance(item, Drone) and item.hive != self.hive]
			if len(drones):
				# next timestep will be spent mating
				self.mate(random.choice(drones))
				return

		# did not mate, and we have either reached last_resource or executed a random move
		if not self.last_resource or self.pos == self.last_resource:
			flower_patch = [item for item in cur_cell_contents if isinstance(item, FlowerPatch)]
			if flower_patch:
				flower_patch = flower_patch[0]
				if flower_patch.nectar_units > 0:
					# next timestep will be spent collecting
					self.collect(flower_patch)
				else:
					self.last_resource = None