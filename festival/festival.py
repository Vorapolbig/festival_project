import random
from typing import Type, Any, Tuple, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation, SimultaneousActivation, StagedActivation
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace

from tqdm import tqdm

import seaborn as sns
sns.set()


class Guest(Agent):

    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float]):
        super().__init__(unique_id, model)
        self.pos: Tuple[float, float] = pos
        self.interaction_proposals: List[Tuple[Guest, str]] = []
        self.dead: bool = False
        self.range: float = 2.0

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
            self.dead = True
        else:
            other.dead = True

    def die(self):
        if self.dead:
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            print("%d just died" % self.unique_id)
        return

    def propose_interaction(self, other: 'Guest', action: 'str'):
        other.interaction_proposals.append((self, action))
        self.interaction_proposals.append((other, action))

    def send_proposes(self):

        # Could be learned
        neighbors = self.model.space.get_neighbors(self.pos, self.range, include_center=False)
        if len(neighbors) > 0:
            other_agent = random.choice(neighbors)
            self.propose_interaction(other_agent, 'fight')

    def process_proposes(self):
        """
        To implement individually, approve which interactions you're interested in
        """

        # Check which I'm still interested in, could be learned
        self.interaction_proposals = filter(lambda x: True, self.interaction_proposals)
        # self.interaction_proposals = list(self.interaction_proposals)

        # Check which the other is still interested in, don't touch
        self.interaction_proposals = filter(lambda x: (self, x[1]) in x[0].interaction_proposals,
                                            self.interaction_proposals)

        self.interaction_proposals = list(self.interaction_proposals)

        if len(self.interaction_proposals) > 1:
            print("Actually making a choice!")

        if len(self.interaction_proposals) > 0:
            # Choose a random interaction from the approved ones
            other: Guest
            interaction: str
            other, interaction = random.choice(self.interaction_proposals)
            getattr(self, interaction)(other)
            other.interaction_proposals = []

    def step(self):
        self.wander(2.0)

# TODO: Happiness and preferences


class SimpleModel(Model):

    def __init__(self, num_agents):
        super().__init__()
        self.num_agents = num_agents
        self.schedule = StagedActivation(self, ['send_proposes', 'process_proposes', 'step', 'die'])
        self.space = ContinuousSpace(100, 100, True)
        self.datacollector = DataCollector(
            model_reporters={"Alive agents": lambda model: model.schedule.get_agent_count()}
        )

        for i in range(self.num_agents):
            x, y = np.random.rand(2) * 100
            a_ = Guest(i, self, (x, y))
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
