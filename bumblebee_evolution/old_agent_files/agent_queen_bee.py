## Class for Queen Bumblebee

from agent_bee import Bee


class QueenBee(Bee):
    def __init__(self, unique_id, model, pos, associated_hive, fertilized=False):
        """
        Args:
            unique_id (int): unique id for the bee.
            model (BeeEvolutionModel): the model being used for the simulations.
            pos (tuple(int, int)): The position of the bee in the environment.
            associated_hive (Hive): the original hive of the bee
        """
        super().__init__(unique_id, model, pos, associated_hive)
        self.name = "QueenBee"
        self.nectar_needed = 740 #in mg. Needs to be converted to our units and then stored
        self.feritilized = fertilized
