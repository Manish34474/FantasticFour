from __future__ import annotations

import os
import pickle

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional
from enum import Enum  
from collections import defaultdict

if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location
    from types import List
    from model.actions.action import Action



class AgentRole(Enum):
    VILLAIN = 0
    HERO = 1
    BRIDGE = 2
    FRANKLIN = 3
    HEADQUARTERS = 4

class Agent(ABC):
    """Represents an agent with a location."""

    def __init__(self, location: Location, role: AgentRole, health: Optional[float] = None) -> None:
        """
        Initialise the Agent object with the given location.

        Parameters:
            location (Location): The location of the agent.
        """
        self._location = location
        self._role = role
        self._health = health if health is not None else 1.0
        self.q_table = defaultdict(float)
        self.alpha = self.alpha = 0.1   # learning rate
        self.gamma = 0.9   # discount
        self.epsilon = 0.2 # exploration

        self.filepath = f"./model/agents/q_tables/{self.__class__.__name__}.pkl"

        if os.path.exists(self.filepath):
            self.load_q()


    
    @abstractmethod
    def get_state(self, environment: Environment) -> tuple:
        pass
    

    def update_q(self, old_state, action, reward, new_state, env):
        if self.actions(env) is None:
            return
        
        best_next = max([self.q_table[(new_state, a)] for a in self.actions(env)], default=0)
        self.q_table[(old_state, action)] += self.alpha * (
            reward + self.gamma * best_next - self.q_table[(old_state, action)]
        )
    

    def save_q(self) -> None:
        with open(self.filepath, "wb") as f:
            pickle.dump(self.q_table, f)
        
    
    def load_q(self) -> None:
        with open(self.filepath, "rb") as f:
            self.q_table = pickle.load(f)

    def __eq__(self, other: 'Agent') -> bool:
        """
        Compare two Agent objects for equality based on their locations.

        Parameters:
            other (Agent): The other Agent object to compare.

        Returns:
            bool: True if the two agents have the same location, False otherwise.
        """
        return isinstance(other, Agent) and self._location == other._location

    def __str__(self) -> str:
        """
        Return a string representation of the Agent object.

        Returns:
            str: String representation of the Agent object.
        """
        return f"{self.__class__.__name__} {self._location}"
    
    def __hash__(self):
        return hash(self.__class__.__name__)
    
    def name(self):
        return hash(self.__class__.__name__)

    @abstractmethod
    def actions(self, environment: Environment) -> List[Optional[Action]]:
        pass


    def get_location(self) -> Location:
        """
        Get the location of the agent.

        Returns:
            Location: The location of the agent.
        """
        return self._location

    def set_location(self, location: Location) -> None:
        """
        Set the location of the agent.

        Parameters:
            location (Location or None): The new location of the agent.
        """
        self._location = location
    
    def get_agent_role(self) -> AgentRole:
        """
        Get the role of the agent.

        Returns:
            AgentRole: The role of the agent.
        """
        return self._role
    
    def get_health(self) -> float:
        """
        Get the health of the agent.
        Returns:
            float: The health of the agent.
        """
        return self._health


    def reduce_health(self, attack_power: float) -> None:
        """
        Reduce the health of the agent by the specified attack power.

        Parameters:
            attack_power (float): The amount of health to reduce.
        """
        self._health -= attack_power if self._health > 0 else 0
        if self._health < 0.0:
            self._health = 0.0
    
    def increase_health(self, repair_power: float) -> None:
        """
        Increase the health of the agent by the specified repair power.

        Parameters:
            repair_power (float): The amount of health to increase.
        """
        self._health += repair_power if self._health < 1.0 else 0.0
        if self._health > 1.0:
            self._health = 1.0
    
    def pick_action(self, environment: Environment) -> Action:
        """
        Pick an action for Sue Storm to perform.
        :return: The action to be performed.
        """
        import random

        available_actions = self.actions(environment)

        if available_actions is None:
            return None

        state = self.get_state(environment)

        if random.random() < self.epsilon:
            return random.choice(available_actions)
        else:
            return max(available_actions, key=lambda a: self.q_table[(state, a)])
