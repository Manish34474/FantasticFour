from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from model.actions.action import Action

if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location
    from model.agents.agent import Agent


class Protect(Action):
    """
    Represents an Protect action in the environment.
    """

    def __init__(self, location: Location, agent: Agent) -> None:
        """
        Initialize the protect action.
        """
        super().__init__(location, agent)
        

    def execute(self, environment: Environment) -> int:
        """
        Execute the protect action in the given environment at the specified location.

        :param environment: The environment in which the action is executed.
        :param agent: The agent performing the protection.
        """
        return 0