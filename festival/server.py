from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule


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

chart = ChartModule([{"Label": "Alive agents",
                      "Color": "Black"}],
                    data_collector_name='datacollector')


server = ModularServer(SimpleModel,
                       [canvas, chart],
                       "Simple Model",
                       {"num_agents": n_slider})
