from __future__ import annotations

from typing import TYPE_CHECKING

from model.agents.agent import Agent, AgentRole

from controller.config.bridge_config import BridgeConfig as CONFIG

if TYPE_CHECKING:
    from model.location import Location


class Bridge(Agent):
    def __init__(self, location: Location, health: float) -> None:
        super().__init__(location, role = AgentRole.BRIDGE, health = health)

        self.damage_rate = CONFIG.damage_rate
    
    def get_state(self, environment):
        return (self._location.get_x(), self._location.get_y())

    def actions(self, environment):
        return super().actions(environment)

