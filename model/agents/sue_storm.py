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

    def get_state(self, environment):
        # state = (region_id, bridge_distance_bin, brige_health_bin, enemy_distance_bin)

        region_size = 5   # divide 20x20 into 5x5 = 25 regions
        region_x = self._location.get_x() // region_size
        region_y = self._location.get_y() // region_size
        region_id = region_y * (WorldConfig.world_size // region_size) + region_x

        # Nearest Bridge Info
        bridge_agents = [agent for row in environment.get_grid() for agent in row if agent is not None and agent.get_agent_role() == AgentRole.BRIDGE]
        dist_from_bridge = {bridge: self._location.dist(bridge.get_location())  for bridge in bridge_agents}
        min_dist = min(dist_from_bridge.values())
        if min_dist <= 2: bridge_dist_bin = 0
        elif min_dist <= 6: bridge_dist_bin = 1
        else: bridge_dist_bin = 2

        # Nearest Bridge Health
        near_bridge_health = min(dist_from_bridge, key = dist_from_bridge.get).get_health()

        if near_bridge_health <= 0.2: bridge_health_bin = 0
        elif near_bridge_health <= 0.6: bridge_health_bin = 1
        else: bridge_health_bin = 2

        enemy_agents = [agent for row in environment.get_grid() for agent in row if agent is not None and agent.get_agent_role() == AgentRole.HERO]
        dist_from_enemy = [self._location.dist(villain.get_location()) for villain in enemy_agents]
        min_dist = min(dist_from_enemy) if len(dist_from_enemy) > 0 else 0

        if min_dist <= 2: enemy_dist_bin = 0
        elif min_dist <=6: enemy_dist_bin = 1
        else: enemy_dist_bin = 2

        return (region_id, bridge_dist_bin, bridge_health_bin, enemy_dist_bin)
    
    

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

    
