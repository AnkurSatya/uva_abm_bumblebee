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

width, height = 30, 30
num_hives = 3

grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

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

chart_fertilized_queens = ChartModule([{"Label": "Total Fertilized Queens",
                                        "Color": "Black"}],
                                        data_collector_name='datacollector')

alpha = 0.8
queen_coeff = 1
worker_coeff = 5
drone_coeff = 2

coeffs = {"alpha":alpha, 
          Queen:queen_coeff,
          Worker:worker_coeff,
          Drone:drone_coeff}

server = ModularServer(BeeEvolutionModel,
                       [grid, chart_bees, chart_fertilized_queens] + hive_charts,
                       "Bee Model",
                       {"width":width, 
                        "height":height, 
                        "num_hives": num_hives,
                        "initial_bees_per_hive":3, 
                        "daily_steps":100, 
                        "rng": np.random.default_rng(1),
                        "coefficients":coeffs, 
                        "N_days":30})

server.port = 8521 # The default
server.launch()