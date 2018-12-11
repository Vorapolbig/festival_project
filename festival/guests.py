import random
from typing import Type, Any, Tuple, List, DefaultDict
from collections import defaultdict

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

    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float], learning: bool = True):
        super().__init__(unique_id, model)
        self.range: float = 3.
        self.happiness: float = 0.0
        self.learning = learning

        self.pos: Tuple[float, float] = pos
        self.interaction_proposals: List[Tuple[Guest, str]] = []
        self.dead: bool = False

        self.fullness = .55
        self.enjoyment = .55

        self.role: str = None
        self.type = 'guest'
        self.tastes = {
            'party': random.random() - 0.5,
            'fight': random.random() - 0.5,
            'selfie': random.random() - 0.5,
            'smoke': random.random() - 0.5
        }

        self.target = None

        self.knowledge: DefaultDict[Tuple[str, str], float] = defaultdict(float)
        self.knowledge_steps: DefaultDict[Tuple[str, str], int] = defaultdict(lambda: 1)

        self.action: str = None

    def __repr__(self):
        return self.unique_id

    def distance_to(self, other: Tuple[float, float]):
        pos = np.array(self.pos)
        other = np.array(other)
        return np.linalg.norm(pos - other)

    def head_to(self, target: Tuple[float, float], speed: float = 1.5):
        """
        Moves in the direction of the target point, with the specified speed.
        """
        pos = np.array(self.pos)
        target = np.array(target)

        heading = np.array(self.model.space.get_heading(pos, target))
        vector = speed * heading / np.linalg.norm(heading)
        self.model.space.move_agent(self, pos + vector)
        return

    def wander(self, speed: float = 1.):
        """
        Moves in a random direction with a specified speed
        """
        pos = np.array(self.pos)

        random_heading = random.random() * 2 * np.pi
        rand_vector = speed * np.array([np.cos(random_heading), np.sin(random_heading)])
        target_location = pos + rand_vector
        target_location = np.clip(target_location, [0, 0], [99.9, 99.9])
        self.model.space.move_agent(self, target_location)
        return

    def propose_interaction(self, other: 'Guest', action: str):
        """
        Sends a proposal of an interaction to another agent.
        For an interaction to occur, both agents must consent to it.
        Args:
            other: the other participant of the interaction.
            action: name of the interaction
        """
        other.interaction_proposals.append((self, action))
        self.interaction_proposals.append((other, action))

    def send_proposes(self):
        """
        Sends a proposal of an interaction to a neighbor

        """
        neighbors = self.model.space.get_neighbors(self.pos, self.range, include_center=False)
        neighbors = list(filter(lambda x: x.type == 'guest', neighbors))

        if len(neighbors) > 0:
            options = list(map(lambda x: (x.role, self.action), neighbors))
            know = list(map(lambda x: self.knowledge[x], options))
            # print("Knowledges", probs)
            probs = list(map(lambda x: np.exp(x), know))
            # print("Softmax", probs)
            probs = list(map(lambda x: x / sum(probs), probs))
            # print("Normed", probs)
            if len(neighbors) > 1:
                print(self.unique_id, neighbors, probs, know)

            other_agent = random.choices(neighbors, probs)[0]
            self.propose_interaction(other_agent, self.action)

    def process_proposes(self):
        """
        To implement individually, approve which interactions you're interested in
        """

        # Check which I'm still interested in, could be learned
        accepted = defaultdict(bool)
        for proposal in self.interaction_proposals:
            proposal: Tuple[Guest, str]
            error_prob = .05
            if random.random() < error_prob:
                accepted[proposal] = True
            else:
                if self.knowledge[(proposal[0].role, proposal[1])] >= 0:
                    accepted[proposal] = True

        self.interaction_proposals = filter(lambda x: accepted[x], self.interaction_proposals)
        # self.interaction_proposals = filter(lambda x: False, self.interaction_proposals)

        # self.interaction_proposals = list(self.interaction_proposals)

        # Check which the other is still interested in, don't touch
        self.interaction_proposals = filter(lambda x: (self, x[1]) in x[0].interaction_proposals,
                                            self.interaction_proposals)
        # TODO maybe split this up?
        self.interaction_proposals = list(self.interaction_proposals)

        if len(self.interaction_proposals) > 0:
            # Choose a random interaction from the approved ones
            if len(self.interaction_proposals) > 1:
                print(self.unique_id, self.interaction_proposals)

            other: Guest
            interaction: str
            other, interaction = random.choice(self.interaction_proposals)
            # print(interaction)

            getattr(self.model, interaction)(self, other)
            other.interaction_proposals = []

    def step(self):

        self.fullness -= 0.005 * self.fullness
        self.enjoyment -= 0.005 * self.enjoyment
        # self.happiness += 0.1 * (self.fullness - 0.5) + 0.1 * (self.enjoyment - 0.5)

        # self.happiness -= 0.02

        if self.fullness < 0.5:
            if self.target is None:
                self.target = random.choice(list(filter(lambda x: x.type == 'store', self.model.schedule.agents)))
            self.head_to(self.target.pos, speed=1.)
        elif self.enjoyment < 0.5:
            if self.target is None:
                self.target = random.choice(list(filter(lambda x: x.type == 'stage', self.model.schedule.agents)))
            self.head_to(self.target.pos, speed=1.)
        else:
            self.wander(1.0)

        if self.target is not None and self.distance_to(self.target.pos) < 2:
            if self.target.type == 'store':
                self.fullness = 1.
            elif self.target.type == 'stage':
                self.enjoyment = 1.
            self.target = None

        self.interaction_proposals = []
        # print(self, self.knowledge)

    def die(self):
        if self.dead:
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            print("%s just died" % self.unique_id)
        return

    def learn(self, key: Tuple[str, str], value: float):
        if not self.learning:
            return
        self.knowledge_steps[key] += 1
        n = self.knowledge_steps[key]
        self.knowledge[key] = self.knowledge[key] + (1 / n) * (value - self.knowledge[key])


class PartyPerson(Guest):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float], learning: bool = True):
        super().__init__(unique_id, model, pos, learning)
        self.role = 'party'
        self.action = 'party'

    def process_proposes(self):
        super().process_proposes()

    def step(self):
        super().step()


class Guard(Guest):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float], learning: bool = True):
        super().__init__(unique_id, model, pos, learning)
        self.role = 'guard'
        self.action = 'calm'

    def process_proposes(self):
        super().process_proposes()

    def step(self):
        super().step()


class Troublemaker(Guest):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float], learning: bool = True):
        super().__init__(unique_id, model, pos, learning)
        self.role = 'troublemaker'
        self.action = 'fight'

    def process_proposes(self):
        super().process_proposes()  # TODO approve only calm if present

    def step(self):
        super().step()


class Celebrity(Guest):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float], learning: bool = True):
        super().__init__(unique_id, model, pos, learning)
        self.role = 'celebrity'
        self.action = 'selfie'

    def process_proposes(self):
        super().process_proposes()

    def step(self):
        super().step()


class Hippie(Guest):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float], learning: bool = True):
        super().__init__(unique_id, model, pos, learning)
        self.role = 'hippie'
        self.action = 'smoke'

    def process_proposes(self):
        super().process_proposes()

    def step(self):
        super().step()
