from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole

from controller.config.hero_config import HumanTorchConfig as CONFIG
from controller.config.config import Config as GLOBAL_CONFIG

from model.actions.move import Move
from model.actions.attack import Attack
from model.actions.repair import Repair
from model.actions.protect import Protect
from model.actions.heal import Heal

if TYPE_CHECKING:
    from model.location import Location
    from model.actions.action import Action


class HumanTorch(Agent):
    def __init__(self, location: Location) -> None:
        super().__init__(location, role=AgentRole.HERO)
        self.repair_rate = CONFIG.bridge_repair_rate
        self.scan_range = CONFIG.scan_radius
        self.attack_rate = CONFIG.attack_rate
        self.ranged_attack_health_reduce = CONFIG.ranged_attack_health_reduce
        self.ranged_attack_effect = CONFIG.ranged_attack_effect
        self.close_attack_rate = CONFIG.close_attack_rate
        self.damage_rate = CONFIG.damage_rate
    
 
    def actions(self, environment: Environment) -> list[Optional[Action]]:
        """
        Get the list of actions available to Human Torch in the given environment.
        
        :param environment: The environment in which the actions are to be performed.
        """
        actions = []
        movement_range = environment.get_adjacent_locations(self._location, 1)
        actionable_locations = environment.get_adjacent_locations(self._location, self.scan_range)

        franklin_flag = False
        franklin_agent = None

        for loc in movement_range:
            scanned_agent = environment.get_agent(loc)

            if scanned_agent.__class__.__name__ == "Franklin":
                franklin_flag = True
                franklin_agent = scanned_agent

            if scanned_agent is None:
                actions.append(Move(loc, self))
        
        if self._health > 0:
            for loc in actionable_locations:
                scanned_agent = environment.get_agent(loc)

                if scanned_agent is None:
                    continue

                elif scanned_agent.get_agent_role() is AgentRole.HEADQUARTERS:
                    actions.append(Heal(self._location, self))

                elif scanned_agent.get_agent_role() is AgentRole.BRIDGE:
                    if scanned_agent.get_health() < 1.0:
                        actions.append(Repair(loc, self))

                    actions.append(Protect(loc, self))
                
                elif scanned_agent.get_agent_role() is AgentRole.VILLAIN:
                    if scanned_agent.get_health() > 0.0:
                        actions.append(Attack(loc, self))
                
        if franklin_flag:
            for loc in movement_range:
                scanned_agent = environment.get_agent(loc)

                if scanned_agent is None:
                    m = GLOBAL_CONFIG.world_size
                    move_x = (m + loc.get_x() - self._location.get_x()) % m
                    move_y = (m + loc.get_y() - self._location.get_y()) % m
                    franklin_loc = franklin_agent.get_location()
                    franklin_loc.set_x(franklin_loc.get_x() + move_x)
                    franklin_loc.set_y(franklin_loc.get_y() + move_y)

                    if environment.get_agent(franklin_loc) is None:
                        actions.append(Move(loc, self, move_franklin=True))

        
        return actions