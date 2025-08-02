from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.agents.agent import AgentRole
from model.location import Location

from controller.config.galactus_config import GalactusConfig as CONFIG
from controller.config.config import Config as WorldConfig

if TYPE_CHECKING:

    from model.environment import Environment
    from model.actions.action import Action


class Galactus(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role = AgentRole.VILLAIN)
        self.attack_rate = CONFIG.gal_attack_rate
        self.damage_rate = CONFIG.gal_damage_rate

    def get_state(self, environment: Environment) -> tuple:
        return None


    def actions(self, environment: Environment) -> list[Optional[Action]]:
        return None