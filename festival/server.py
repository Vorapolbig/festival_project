from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

from festival.festival import FestivalModel
from festival.SimpleContinuousModule import SimpleCanvas


def agent_draw(agent):
    if agent.role == 'store':
        color = "Blue"
    if agent.role == 'store':
        display = {"Shape": "rect",
                   "w": 0.05,
                   "h": 0.05,
                   "Filled": "true",
                   "Color": "Blue"}
    else:
        display = {"Shape": "circle",
                   "r": 2,
                   "Filled": "true",
                   "Color": "Red"}

    return display


canvas = SimpleCanvas(agent_draw, 500, 500)
model_params = {"num_agents": 50}
n_party = UserSettableParameter('slider', 'Number of party agents', 20, 2, 100, 1)
n_guard = UserSettableParameter('slider', 'Number of guard agents', 5, 2, 100, 1)
n_trouble = UserSettableParameter('slider', 'Number of troublemaker agents', 5, 2, 100, 1)
n_celeb = UserSettableParameter('slider', 'Number of celebrity agents', 5, 2, 100, 1)
n_hippie = UserSettableParameter('slider', 'Number of hippie agents', 20, 2, 100, 1)


# chart = ChartModule([{"Label": "Alive agents",
#                       "Color": "Black"}],
#                     data_collector_name='datacollector')

# chart = ChartModule([{"Label": "Mean happiness",
#                       "Color": "Red"}],
#                     data_collector_name='datacollector')

chart = ChartModule([{"Label": "Mean fullness",
                      "Color": "Red"}],
                    data_collector_name='datacollector')

server = ModularServer(FestivalModel,
                       [canvas, chart],
                       "Festival Model",
                       {"num_party": n_party,
                        "num_guard": n_guard,
                        "num_trouble": n_trouble,
                        "num_celeb": n_celeb,
                        "num_hippie": n_hippie})
