from __future__ import annotations

from typing import TYPE_CHECKING

from model.agents.agent import Agent, AgentRole

if TYPE_CHECKING:
    from model.location import Location


class Headquarter(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role = AgentRole.HEADQUARTERS)
    
    def get_state(self, environment):
        return (self._location.get_x(), self._location.get_y())

    def actions(self, environment):
        return super().actions(environment)

