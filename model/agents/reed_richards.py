from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole
from controller.config.hero_config import ReedRichardConfig as CONFIG
from controller.config.config import Config as WorldConfig

from model.actions.repair import Repair
from model.actions.move import Move
from model.actions.protect import Protect

if TYPE_CHECKING:
    from model.location import Location
    from model.actions.action import Action


class ReedRichards(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role=AgentRole.HERO)
        self.repair_rate = CONFIG.bridge_repair_rate
        self.scan_range = CONFIG.scan_radius
        self.damage_rate = CONFIG.damage_rate


    def actions(self, environment: Environment) -> list[Optional[Action]]:
        """
        Define the actions that Reed Richards can perform in the environment.
        This method should return a list of actions available to this agent.
        
        :param environment: The environment in which the agent operates.
        :return: A list of actions that this agent can perform.
        """

        actionable_locations = environment.get_adjacent_locations(self._location)
        
        actions = []

        for loc in actionable_locations:
            scanned_agent = environment.get_agent(loc)

            if scanned_agent is None:
                actions.append(Move(loc, self))


            elif scanned_agent.get_agent_role() is AgentRole.BRIDGE:
                if scanned_agent.get_health() < 1.0:
                    actions.append(Repair(loc, self))
                actions.append(Protect(loc, self))

        return actions