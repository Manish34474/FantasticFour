"""
This module defines the Earth environment for a simulation.

It includes the `Earth` class, which represents a grid-based environment where agents
can interact, and the `FightStatus` enum to track the state of a conflict within
the environment.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional, TYPE_CHECKING
from enum import Enum

from controller.config.config import Config

from model.environment import Environment
from model.location import Location
from model.agents.agent import Agent, AgentRole

if TYPE_CHECKING:
    from model.agents.agent import Agent
    from model.actions.action import Action

class FightStatus(Enum):
    """
    Enum representing the status of a fight within the Earth environment.

    - `WON`: Indicates the fight has been won.
    - `LOST`: Indicates the fight has been lost.
    - `RUNNING`: Indicates the fight is ongoing.
    """
    WON = 1
    LOST = 0
    RUNNING = -1

class Earth(Environment):
    """
    Concrete implementation of the `Environment` class representing the Earth.

    This class manages a grid of agents, their actions, and the overall status of
    the environment. It handles agent placement, movement, and interaction.
    """

    def __init__(self):
        """
        Initialise the Earth environment.

        Initialises a grid with dimensions based on the world size specified in the `Config` module.
        """
        # Call the constructor of the parent class (Environment)
        super().__init__()
        # Initialize a 2D list (grid) to store agents, with dimensions from Config.
        self.__grid: list[list[Optional[Agent]]] = [
            [None for _ in range(self.get_width())] for _ in range(self.get_height())
        ]

        # A buffer to store actions that need to be executed.
        self.__action_buffer = []
        # The current status of the fight, initialized to RUNNING.
        self.__status = FightStatus.RUNNING


    def __str__(self):
        """
        Return a string representation of the Earth environment.

        Returns:
            str: A string representation of the Earth environment including its dimensions.
        """
        # Create a visual representation of the grid using agent class names or '.' for empty cells.
        grid = '\n'.join([' '.join(['.  ' if cell is None else cell.__class__.__name__[0:3] for cell in row]) for row in self.__grid])
        grid += '\n\n\n'
        # Append the health of each agent in the grid to the string representation.
        for row in self.__grid:
            for cell in row:
                if cell is not None:
                    grid += f"{cell.__class__.__name__} hp =  {cell._health}\n"
        return grid

    def get_grid(self) -> list[list[Optional[Agent]]]:
        """
        Returns a copy of the current grid.

        Returns:
            list[list[Optional[Agent]]]: A copy of the 2D grid containing agents.
        """
        return self.__grid.copy()

    def clear(self) -> None:
        """
        Clears all agents from the grid and resets the environment status.
        """
        # Reinitialize the grid with `None` values.
        self.__grid = [[None for _ in range(Config.world_size)] for _ in range(Config.world_size)]

        # Reset the action buffer and fight status.
        self.__action_buffer = []
        self.__status = FightStatus.RUNNING


    def get_status(self) -> FightStatus:
        """
        Returns the current fight status of the environment.

        Returns:
            FightStatus: The status of the fight (e.g., `RUNNING`, `WON`, `LOST`).
        """
        return self.__status

    def get_agent(self, location: Location) -> Optional[Agent]:
        """
        Returns the agent at a given location, or None if location is invalid.

        Args:
            location (Location): The location to retrieve the agent from.

        Returns:
            Optional[Agent, None]: The agent at the specified location, or `None` if the location is outside the grid.
        """
        # Check if the provided location is valid.
        if location:
            # Wrap the coordinates to handle out-of-bounds locations.
            wrapped_x = location.get_x() % Config.world_size
            wrapped_y = location.get_y() % Config.world_size
            return self.__grid[wrapped_y][wrapped_x]

        # Return `None` if the location object is not valid.
        return None

    def get_adjacent_locations(self, location: Location, scan_range: int = 1) -> list[Location]:
        """
        Returns a list of adjacent positions on the grid, wrapping around the edges if necessary.

        Args:
            location (Location): The location to find adjacent positions for.
            scan_range (int): The range to scan for adjacent locations.

        Returns:
            List[Location]: A list of adjacent positions.
        """
        # Get all points within the specified scan range, including the center.
        locs = Location(location.get_x(), location.get_y(), scan_range).get_points()
        # Remove the center point to get only the adjacent locations.
        locs.remove(location)
        return locs


    def set_agent(self, agent: Optional[Agent], location: Location) -> None:
        """
        Places an agent at a specific location, wrapping around the grid edges if necessary.

        Args:
            agent (Agent): The agent to be placed.
            location (Location): The location where the agent should be placed.
        """
        # Check if the location is valid and has a range of 0 (single point).
        if location and location.get_range() == 0:
            # Wrap coordinates to handle out-of-bounds locations.
            wrapped_x = location.get_x() % Config.world_size
            wrapped_y = location.get_y() % Config.world_size
            self.__grid[wrapped_y][wrapped_x] = agent

        # Check if the location is valid and has a range greater than 0.
        elif location and location.get_range() > 0:
            # Get all points within the specified range.
            points = location.get_points()
            # Place the agent at each point in the range.
            for point in points:
                self.__grid[point.get_y()][point.get_x()] = agent


    def register_action(self, action: Action) -> None:
        """
        Registers an action to be executed later.

        Args:
            action (Action): The action object to be added to the buffer.
        """
        # If the action is not `None`, add it to the action buffer.
        if action:
            self.__action_buffer.append(action)


    def execute_actions(self) -> tuple:
        """
        Executes all actions in the action buffer, ensuring that each move action is executed only once.

        This method is responsible for processing the actions registered by agents in the environment.
        It should handle the order of execution and any potential conflicts.
        """
        # The implementation of this method is currently missing.
        pass