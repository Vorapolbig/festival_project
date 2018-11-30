from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter


from festival.festival import SimpleModel
from festival.SimpleContinuousModule import SimpleCanvas


def agent_draw(agent):
    return {"Shape": "circle",
            "r": 2,
            "Filled": "true",
            "Color": "Red"}


canvas = SimpleCanvas(agent_draw, 500, 500)
model_params = {"num_agents": 50}

n_slider = UserSettableParameter('slider', "Number of agents", 50, 2, 200, 1)

server = ModularServer(SimpleModel,
                       [canvas],
                       "Simple Model",
                       {"num_agents": n_slider})
