"""Class for the flower patches which contain the food source, nectar."""

class FlowerPatch(object):
    def __init__(self, pos, nectar_units):
        """
        Args:
            pos (tuple(int, int)): position of the flower patch in the environment.
            nectar_units (float): nectar in the flower patch at the beginning of model run.
        """

        self.pos = pos
        self.max_nectar_units = nectar_units
        self.nectar_units = nectar_units
        self.replenishing_quantity = 0.1 # for every time step.

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
        
        self.nectar_units = max(self.max_nectar_units, self.nectar_units + self.replenishing_quantity)

