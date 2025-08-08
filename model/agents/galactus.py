from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from model.agents.agent import Agent
from model.agents.agent import AgentRole
from controller.config.galactus_config import GalactusConfig as CONFIG
from controller.config.config import Config as WorldConfig

from model.actions.move import Move
from model.location import Location

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
    
    def __next_location(self, bridges, franklin):
        """
        Decide the agent's next move toward the largest cluster of bridges or towards Franklin, whatever's closer.
        """

        # --- Step 1: Find clusters ---
        # For only 4 points, we can just check pairwise distances.
        # We'll treat clustering as: group cells that are closer than others.
        # For simplicity, we compute total pairwise distance and group by minimal sums.

        # Sort clusters by (size desc, compactness asc)
        from itertools import combinations

        best_cluster = None
        best_key = None

        for r in range(1, 5):  # possible cluster sizes
            for combo in combinations(bridges, r):
                # Compute total pairwise distance in this cluster
                dsum = 0
                for a, b in combinations(combo, 2):
                    dsum += a.dist(b)
                # Ranking key: (-size, dsum)
                key = (-len(combo), dsum)
                if best_key is None or key < best_key:
                    best_key = key
                    best_cluster = combo

        # --- Step 2: Nearest special in best cluster ---
        nearest = min(best_cluster, key=lambda s: self._location.dist(s))


        # Compare nearest and franklin
        franklin_dist = self._location.dist(franklin)
        nearest_dist = self._location.dist(nearest)

        if franklin_dist < nearest_dist:
            nearest = franklin

        # --- Step 3: Compute step toward nearest special ---
        ax, ay = self._location.get_x(), self._location.get_y()
        tx, ty = nearest.get_x(), nearest.get_y()
        m = WorldConfig.world_size

        # shortest dx, dy considering wrap
        dx = (tx - ax) % m
        if dx > m // 2:
            dx -= m
        dy = (ty - ay) % m
        if dy > m // 2:
            dy -= m

        # clamp to [-1,0,1] for Chebyshev step
        step_x = (dx > 0) - (dx < 0)
        step_y = (dy > 0) - (dy < 0)

        new_x = (ax + step_x) % m
        new_y = (ay + step_y) % m

        return Location(new_x, new_y)


    def actions(self, environment: Environment) -> list[Optional[Action]]:
        import random

        bridges = [agent.get_location() for row in environment.get_grid() for agent in row if agent is not None and agent.get_agent_role() == AgentRole.BRIDGE] 
        franklin = [agent.get_location() for row in environment.get_grid() for agent in row if agent is not None and agent.get_agent_role() == AgentRole.FRANKLIN]
        if len(franklin) == 0:
            move_loc = random.choice(environment.get_adjacent_locations(self._location))
        else:
            move_loc = self.__next_location(bridges, franklin[0])
        
        move_loc.set_range(self._location.get_range())
        return [Move(move_loc, self)]