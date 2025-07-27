from __future__ import annotations

from typing import TYPE_CHECKING

from model.agents.agent import Agent, AgentRole
from model.actions.action import Action

from controller.config.hero_config import HeroConfig as CONFIG


if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location



class Heal(Action):
    """
    Represents an heal action in the environment.
    """

    def __init__(self, location: Location, agent: Agent) -> None:
        """
        Initialize the heal action.
        """
        super().__init__(location, agent)
        

    def execute(self, environment: Environment) -> None:
        """
        Execute the heal action in the given environment at the specified location.

        :param environment: The environment in which the action is executed.
        :param agent: The agent performing the healing.
        """
        self._agent.increase_health(CONFIG.heal_rate)

        if self._agent.get_agent_role() is AgentRole.VILLAIN:
            return -3
        else:
            return 3