from model import *
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if isinstance(agent, Bee):
        portrayal["Color"] = "red"
        portrayal["Layer"] = 2
        
    elif isinstance(agent, Hive):
        print(agent)
        portrayal["Color"] = "green"
        portrayal["Layer"] = 3
    else:
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 1
        portrayal["r"]=0.1

    return portrayal

grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)

server = ModularServer(BeeEvolutionModel,
                       [grid],
                       "Model",
                       {"width":100, "height":100, "num_hives":5, "nectar_units":100, "initial_bees_per_hive":100,"daily_steps":100,"rng": np.random.default_rng(1),"alpha":1,"beta":1,"gamma":1,"N_days":2})


server.port = 8521 # The default
server.launch()



