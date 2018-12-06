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

# TODO: Implement an "event" agent for visualization purposes


class Store(Agent):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float]):
        super().__init__(unique_id, model)
        self.pos = pos
        self.role = 'store'
        self.type = 'store'

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

    def __init__(self, num_party: int=20, num_guard: int=5, num_trouble: int=5, num_celeb: int=5, num_hippie: int=20):
        super().__init__()
        self.num_agents = num_party + num_guard + num_trouble + num_celeb + num_hippie
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
        assert self == agent1.model == agent2.model, "Can't kill other festival's guests"
        for agent in (agent1, agent2):
            if agent.role == 'troublemaker':
                agent.happiness += 2
            agent.happiness -= 1
            agent.happiness += agent.tastes['fight']
            agent.happiness += random.random() - 0.5
        print("A fight is happening")

    def party(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model
        for agent in (agent1, agent2):
            if agent.role == 'party':
                agent.happiness += 1
            agent.happiness += agent.tastes['party']
            agent.happiness += random.random() - 0.5
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
        else:
            guard.happiness -= 1
            guest.happiness -= 1

    def selfie(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model

        if agent1.role == 'celebrity':
            celeb = agent1
            guest = agent2
        elif agent2.role == 'celebrity':
            celeb = agent2
            guest = agent1
        else:
            print("No celeb in selfie")
            return

        if guest.role == 'troublemaker':
            self.fight(celeb, guest)
            return
        elif guest.role == 'guard':
            celeb.happiness += 1
            guest.happiness -= 1
        else:
            celeb.happiness += 1
            guest.happiness += 1

        for agent in (celeb, guest):
            agent.happiness += agent.tastes['selfie']
            agent.happiness += random.random() - 0.5

    def smoke(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model

        if agent1.role == 'hippie':
            hippie = agent1
            guest = agent2
        elif agent2.role == 'hippie':
            hippie = agent2
            guest = agent1
        else:
            print("No hippie in smoking")
            return

        if guest.role == 'hippie':
            hippie.happiness += 2
            guest.happiness += 2
        elif guest.role == 'celebrity':
            hippie.happiness += 1
            guest.happiness -= 1
        elif guest.role == 'guard':
            hippie.happiness -= 1
            guest.happiness += 1
        else:
            hippie.happiness += 1
            guest.happiness += 0.5

        for agent in (hippie, guest):
            agent.happiness += agent.tastes['smoke']
            agent.happiness += random.random() - 0.5


# Roles:
# PartyPerson - parties with everyone
# Guard - points for staying near the celebrity and calming troublemakers, negative for distractions and calming normies
# Troublemaker - points for causing fights, negative for getting calmed by bodyguard
# Celebrity - points for selfies with nice/popular guests
# Hippie - points for sharing weed
