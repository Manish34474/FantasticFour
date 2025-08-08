from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.environment import Environment
from model.agents.agent import AgentRole

from controller.config.silver_surfer_config import SilverSurferConfig as CONFIG
from controller.config.config import Config as WorldConfig

from model.actions.move import Move
from model.actions.attack import Attack
from model.actions.retreat import Retreat

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
        self.epsilon = 1.0

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
        movement_range = environment.get_adjacent_locations(self._location, self.__move_range)
        actionable_range = environment.get_adjacent_locations(self._location)
        # intelligence_range = environment.get_adjacent_locations(self._location, self.scan_range)

        actions = []

        if self._health <= 0.2:
            actions.append(Retreat(self._location, self))
            return actions

        for loc in movement_range:
            scanned_agent = environment.get_agent(loc)
            if(scanned_agent is None):
                actions.append(Move(loc, self))
        
        for loc in actionable_range:
            scanned_agent = environment.get_agent(loc)

            if scanned_agent is None:
                continue

            scanned_agent_role = scanned_agent.get_agent_role()
            if(scanned_agent_role == AgentRole.BRIDGE or scanned_agent_role == AgentRole.HERO):
                actions.append(Attack(loc, self))

        return actions