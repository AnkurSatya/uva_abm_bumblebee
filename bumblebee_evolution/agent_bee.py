from mesa import Agent
import random


class Bee(Agent):
    def __init__(self, unique_id, model, pos, associated_hive):
        """
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
            pos (tuple(int, int)): The position of the bee in the environment.
            associated_hive (Hive): the original hive of the bee
        """
        super().__init__(unique_id, model)

        self.name = "Bee"
        self.associated_hive = associated_hive
        self.hive_pos = associated_hive.pos
        self.pos = pos
        self.isCollecting = False
        self.health_level = 0
        self.last_resource = self.hive_pos

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
    
    def back_to_hive(self):
        # we need to find a method to move towards the hive. Use self.hive_pos for hive position.
        return

    def towards_resource(self, last_resource):
        # we need to find a method to move towards the last resource
        return
