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

# TODO: Implement venues
# TODO: Implement an "event" agent for visualization purposes


class Store(Agent):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float]):
        super().__init__(unique_id, model)
        self.pos = pos
        self.role = 'store'
        self.type = 'store'
        # TODO: Fix display

    def send_proposes(self):
        pass

    def process_proposes(self):
        pass

    def step(self):
        pass

    def die(self):
        pass


class Stage(Agent):
    pass

class Event(Agent):
    # Only serves the purpose of being visualized
    pass

class FestivalModel(Model):

    def __init__(self, num_agents):
        super().__init__()
        self.num_agents = num_agents
        self.schedule = StagedActivation(self, ['send_proposes', 'process_proposes', 'step', 'die'])
        self.space = ContinuousSpace(100, 100, False)
        self.datacollector = DataCollector(
            model_reporters={"Alive agents": lambda model: model.schedule.get_agent_count(),
                             "Mean happiness": lambda model: np.mean([a.happiness for a in filter(lambda x: x.type == 'guest', model.schedule.agents)]),
                             "Mean fullness": lambda model: np.mean([a.fullness for a in filter(lambda x: x.type == 'guest', model.schedule.agents)])}
        )

        for i in range(self.num_agents):
            x, y = np.random.rand(2) * 100
            a_ = PartyPerson('Guest%d' % i, self, (x, y))
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

        for x, y in ((x, y) for x in [33, 66] for y in [33, 66]):
            s_ = Store('StoreX%dY%d' % (x, y), self, (x, y))
            self.schedule.add(s_)
            self.space.place_agent(s_, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def fight(self, agent1: Guest, agent2: Guest):
        # TODO: change this to modifying happiness and energy
        assert self == agent1.model == agent2.model, "Can't kill other festival's guests"
        eps = random.random()
        if eps < 0.5:
            agent1.dead = True
        else:
            agent2.dead = True
        print("A fight is happening")

    def party(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model
        for agent in (agent1, agent2):
            if agent.role == 'party':
                agent.happiness += 1
            agent.happiness += agent.tastes['party']
        print("A party is happening")

    def calm(self, agent1: Guest, agent2: Guest): # Incorporate this in fight?
        assert self == agent1.model == agent2.model
        assert agent1.role == 'guard' or agent2.role == 'guard', "This interaction is forbidden"

        if agent1.role == 'guard':
            guard = agent1
            guest = agent2
        elif agent2.role == 'guard':
            guard = agent2
            guest = agent1
        else:
            guard = None
            guest = None
            print("This interaction should not be happening, we don't have a guard involved")
            return

        if guest.role == 'troublemaker':
            guard.happiness += 1
            guest.happiness -= 1

# Roles:
# PartyPerson
# Guard - points for staying near the celebrity and calming troublemakers, negative for distractions and calming normies
# Troublemaker - points for causing fights, negative for getting calmed by bodyguard
# Celebrity - points for selfies with nice/popular guests
# Hippie - points for sharing weed
