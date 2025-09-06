from __future__ import annotations

from collections import Counter
from typing import Optional, TYPE_CHECKING
from enum import Enum

from controller.config.config import Config
from controller.config.silver_surfer_config import SilverSurferConfig
from controller.config.bridge_config import BridgeConfig

from model.actions.move import Move
from model.actions.attack import Attack
from model.actions.protect import Protect

from model.environment import Environment
from model.location import Location
from model.agents.agent import Agent, AgentRole
from model.agents.franklin import Franklin

if TYPE_CHECKING:
    from model.agents.agent import Agent
    from model.actions.action import Action

class FightStatus(Enum):
    """Enum representing the status of the Earth environment."""
    WON = 1
    LOST = 0
    RUNNING = -1

class Earth(Environment):
    """Concrete implementation of the Environment class representing the Earth."""

    def __init__(self):
        """
        Initialise the Mars environment.

        Initialises a grid with dimensions based on the world size specified in the Config module.
        """
        super().__init__()
        self.__grid: list[list[Optional[Agent]]] = [
            [None for _ in range(self.get_width())] for _ in range(self.get_height())
        ]

        self.__action_buffer = []
        self.__status = FightStatus.RUNNING

        # for silver surfer respawn
        self.__ss_timer = 0
        self.__ss_flag = True
        self.__ss_agent = None


    def __str__(self):
        """
        Return a string representation of the Earth environment.

        Returns:
            str: A string representation of the Earth environment including its dimensions.
        """
        grid = '\n'.join([' '.join(['.  ' if cell is None else cell.__class__.__name__[0:3] for cell in row]) for row in self.__grid])
        grid += '\n\n\n'
        for row in self.__grid:
            for cell in row:
                if cell is not None:
                    grid += f"{cell.__class__.__name__} hp =  {cell._health}\n"
        return grid

    def get_grid(self) -> list[list[Optional[Agent]]]:
        return self.__grid.copy()

    def clear(self) -> None:
        """Clears all agents from the grid."""
        self.__grid = [[None for _ in range(Config.world_size)] for _ in range(Config.world_size)]

        self.__action_buffer = []
        self.__status = FightStatus.RUNNING

        # for silver surfer respawn
        self.__ss_timer = 0
        self.__ss_flag = True
        self.__ss_agent = None

    def get_status(self) -> FightStatus: 
        return self.__status

    def get_agent(self, location: Location) -> Optional[Agent]:
        """
        Returns the agent at a given location, or None if location is None.

        Args:
            location (Location): The location to retrieve the agent from.

        Returns:
            Optional[Agent, None]: The agent at the specified location, or None if the location is outside the grid.
        """
        if location:
            wrapped_x = location.get_x() % Config.world_size
            wrapped_y = location.get_y() % Config.world_size
            return self.__grid[wrapped_y][wrapped_x]

        return None

    def get_adjacent_locations(self, location: Location, scan_range: int = 1) -> list[Location]:
        """
        Returns a list of adjacent positions on the grid, wrapping around the edges if necessary.

        Args:
            location (Location): The location to find adjacent positions for.

        Returns:
            List[Location]: A list of adjacent positions.
        """
        # directions = [(-1, -1), (0, -1), (1, -1),
        #               (-1, 0), (1, 0),
        #               (-1, 1), (0, 1), (1, 1)]
        
        # if(scan_range > 1):
        #     i = 0
        #     for i in range(2, scan_range+1):
        #         add_directions = [(x* i, y * i) for x,y in directions]
        #         directions.extend(add_directions)

        # x, y = location.get_x(), location.get_y()
        # return [Location((x + dx) % self.get_width(), (y + dy) % self.get_height()) for dx, dy in
        #         directions]

        locs = Location(location.get_x(), location.get_y(), scan_range).get_points()
        locs.remove(location)
        return locs


    def set_agent(self, agent: Optional[Agent], location: Location) -> None:
        """
        Places an agent at a specific location, wrapping around the grid edges if necessary.

        Args:
            agent (Agent): The agent to be placed.
            location (Location): The location where the agent should be placed.
        """
        if location and location.get_range() == 0:
            wrapped_x = location.get_x() % Config.world_size
            wrapped_y = location.get_y() % Config.world_size
            self.__grid[wrapped_y][wrapped_x] = agent
        
        elif location and location.get_range() > 0:
            points = location.get_points()
            for point in points:
                self.__grid[point.get_y()][point.get_x()] = agent

    
    def set_ss_flag(self, flag: bool, location: Location) -> None:
        """
        Sets the flag indicating whether the Silver Surfer is currently in the environment.

        Args:
            flag (bool): True if Silver Surfer is present, False otherwise.
        """
        self.__ss_flag = flag
        self.__ss_agent = self.get_agent(location)


    def register_action(self, action: Action) -> None:
        """
        Registers an action to be executed later."""

        if action:
            self.__action_buffer.append(action)

    
    def __silver_surfer_respawn(self) -> None:

        import random

        # Silver Surfer respawn logic
        if self.__ss_flag == False :
            if self.__ss_timer == SilverSurferConfig.ss_respawn_time :
                self.__ss_flag = True
                self.__ss_timer = 0

                # respawn silver surfer
                while True:
                    x = random.randint(0, Config.world_size - 1)
                    y = random.randint(0, Config.world_size - 1)
                    location = Location(x, y)

                    if self.get_agent(location) is None:
                        self.__ss_agent.set_location(location)
                        self.set_agent(self.__ss_agent, location)
                        break
            
            else:
                self.__ss_timer += 1
    
    def execute_actions(self) -> None:
        """
        Executes all actions in the action buffer, ensuring that each move action is executed only once.
        """
       

        from model.agents.galactus import Galactus

        # filter out move actions from all actions
        move_actions = [action for action in self.__action_buffer if type(action) == Move]

        # count the number of occurrences of each move action
        counts = Counter(move_actions)
        
        # non-repeating move actions are valid moves
        valid_moves = [move for move in move_actions if counts[move] == 1]

        # reward value
        h_reward = 0
        v_reward = 0

        # ensure galactus move is executed last
        gal_idx = next((i for i, agt in enumerate(valid_moves) if isinstance(agt._agent, Galactus)), None)
        galactus_move = valid_moves.pop(gal_idx) if gal_idx is not None else None
        reward_list = [action.execute(self) for action in valid_moves]
        h_reward += sum([r for r in reward_list if r > 0])
        v_reward -= sum([r for r in reward_list if r < 0])

        v_reward -= galactus_move.execute(self) if galactus_move else 0


        #resolve attack and protect actions
        # step1: filter attack and protect actions
        # step2: execute an attack only if there is no protect action on the same location
        # step3: the protect action may contain location with range > 0
        # step4: if there are multiple protect actions on the same location, one is enough
        # step5: execute all other actions (except move) as they are

        for action in self.__action_buffer:
            if action is not None and type(action) == Attack:
                if any(action.get_location() in protect.get_location().get_points() for protect in self.__action_buffer if type(protect) == Protect):
                    continue
                else:
                    reward = action.execute(self)
                    if reward > 0: h_reward += reward
                    else: v_reward += reward * -1
            

            elif action is not None and type(action) != Move:
                reward = action.execute(self)
                if reward > 0: h_reward += reward
                else: v_reward += reward * -1
        


        self.__action_buffer.clear()
    
        self.__silver_surfer_respawn()
        
        # Game win or lose logic
        # if all bridges have full health, the game is won
        bridge_agents = [agent for row in self.__grid for agent in row if agent is not None and agent.get_agent_role() == AgentRole.BRIDGE]
        if all(bridge._health >= 1.0 for bridge in bridge_agents) and len(bridge_agents) == BridgeConfig.num_of_bridges:
            self.__status = FightStatus.WON
            print("Game Won! Completion of bridges")
            return (100 + h_reward, v_reward - 100)
        
        if len(bridge_agents) < BridgeConfig.num_of_bridges or any(bridge._health <= 0.0 for bridge in bridge_agents):
            self.__status = FightStatus.LOST
            print("Game Lost! Due to lack of all bridges")
            return (h_reward - 100, v_reward + 100)
        
        hero_agents = [agent for row in self.__grid for agent in row if agent is not None and agent.get_agent_role() == AgentRole.HERO]
        if len(hero_agents) == 0:
            self.__status = FightStatus.LOST
            print("Game Lost! All heroes are dead")
            return (h_reward - 100, v_reward + 100)
    

        franklin_agents = [agent for row in self.__grid for agent in row if agent is not None and agent.__class__ == Franklin]
        if len(franklin_agents) == 0:
            self.__status = FightStatus.LOST
            print("Game Lost! Galactus has found Franklin")
            return (h_reward - 100, v_reward + 100)

        return (h_reward, v_reward)

