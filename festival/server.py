from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

from festival.festival import FestivalModel
from festival.SimpleContinuousModule import SimpleCanvas


guest_color_dict = {
    # role, color
    'party': 'Orange',
    'troublemaker': 'Red',
    'celebrity': 'Pink',
    'guard': 'Black',
    'hippie': 'Green',
    'lucia': 'Yellow'
}

guest_size_dict = {
    # role, color
    'party': 4,
    'troublemaker': 4,
    'celebrity': 6,
    'guard': 4,
    'hippie': 4,
    'lucia': 15
}


def agent_draw(agent):
    if agent.role == 'store':
        display = {"Shape": "rect",
                   "w": 0.05,
                   "h": 0.05,
                   "Filled": "true",
                   "Color": "Blue"}
    elif agent.role == 'stage':
        display = {"Shape": "rect",
                   "w": 0.05,
                   "h": 0.05,
                   "Filled": "true",
                   "Color": "Red"}
    # elif agent.role == 'Lucia':
    #     display = {"Shape": "star",
    #                "r": 6,
    #                "Filled": "true",
    #                "Color": "Yellow"}
    else:
        display = {"Shape": "circle",
                   "r": guest_size_dict[agent.role],
                   "Filled": "True",
                   "Color": guest_color_dict[agent.role]}
    return display


canvas = SimpleCanvas(agent_draw, 500, 500)
model_params = {"num_agents": 50}
n_party = UserSettableParameter('slider', 'Number of party agents', 10, 2, 20, 1)
n_guard = UserSettableParameter('slider', 'Number of guard agents', 10, 2, 20, 1)
n_trouble = UserSettableParameter('slider', 'Number of troublemaker agents', 10, 2, 20, 1)
n_celeb = UserSettableParameter('slider', 'Number of celebrity agents', 10, 2, 20, 1)
n_hippie = UserSettableParameter('slider', 'Number of hippie agents', 10, 2, 20, 1)

learning = UserSettableParameter('checkbox', 'Learning', True)
pareto_fight = UserSettableParameter('checkbox', 'Pareto Fight', False)
pareto = UserSettableParameter('checkbox', 'Pareto', False)
lucia = UserSettableParameter('checkbox', 'Lucia Dagen', False)

# chart = ChartModule([{"Label": "Alive agents",
#                       "Color": "Black"}],
#                     data_collector_name='datacollector')

chart = ChartModule([{"Label": "Mean happiness",
                      "Color": "Red"}],
                    data_collector_name='datacollector')

# chart = ChartModule([{"Label": "Mean fullness",
#                       "Color": "Red"}],
#                     data_collector_name='datacollector')

server = ModularServer(FestivalModel,
                       [canvas, chart],
                       "Festival Model",
                       {"num_party": n_party,
                        "num_guard": n_guard,
                        "num_trouble": n_trouble,
                        "num_celeb": n_celeb,
                        "num_hippie": n_hippie,
                        "learning": learning,
                        "pareto_fight": pareto_fight,
                        "pareto": pareto,
                        "lucia": lucia})
