from mesa import Model
from mesa.space import MultiGrid
from mesa import Agent
import random


class Bee(Agent):
    def __init__(self, unique_id, model, pos, hive_pos):
        super().__init__(unique_id, model)

        self.hive_id = hive_pos
        self.pos = pos
        self.isCollecting = False
        self.health_level
        self.last_resource = hive_pos

    def random_move(self):
        '''
        This method should get the neighbouring cells (Moore's neighbourhood), select one, and move the agent to this cell.
        '''
        # selecting new positiom
        new_pos = self.random.choice(self.model.grid.get_neighborhood(self.pos, True))
        # moving the agent to the new position
        self.model.grid.move_agent(self, new_pos)
      
    def check_cell(self,treshold):
        '''
        This method should check if the cell is good enough to start collecting food.
        '''
        # content of the cell in the current position
        this_cell = self.model.grid.get_cell_list_contents([self.pos])
        flowers_patch = [obj for obj in this_cell if isinstance(obj, flowers_patch)][0]
        if flowers_patch.nectar_level > treshold: # set the number to the treshold
            self.isCollecting = True

    def collect(self):
        '''
        This method should collect the nectar from the cell.
        '''
        self.health_level += 4672462 # set this number
        flowers_patch.nectar_level -= 4672462 # set this number 
    
    def back_to_hive(self, hive_pos):
        # we need to find a method to move towards the hive
        return

    def towards_resource(self, last_resource):
        # we need to find a method to move towards the last resource
        return
