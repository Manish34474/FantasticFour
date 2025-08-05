from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole

from controller.config.silver_surfer_config import SilverSurferConfig as CONFIG
from controller.config.config import Config as WorldConfig

from model.actions.move import Move
from model.actions.attack import Attack
from model.actions.retreat import Retreat

if TYPE_CHECKING:
    from model.location import Location
    from model.actions.action import Action


class SilverSurfer(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role=AgentRole.VILLAIN)
        self.__move_range = CONFIG.move_range
        self.scan_range = CONFIG.scan_radius
        self.attack_rate = CONFIG.ss_attack_rate
        self.damage_rate = CONFIG.ss_damage_rate
        self.attack_health_reduce = CONFIG.attack_health_reduce
        self.close_attack_rate = CONFIG.close_attack_rate


    def actions(self, environment: Environment) -> list[Optional[Action]]:
        movement_range = environment.get_adjacent_locations(self._location, self.__move_range)
        actionable_range = environment.get_adjacent_locations(self._location)
        # intelligence_range = environment.get_adjacent_locations(self._location, self.scan_range)

        actions = []

        if self._health <= 0.2:
            actions.append(Retreat(self._location, self))
            return actions

        for loc in movement_range:
            scanned_agent = environment.get_agent(loc)
            if(scanned_agent is None):
                actions.append(Move(loc, self))
        
        for loc in actionable_range:
            scanned_agent = environment.get_agent(loc)

            if scanned_agent is None:
                continue

            scanned_agent_role = scanned_agent.get_agent_role()
            if(scanned_agent_role == AgentRole.BRIDGE or scanned_agent_role == AgentRole.HERO):
                actions.append(Attack(loc, self))

        return actions