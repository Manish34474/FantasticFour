from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from model.environment import Environment
    from model.agents.agent import Agent
    from model.location import Location

class Action(ABC):
    """
    Abstract base class for actions in the environment.
    """
    
    def __init__(self, location: Location, agent: Agent) -> None:
        """
        Initialise the Action object with the specified location and agent.

        :param location: The location where the action is to be performed.
        :param agent: The agent performing the action.
        """
        self._location = location
        self._agent = agent


    def __str__(self):
        return f"{self.__class__.__name__} by {self._agent.__class__.__name__} {self._location}"
    
    def get_location(self) -> Location:
        """
        Returns the location where the action is to be performed.

        :return: The location of the action.
        """
        return self._location

    @abstractmethod
    def execute(self, environment: Environment) -> int:
        """
        Execute the action in the given environment at the specified location.

        :param environment: The environment in which the action is executed.
        :param location: The location where the action is performed.
        """
        pass