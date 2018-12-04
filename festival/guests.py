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
        self.range: float = 2.0
        self.happiness: float = 0.0

        self.pos: Tuple[float, float] = pos
        self.interaction_proposals: List[Tuple[Guest, str]] = []
        self.dead: bool = False

        self.fullness = 1.
        self.energy = 1.

        self.role: str = None
        self.type = 'guest'
        self.tastes = {
            'party': random.random() - 0.5,
            'fight': random.random() - 0.5,
        }

        self.store = None

    def distance_to(self, other: Tuple[float, float]):
        pos = np.array(self.pos)
        other = np.array(other)
        return np.linalg.norm(pos - other)

    def head_to(self, target:  Tuple[float, float], speed: float = 1.5):
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

        random_heading = random.random() * 2*np.pi
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
        Returns:

        """
        # Could be learned
        raise NotImplementedError

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

        if len(self.interaction_proposals) > 0:
            # Choose a random interaction from the approved ones
            other: Guest
            interaction: str
            other, interaction = random.choice(self.interaction_proposals)
            getattr(self.model, interaction)(self, other)
            other.interaction_proposals = []

    def step(self):

        self.fullness -= 0.01 * self.fullness
        #self.energy -= 0.1 * self.energy
        self.happiness += 0.1 * (self.fullness - 0.5)# + 0.1 * (self.energy - 0.5)

        if self.fullness < 0.5:
            if self.store is None:
                self.store = random.choice(list(filter(lambda x: x.type == 'store', self.model.schedule.agents)))
            self.head_to(self.store.pos, speed=1.)
        else:
            self.wander(2.0)

        if self.store is not None and self.distance_to(self.store.pos) < 5:
            self.fullness = 1.
            self.store = None

    def die(self):
        if self.dead:
            self.model.space.remove_agent(self)
            self.model.schedule.remove(self)
            print("%s just died" % self.unique_id)
        return


class PartyPerson(Guest):
    def __init__(self, unique_id: Any, model: Model, pos: Tuple[float, float]):
        super().__init__(unique_id, model, pos)
        self.role = 'party'

    def send_proposes(self):
        neighbors = self.model.space.get_neighbors(self.pos, self.range, include_center=False)
        neighbors = list(filter(lambda x: x.type == 'guest', neighbors))
        if len(neighbors) > 0:
            other_agent = random.choice(neighbors)
            self.propose_interaction(other_agent, 'party')

    def process_proposes(self):
        super().process_proposes()

    def step(self):
        super().step()
