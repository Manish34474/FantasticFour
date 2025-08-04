from __future__ import annotations

from typing import TYPE_CHECKING

from model.agents.agent import Agent, AgentRole

from controller.config.hero_config import HeroConfig as CONFIG

if TYPE_CHECKING:
    from model.location import Location


class Franklin(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role = AgentRole.FRANKLIN)

        self.damage_rate = CONFIG.damage_rate
    
    def get_state(self, environment):
        return None

    def actions(self, environment):
        return None

