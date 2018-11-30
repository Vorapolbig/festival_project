import random
from typing import Type, Any, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace

from tqdm import tqdm

import seaborn as sns
sns.set()


class Guest(Agent):

    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float]):
        super().__init__(unique_id, model)
        self.pos = pos
        self.interaction_proposals = []

    def step(self):
        self.wander(0.5)
        self.get_into_a_fight()

    def move(self):
        # rand_vector = np.random.rand(2) * 2 - 1
        pos = np.array(self.pos)

        self.model.space.move_agent(self, pos - 0.01 * pos)

    def wander(self, speed: float = 1.):
        pos = np.array(self.pos)

        random_heading = random.random() * 2*np.pi
        rand_vector = speed * np.array([np.cos(random_heading), np.sin(random_heading)])
        self.model.space.move_agent(self, pos - rand_vector)
        return

    def fight(self, other: 'Guest'):
        eps = random.random()
        if eps < 0.5:
            self.die()
        else:
            other.die()

    def die(self):
        self.model.space.remove_agent(self)
        self.model.schedule.remove(self)
        return

    def get_into_a_fight(self):
        neighbors = self.model.space.get_neighbors(self.pos, 1., include_center=False)
        if len(neighbors) > 0:
            other_agent = random.choice(neighbors)
            self.fight(other_agent)
            print("A fight happened")

    def propose_interaction(self, other: 'Guest', action: 'str'):
        other.interaction_proposals.append((self, action))

# TODO: Stage activation, basic fight proposal
# TODO: Happiness and preferences


class SimpleModel(Model):

    def __init__(self, num_agents):
        super().__init__()
        self.num_agents = num_agents
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(100, 100, True)

        for i in range(self.num_agents):
            x, y = np.random.rand(2) * 100
            a_ = Guest(i, self, (x, y))
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

    def step(self):
        self.schedule.step()
