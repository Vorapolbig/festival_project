import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

from tqdm import tqdm

import seaborn as sns
sns.set()


def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N-i) for i, xi in enumerate(x)) / (N*sum(x))
    return 1 + (1/N) - 2*B


class MoneyAgent(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos,
                                                          moore=True,
                                                          include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1


class MoneyModel(Model):

    def __init__(self, N, width, height):
        super().__init__()
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        for i in range(self.num_agents):
            agent_temp = MoneyAgent(i, self)
            self.schedule.add(agent_temp)

            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(agent_temp, (x, y))

        self.datacollector = DataCollector(
            model_reporters={"Gini": compute_gini},  # Function
            agent_reporters={"Wealth": "wealth"})  # attribute

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def wealth_stats(self):
        return [a.wealth for a in self.schedule.agents]

