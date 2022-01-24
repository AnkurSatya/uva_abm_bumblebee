from model import *
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {
        Drone       : {"Shape":"circle", "r":0.3, "Color":"Yellow", "Filled":"false", "Layer":3},
        Queen       : {"Shape":"circle", "r":0.8, "Color":"Red", "Filled":"false", "Layer":1},
        Worker      : {"Shape":"circle", "r":0.5, "Color":"Blue", "Filled":"false", "Layer":2},
        Hive        : {"Shape":"rect", "w":1, "h":1, "Color":"Black", "Filled":"true", "Layer":0},
        FlowerPatch : {"Shape":"rect", "w":1, "h":1, "Layer":0, "Filled":"true", "Layer":0}
    }
    if isinstance(agent, Bee):
        return portrayal[agent.bee_type]
    elif isinstance(agent, Hive):
        return portrayal[Hive]
    elif isinstance(agent, FlowerPatch):
        if agent.nectar_units == 0:
            portrayal[FlowerPatch]["Color"] = "White"
        else:
            portrayal[FlowerPatch]["Color"] = "Green"

        return portrayal[FlowerPatch]

width, height = 25, 25

grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

chart_worker = ChartModule([{"Label": "Percentage of Workers",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

chart_queen = ChartModule([{"Label": "Percentage of Queens",
                      "Color": "Black"}],
                    data_collector_name='datacollector')

chart_drone = ChartModule([{"Label": "Percentage of Drones",
                            "Color": "Black"}],
                            data_collector_name='datacollector')

chart_fertilized_queens = ChartModule([{"Label": "Total Fertilized Queens",
                                        "Color": "Black"}],
                                        data_collector_name='datacollector')

server = ModularServer(BeeEvolutionModel,
                       [grid, chart_worker, chart_queen, chart_drone],
                       "Model",
                       {"width":width, "height":height, 
                       "num_hives":3,
                       "initial_bees_per_hive":20, 
                       "daily_steps":100, 
                       "rng": np.random.default_rng(1),
                       "alpha":1, "beta":1, "gamma":1, 
                       "N_days":2})

server.port = 8521 # The default
server.launch()