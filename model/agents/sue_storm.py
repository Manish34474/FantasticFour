from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole
from model.location import Location

from controller.config.hero_config import SueStormConfig as CONFIG
from controller.config.config import Config as WorldConfig

if TYPE_CHECKING:

    from model.actions.action import Action


class SueStorm(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role=AgentRole.HERO)
        self.repair_rate = CONFIG.bridge_repair_rate
        self.scan_range = CONFIG.scan_radius
        self.barrier_range = CONFIG.barrier_range
        self.damage_rate = CONFIG.damage_rate
 
    

    def actions(self, environment: Environment) -> list[Optional[Action]]:
        """
        Get the list of actions available to Sue Storm in the given environment.
        :param environment: The environment in which the actions are to be performed. 
        """              
        actions = []
        actionable_locations = environment.get_adjacent_locations(self._location, self.scan_range)

        return actions

    
