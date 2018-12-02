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

from .guests import Guest, PartyPerson

import seaborn as sns
sns.set()


class Store(Agent):
    pass


class Stage(Agent):
    pass


class FestivalModel(Model):

    def __init__(self, num_agents):
        super().__init__()
        self.num_agents = num_agents
        self.schedule = StagedActivation(self, ['send_proposes', 'process_proposes', 'step', 'die'])
        self.space = ContinuousSpace(100, 100, True)
        self.datacollector = DataCollector(
            model_reporters={"Alive agents": lambda model: model.schedule.get_agent_count(),
                             "Mean happiness": lambda model: np.mean([a.happiness for a in model.schedule.agents])}
        )

        for i in range(self.num_agents):
            x, y = np.random.rand(2) * 100
            a_ = PartyPerson('Guest%d' % i, self, (x, y))
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def fight(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model, "Can't kill other festival's guests"
        eps = random.random()
        if eps < 0.5:
            agent1.dead = True
        else:
            agent2.dead = True

    def party(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model
        for agent in (agent1, agent2):
            if agent.role == 'party':
                agent.happiness += 1
            agent.happiness += agent.tastes['party']
        print("A party is happening")
