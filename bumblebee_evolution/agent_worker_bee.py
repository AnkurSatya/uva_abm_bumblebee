from agent_bee import Bee

class WorkerBee(Bee):
    def __init__(self, unique_id, model, pos, associated_hive):
        """
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
            pos (tuple(int, int)): The position of the bee in the environment.
            associated_hive (Hive): the original hive of the bee
        """
        super().__init__(unique_id, model, pos, associated_hive)

        self.name = "WorkerBee"
        self.max_nectar_carry = 40 # set this number
        self.nectar_needed = 236 #in mg. Needs to be converted to our units and then stored
        self.stored_nectar = 0

    def collect(self):
        '''
        This method should collect the nectar from the cell. 
        It will depend upon the following two factors:
            1. The nectar available in the flower patch at bee's position.
            2. The nectar needed by the bee to fulfill its daily quota.
        '''
        flower_patch_at_pos = self.model.get_flower_patch(self.pos)
        if flower_patch_at_pos is not None:
            self.stored_nectar +=  10# set this number
            flower_patch_at_pos.nectar_units -= 10 # set this number
    
    def drop_nectar(self):
        '''
        This method should drop the nectar in the hive.
        '''
        self.associated_hive.nectar_units += self.stored_nectar
        self.stored_nectar = 0

    def step(self):
        '''
        Actions to be taken for a bee at every time step.
        
        '''
        if self.stored_nectar == self.max_nectar_carry: # If nectar stored is max, then either go back to the hive or drop the nectar
            if self.pos == self.hive_pos:
                self.drop_nectar()
            else:
                self.back_to_hive()

        elif self.isCollecting == True:
            self.collect()
        else: # Not full neither collecting, then the bee should move
            if self.last_resource != self.hive_pos: # if position is saved, then go there
                self.towards_resource(self.last_resource)
                self.check_cell(478297429) # set the treshold
            else: 
                # Moving the bee
                self.random_move()
                self.check_cell(478297429) # set the treshold to a different value