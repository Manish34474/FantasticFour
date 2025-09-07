from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum

from model.agents.agent import Agent
from model.actions.action import Action

from controller.config.config import Config

from model.location import Location

if TYPE_CHECKING:
    from model.environment import Environment



class Move(Action):
    """
    Represents a move action in the environment.
    """

    def __init__(self, location: Location, agent: Agent, move_franklin: bool = False) -> None:
        """
        Initialise the Move object with the specified move type.

        """
        super().__init__(location, agent)
        self.__move_franklin = move_franklin

    def get_location(self) -> Location:
        """
        Returns the location to which the agent will move.

        Returns:
            Location: The target location for the move action.
        """
        return self._location

    def __eq__(self, value):
        """
        Check if two Move actions are equal based on their target locations.

        Args:
            value (Move): The Move action to compare with.

        Returns:
            bool: True if the target locations are the same, False otherwise.
        """
        return isinstance(value, Move) and self._location == value.get_location()
    
    def __hash__(self):
        """
        Returns a hash of the Move action based on its target location.

        Returns:
            int: The hash value of the Move action.
        """
        return hash((self._location.get_x(), self._location.get_y()))

    def execute(self, environment: Environment) -> None:
        """
        Execute the move action in the given environment at the specified location.

        :param environment: The environment in which the action is executed.
        :param agent: The agent performing the move.
        """

        if  self.__move_franklin:
            franklin_agent  = [agent for row in environment.get_grid() for agent in row if agent is not None and agent.__class__.__name__ == "Franklin"][0]

        environment.set_agent(None, self._agent.get_location())
        if self.__move_franklin: environment.set_agent(None, franklin_agent.get_location())

        move_dir = (( Config.world_size + self._location.get_x() - self._agent.get_location().get_x()) % Config.world_size, (Config.world_size + self._location.get_y() - self._agent.get_location().get_y()) % Config.world_size)
        if self.__move_franklin: franklin_loc = Location(franklin_agent.get_location().get_x() + move_dir[0], franklin_agent.get_location().get_y() + move_dir[1])

        environment.set_agent(self._agent, self._location)
        if self.__move_franklin: environment.set_agent(franklin_agent, franklin_loc)

        self._agent.set_location(self._location)
        if self.__move_franklin: franklin_agent.set_location(franklin_loc)

        return 0
