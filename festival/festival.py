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

from .guests import Guest, PartyPerson, Guard, Troublemaker, Celebrity, Hippie

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
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float]):
        super().__init__(unique_id, model)
        self.pos = pos
        self.role = 'stage'
        self.type = 'stage'

    def send_proposes(self):
        pass

    def process_proposes(self):
        pass

    def step(self):
        pass

    def die(self):
        pass


class Event(Agent):
    # Only serves the purpose of being visualized
    pass


class FestivalModel(Model):

    def __init__(self, num_party: int= 20, num_guard: int= 5, num_trouble: int= 5, num_celeb: int= 5, num_hippie: int= 20, learning=True, pareto_fight=False, pareto=False):
        super().__init__()
        self.num_agents = num_party + num_guard + num_trouble + num_celeb + num_hippie
        self.num_party = num_party
        self.num_guard = num_guard
        self.num_trouble = num_trouble
        self.num_celeb = num_celeb
        self.num_hippie = num_hippie
        self.pareto = pareto
        self.pareto_fight = pareto_fight

        self.schedule = StagedActivation(self, ['send_proposes', 'process_proposes', 'step', 'die'])
        self.space = ContinuousSpace(100, 100, False)
        self.datacollector = DataCollector(
            model_reporters={"Alive agents": lambda model: model.schedule.get_agent_count(),
                             "Mean happiness": lambda model: np.mean([a.happiness for a in filter(lambda x: x.type == 'guest', model.schedule.agents)]),
                             "Mean fullness": lambda model: np.mean([a.fullness for a in filter(lambda x: x.type == 'guest', model.schedule.agents)])}
        )

        for i in range(self.num_party):
            x, y = np.random.rand(2) * 100
            a_ = PartyPerson('Party%d' % i, self, (x, y), learning)
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

        for i in range(self.num_guard):
            x, y = np.random.rand(2) * 100
            a_ = Guard('Guard%d' % i, self, (x, y), learning)
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

        for i in range(self.num_trouble):
            x, y = np.random.rand(2) * 100
            a_ = Troublemaker('Trouble%d' % i, self, (x, y), learning)
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

        for i in range(self.num_celeb):
            x, y = np.random.rand(2) * 100
            a_ = Celebrity('Celeb%d' % i, self, (x, y), learning)
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

        for i in range(self.num_hippie):
            x, y = np.random.rand(2) * 100
            a_ = Hippie('Hippie%d' % i, self, (x, y), learning)
            self.schedule.add(a_)
            self.space.place_agent(a_, (x, y))

        for x, y in ((x, y) for x in [40, 60] for y in [40, 60]):
            s_ = Store('StoreX%dY%d' % (x, y), self, (x, y))
            self.schedule.add(s_)
            self.space.place_agent(s_, (x, y))

        for x, y in ((x, y) for x in [20, 80] for y in [20, 80]):
            s_ = Stage('StageX%dY%d' % (x, y), self, (x, y))
            self.schedule.add(s_)
            self.space.place_agent(s_, (x, y))

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def fight(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model, "Can't fight between other festival's guests"
        buffers = {agent1: 0., agent2: 0.}
        buffers_joy = {agent1: 0., agent2: 0.}

        for agent in (agent1, agent2):
            if agent.role == 'troublemaker':
                buffers[agent] += 1
            else:
                buffers[agent] -= 3
            if self.pareto_fight:
                p1 = [0.25, 0.25, 0.25, 0.25]
                p2 = [0.10, 0.10, 0.20, 0.60]
                index = np.random.choice(np.arange(0, 4), p=p1 if self.pareto else p2)
                store = [(0, 0), (0.2, -0.7), (-0.7, 0.2), (-0.5, -0.5)]

                select = store[index]
                buffers_joy[agent] += select[0] if agent.role == 'troublemaker' else select[1]

            buffers[agent] += agent.tastes['fight']
            buffers[agent] += 0.5*random.random() - 0.25

        for agent in (agent1, agent2):
            agent.happiness += buffers[agent]
            if self.pareto_fight:
                agent.enjoyment += buffers_joy[agent]

        agent1.learn((agent2.role, 'fight'), buffers[agent1])
        agent2.learn((agent1.role, 'fight'), buffers[agent2])
        print("A fight is happening")

    def party(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model
        buffers = {agent1: 0., agent2: 0.}
        for agent in (agent1, agent2):
            if agent.role == 'party':
                buffers[agent] += 1
            if agent.role == 'guard':
                buffers[agent] -= 3
            buffers[agent] += agent.tastes['party']
            buffers[agent] += 0.5*random.random() - 0.25

        for agent in (agent1, agent2):
            agent.happiness += buffers[agent]

        agent1.learn((agent2.role, 'party'), buffers[agent1])
        agent2.learn((agent1.role, 'party'), buffers[agent2])

        print("A party is happening")

    def calm(self, agent1: Guest, agent2: Guest): # Incorporate this in fight?
        assert self == agent1.model == agent2.model
        assert agent1.role == 'guard' or agent2.role == 'guard', "This interaction is forbidden"
        buffers = {agent1: 0., agent2: 0.}
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
            buffers[guard] += 1
            buffers[guest] -= 1
        else:
            buffers[guard] -= 2
            buffers[guest] -= 2

        for agent in (agent1, agent2):
            agent.happiness += buffers[agent]

        agent1.learn((agent2.role, 'calm'), buffers[agent1])
        agent2.learn((agent1.role, 'calm'), buffers[agent2])

        print("Calming is happening")

    def selfie(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model
        buffers = {agent1: 0, agent2: 0}

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
            buffers[celeb] += 1
            buffers[guest] -= 1
        else:
            buffers[celeb] += 1
            buffers[guest] += 1

        for agent in (celeb, guest):
            buffers[agent] += agent.tastes['selfie']
            buffers[agent] += 0.5*random.random() - 0.25

        for agent in (agent1, agent2):
            agent.happiness += buffers[agent]

        agent1.learn((agent2.role, 'selfie'), buffers[agent1])
        agent2.learn((agent1.role, 'selfie'), buffers[agent2])

        print("Selfie is happening")

    def smoke(self, agent1: Guest, agent2: Guest):
        assert self == agent1.model == agent2.model
        buffers = {agent1: 0., agent2: 0.}

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
            buffers[hippie] += 2
            buffers[guest] += 2
        elif guest.role == 'celebrity':
            buffers[hippie] += 1
            buffers[guest] -= 2
        elif guest.role == 'guard':
            buffers[hippie] -= 2
            buffers[guest] += 1
        else:
            buffers[hippie] += 1
            buffers[guest] += 0.5

        for agent in (hippie, guest):
            buffers[agent] += agent.tastes['smoke']
            buffers[agent] += 0.5*random.random() - 0.25

        for agent in (agent1, agent2):
            agent.happiness += buffers[agent]

        agent1.learn((agent2.role, 'smoke'), buffers[agent1])
        agent2.learn((agent1.role, 'smoke'), buffers[agent2])

        print("Smoking is happening")


# Roles:
# PartyPerson - parties with everyone
# Guard - points for staying near the celebrity and calming troublemakers, negative for distractions and calming normies
# Troublemaker - points for causing fights, negative for getting calmed by bodyguard
# Celebrity - points for selfies with nice/popular guests
# Hippie - points for sharing weed
