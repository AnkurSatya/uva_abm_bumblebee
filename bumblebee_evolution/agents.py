from mesa import Agent
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

	def collect(self):
		'''
		This method should collect the nectar from the cell.
		'''
		self.health_level += 4672462 # set this number
		flowers_patch.nectar_level -= 4672462 # set this number 
		self.isCollecting = True
	
	def back_to_hive(self):
		# we need to find a method to move towards the hive (located at self.hive.pos)
		# take one step towards the hive using shortest path?
		return

	def towards_resource(self, last_resource):
		# we need to find a method to move towards the last resource
		# this can take multiple time steps... either we call this function each timestep and move one cell towards resource
		# or this is called once, and the bee will automatically move towards the resource for however many time steps are needed
		return

		
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

	def collect(self):
		'''
		This method should collect the nectar from the cell.
		'''
		self.stored_nectar += 4672462 # set this number
		flowers_patch.nectar_level -= 4672462 # set this number 
	
	def drop_nectar(self):
		'''
		This method should drop the nectar in the hive.
		'''
		self.hive.nectar_level += self.stored_nectar
		self.stored_nectar = 0

	def step(self):
		'''
		'''
		if self.stored_nectar == self.max_nectar: # If nectar stored is max, then either go back to the hive or drop the nectar
			if self.pos == self.hive_pos:
				self.drop_nectar()
			else:
				self.back_to_hive(self.hive_pos)

		elif self.isCollecting == True:
			self.collect()
		else: # Not full neither collecting, then the bee should move
			if self.last_resource != self.hive_pos: # if position is saved, then go there
				self.towards_resource(self.last_resource) # TODO : this can take multiple time steps...
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
	def __init__(self, unique_id, model, hive, pos, health=740, fertilized=False):
		"""
		Args:
			unique_id (int): unique id for the bee.
			model (BeeEvolutionModel): the model being used for the simulations.
			hive (Hive): the original hive of the bee.
			pos (tuple(int, int)): The position of the bee in the environment.
			health (int): amount of nectar needed per day.
			fertilized (bool): whether queen has been fertilized or not.
		"""
		super().__init__(unique_id, model, hive, pos, health)

		self.name = "Queen"
		self.nectar_needed = health
		self.fertilized = fertilized
		self.isMating = False

	def mate(self, drone):
		self.fertilized = True
		self.model.grid.remove_agent(drone)


	def step(self):
		'''
		Defines behaviour for one timestep.
		'''
		# in the hive and full on nectar
		if self.pos == self.hive.pos and self.health_level == self.nectar_needed:
			return

		if self.isMating:
			self.isMating = False
			return

		# if there is male drone from a different hive at current position
			self.mate(drone)
			return

		# spend one timestep collecting resources, cannot do anything else
		if self.isCollecting:
			self.isCollecting = False

		else:
			if self.health_level == self.nectar_needed:
				self.back_to_hive()
			else:
				# if there is good source of nectar at current position
					self.collect()
				else:
					self.random_move()