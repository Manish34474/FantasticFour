from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.agents.agent import AgentRole

from controller.config.hero_config import TheThingConfig as CONFIG
from controller.config.config import Config as WorldConfig


if TYPE_CHECKING:
    from model.location import Location
    from model.actions.action import Action

class TheThing(Agent):
 
    def __init__(self, location: Location) -> None:
        super().__init__(location, role=AgentRole.HERO)
        self.scan_range = CONFIG.scan_radius
        self.repair_rate = CONFIG.bridge_repair_rate
        self.attack_rate = CONFIG.attack_rate
        self.close_attack_rate = CONFIG.close_attack_rate
        self.damage_rate = CONFIG.damage_rate
    


    def actions(self, environment) -> list[Optional[Action]]:
        """
        Returns a list of actions that the Thing can perform in the environment.
        
        :param environment: The environment in which the Thing operates.
        :return: A list of actions available to the Thing.
        """
        actions = []
        actionable_locations = environment.get_adjacent_locations(self._location, self.scan_range)


        return actions

    