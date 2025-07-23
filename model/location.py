import math

from controller.config.config import Config


class Location:
    """Represents a location with integer x and y coordinates."""

    def __init__(self, x: int, y: int, range: int = 0) -> None:
        """
        Initialise the Location object with the given x and y coordinates.

        Parameters:
            x (int): The x-coordinate of the location.
            y (int): The y-coordinate of the location.
        """
        self.__x = x
        self.__y = y
        self._range = range
        self._world_size = Config.world_size

    def __eq__(self, other):
        """Return true if two objects are equal."""
        return self.__x == other.get_x() and self.__y == other.get_y()

    def __repr__(self) -> str:
        """Return a string representation of the location."""
        return f"Location({self.__x}, {self.__y})"

    def __str__(self) -> str:
        """Return a string representation of the location."""
        return f"Located at ({self.__x}, {self.__y})"

    def get_x(self) -> int:
        """Get the x-coordinate of the location."""
        return self.__x

    def set_x(self, x: int) -> None:
        """
        Set the x-coordinate of the location.

        Parameters:
            x (int): The new x-coordinate of the location.
        """
        self.__x = x
    
    def get_range(self) -> int:
        return self._range
    
    def set_range(self, range: int) -> None:
        self._range = range

    def get_y(self) -> int:
        """Get the y-coordinate of the location."""
        return self.__y

    def set_y(self, y: int) -> None:
        """
        Set the y-coordinate of the location.

        Parameters:
            y (int): The new y-coordinate of the location.
        """
        self.__y = y
    
    def dist(self, loc: "Location") -> float:
        """
        Toroidal Chebyshev distance between two cells in a wraparound grid.
        """
        
        dx = abs(self.__x - loc.__x)
        dy = abs(self.__y - loc.__y)
        
        dx = min(dx, self._world_size - dx)  # wraparound in x
        dy = min(dy, self._world_size - dy)  # wraparound in y
        
        return max(dx, dy)


    def get_points(self) -> list["Location"]:
        """Get the points in the range of the location."""
        points = []
        left_x = (self._world_size + self.__x - self._range) % self._world_size
        top_y = (self._world_size + self.__y - self._range) % self._world_size
        count_x = 0
        count_y = 0
        while(count_x < 2 * self._range + 1):
            while(count_y < 2 * self._range + 1):
                points.append(Location((left_x + count_x) % self._world_size, (top_y + count_y) % self._world_size))
                count_y += 1
            
            count_x += 1
            count_y = 0
        return points
    
