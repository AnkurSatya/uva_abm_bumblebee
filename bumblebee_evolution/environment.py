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
        self.nectar_units = min(self.max_nectar_units, self.nectar_units + self.replenishing_quantity)


"""Class for the hives"""
class Hive(object):
    def __init__(self, id, pos, nectar_units, bees):
        """
        Args:
            id (int): id for the hive.
            pos (tuple(int, int)): position of the hive in the environment.
            nectar_units (float): nectar in the hive at the beginning of model run.
        """
        self.id = id
        self.pos = pos
        self.max_nectar_units = nectar_units
        self.nectar_units = nectar_units
        self.bees = bees

    def get_num_bees_present(self):
        """
        Returns:
            int: number of bees present in the hive
        """
        bees_present = 0
        for bee in self.bees:
            if bee.pos == self.pos:
                bees_present += 1
        return bees_present

    def get_bees_of_type(self, bee_type):
        """
        Args:
            bee_type (string): type of the bee

        Returns:
            List(MaleBee/WorkerBee/QueenBee): a list of bee agents belonging to the bee_type.
        """
        type_bees = []
        for bee in self.bees:
            if bee.name == bee_type:
                type_bees.append(bee)
        return type_bees

    def get_bees_type_count(self):
        """
        Returns:
            dict: {'MaleBee': num present in the hive, 'WorkerBee': num present in the hive, 'QueenBee': num present in the hive}
        """
        bee_type_count = {
            "Drone": 0, 
            "Worker": 0,
            "Queen": 0}
        for bee in self.bees:
            bee_type_count[bee.name] += 1

        return bee_type_count


    def get_fertilized_queens(self):
        """
        Returns:
            int: the number of queen bees fertilized which are associated with the hive.
        """
        queen_bees = self.get_bees_of_type("Queen")

        fertilized_count = 0
        for bee in queen_bees:
            if bee.fertilized:
                fertilized_count += 1

        return fertilized_count

    def step(self):
        """
        Actions to be taken for a hive after a fixed number of steps(representing a day).
        1. Distributing the nectar among the bees.
        """
        pass