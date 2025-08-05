from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole
from model.location import Location

from controller.config.hero_config import SueStormConfig as CONFIG
from controller.config.config import Config as WorldConfig

from model.actions.move import Move
from model.actions.repair import Repair
from model.actions.protect import Protect

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

        franklin_flag = False
        franklin_agent = None

        for loc in actionable_locations:
            scanned_agent = environment.get_agent(loc)

            if scanned_agent.__class__.__name__ == "Franklin":
                franklin_flag = True
                franklin_agent = scanned_agent

            if scanned_agent is None:
                actions.append(Move(loc, self))
            
            elif scanned_agent.get_agent_role() is AgentRole.BRIDGE:
                if scanned_agent.get_health() < 1.0:
                        actions.append(Repair(loc, self))
                actions.append(Protect(loc, self))
    
        actions.append(Protect(Location(self._location.get_x(), self._location.get_y(), self.barrier_range), self))

        if franklin_flag:
            for loc in actionable_locations:
                scanned_agent = environment.get_agent(loc)

                if scanned_agent is None:
                    m = WorldConfig.world_size
                    move_x = (m + loc.get_x() - self._location.get_x()) % m
                    move_y = (m + loc.get_y() - self._location.get_y()) % m
                    franklin_loc = franklin_agent.get_location()
                    franklin_loc.set_x(franklin_loc.get_x() + move_x)
                    franklin_loc.set_y(franklin_loc.get_y() + move_y)

                    if environment.get_agent(franklin_loc) is None:
                        actions.append(Move(loc, self, move_franklin=True))


        return actions

    
