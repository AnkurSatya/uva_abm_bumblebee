from model import *
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

"""
In this file is possible to look at the behaviour of the model using MESA visualisation.
"""

def agent_portrayal(agent):
    """
    This method change the color and the shape of an agent in the visualisation, 
    depending on the type of the agent.
    """
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

width = height = 25
num_hives = 3

grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# chart for total bees
chart_bees = ChartModule([{"Label": "Total Workers", "Color": "Blue"}, 
                          {"Label": "Total Queens", "Color": "Red"},
                          {"Label": "Total Drones", "Color": "Yellow"}],
                          data_collector_name='datacollector')

# charts for individual hives
hive_charts = []
for hive_i in range(num_hives):
    hive_charts.append(ChartModule([{'Label': f'Workers in Hive {hive_i}', 'Color': 'Blue'},
                                    {'Label': f'Queens in Hive {hive_i}', 'Color': 'Red'},
                                    {'Label': f'Drones in Hive {hive_i}', 'Color': 'Yellow'}],
                                    data_collector_name='datacollector'))

# chart for fertilized queens
chart_fertilized_queens = ChartModule([{"Label": "Total Fertilized Queens",
                                        "Color": "Black"}],
                                        data_collector_name='datacollector')

alpha = 0.5
forager_royal_ratio = 0.5
growth_factor = 0.5
resource_variability = 0.25

server = ModularServer(BeeEvolutionModel,
                       [grid, chart_bees, chart_fertilized_queens] + hive_charts,
                       "Bee Model",
                       {"alpha":alpha,
                        "forager_royal_ratio":forager_royal_ratio,
                        "growth_factor":growth_factor,
                        "resource_variability": resource_variability,
                        "seed":1,
                        "daily_data_collection": True})

server.port = 8521 # The default
server.launch()