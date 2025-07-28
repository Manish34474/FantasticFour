from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from model.actions.action import Action

if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location
    from model.agents.agent import Agent


class Retreat(Action):
    """
    Represents an retreat action in the environment.
    """

    def __init__(self, location: Location, agent: Agent) -> None:
        """
        Initialize the retreat action.
        """
        super().__init__(location, agent)
        

    def execute(self, environment: Environment) -> int:
        """
        Execute the retreat action in the given environment at the specified location.
        Only for SilverSurfer. This action removes SilverSurfer from the environment for exactly 5 time steps.

        :param environment: The environment in which the action is executed.
        :param agent: The agent performing the retreation.
        """
        
        environment.set_ss_flag(False, self._location)  # Set the flag indicating Silver Surfer is not in the environment
        self._agent.set_location(None)
        environment.set_agent(None,self._location)

        return 0