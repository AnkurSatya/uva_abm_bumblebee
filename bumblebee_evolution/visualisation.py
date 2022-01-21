from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if isinstance(agent, Drone):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 2
    elif isinstance(agent, Queen):
        portrayal["Color"] = "green"
        portrayal["Layer"] = 3
    elif isinstance(agent, Worker):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 3
    elif isinstance(agent, Hive):
        portrayal["Color"] = "orange"
        portrayal["Layer"] = 4
    else:
        portrayal["Color"] = "black"
        portrayal["Layer"] = 1
        portrayal["r"]=0.1

    return portrayal

grid = CanvasGrid(agent_portrayal, 30, 30, 500, 500)

server = ModularServer(BeeEvolutionModel,
                       [grid],
                       "Model",
                       {"width":30, "height":30, "num_hives":5, "nectar_units":100000, "initial_bees_per_hive":100,"daily_steps":100,"rng": np.random.default_rng(1),"alpha":1,"beta":1,"gamma":1,"N_days":2})


server.port = 8521 # The default
server.launch()



