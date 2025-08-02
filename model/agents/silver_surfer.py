from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole

from controller.config.silver_surfer_config import SilverSurferConfig as CONFIG
from controller.config.config import Config as WorldConfig


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

        actions = []

        return actions