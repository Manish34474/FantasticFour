from __future__ import annotations

from typing import  TYPE_CHECKING

from model.actions.action import Action

if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location
    from model.agents.agent import Agent


class Repair(Action):
    """
    Represents an Repair action in the environment.
    """

    def __init__(self, repair_location: Location, agent: Agent) -> None:
        """
        Initialize the repair action with a target location.
        """
        super().__init__(repair_location, agent)
        

    def execute(self, environment: Environment) -> int:
        """
        Execute the repair action in the given environment at the specified location.

        :param environment: The environment in which the action is executed.
        :param agent: The agent performing the repair.
        """
        target_agent = environment.get_agent(self._location)
        if target_agent is not None:
            target_agent.increase_health(self._agent.repair_rate)
            return 10

        return 0