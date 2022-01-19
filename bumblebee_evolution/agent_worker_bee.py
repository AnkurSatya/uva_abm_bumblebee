from agent_bee import Bee

class Worker(Bee):
    def __init__(self, unique_id, model, pos, hive_pos):
        super().__init__(unique_id, model, pos)

        self.max_nectar = 40 # set this number
        self.nectar_needed = 236
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
        hive_nectar_level += self.stored_nectar
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
                self.towards_resource(self.last_resource)
                self.check_cell(478297429) # set the treshold
            else: 
                # Moving the bee
                self.random_move()
                self.check_cell(478297429) # set the treshold to a different value