import pytest
from unittest.mock import MagicMock, create_autospec

# Import the classes to be tested
from model.environment import Environment
from model.location import Location
from model.agents.agent import Agent, AgentRole
from model.actions.action import Action
from controller.config.config import Config

# Assuming Earth and FightStatus are in a file named 'earth.py'
from model.environment_files.earth import Earth, FightStatus

# Mock classes for testing purposes since Agent and Action are abstract
class MockAgent(Agent):
    """A mock agent class for testing."""
    def __init__(self, location: Location, role: AgentRole = AgentRole.HERO, health: float = 1.0):
        super().__init__(location, role, health)

    def get_state(self, environment: Environment) -> tuple:
        return (self._location.get_x(), self._location.get_y())

    def actions(self, environment: Environment) -> list[Optional[Action]]:
        return [MockAction(self.get_location(), self)]

class MockAction(Action):
    """A mock action class for testing."""
    def __init__(self, location: Location, agent: Agent):
        super().__init__(location, agent)

    def execute(self, environment: Environment) -> int:
        return 0

@pytest.fixture
def earth_environment():
    """Fixture to provide a new Earth instance for each test."""
    return Earth()

def test_initialization(earth_environment):
    """Test that the Earth environment is initialized correctly."""
    assert earth_environment.get_width() == Config.world_size
    assert earth_environment.get_height() == Config.world_size
    grid = earth_environment.get_grid()
    assert len(grid) == Config.world_size
    assert all(len(row) == Config.world_size for row in grid)
    assert all(all(cell is None for cell in row) for row in grid)
    assert earth_environment.get_status() == FightStatus.RUNNING

def test_clear(earth_environment):
    """Test that the clear method resets the environment."""
    agent1 = MockAgent(Location(1, 1))
    earth_environment.set_agent(agent1, agent1.get_location())
    
    earth_environment.clear()
    
    grid = earth_environment.get_grid()
    assert all(all(cell is None for cell in row) for row in grid)
    assert earth_environment.get_status() == FightStatus.RUNNING

def test_set_agent_at_location(earth_environment):
    """Test placing an agent at a single location."""
    location = Location(1, 1)
    agent = MockAgent(location)
    earth_environment.set_agent(agent, location)
    assert earth_environment.get_agent(location) == agent

def test_set_agent_with_range(earth_environment):
    """Test placing an agent with a range, affecting multiple locations."""
    location_with_range = Location(5, 5, range=1)
    agent = MockAgent(location_with_range)
    earth_environment.set_agent(agent, location_with_range)
    
    # Check if the agent is placed at all points in the range
    expected_points = location_with_range.get_points()
    for point in expected_points:
        assert earth_environment.get_agent(point) == agent

def test_get_agent(earth_environment):
    """Test retrieving an agent from a location."""
    location = Location(10, 15)
    agent = MockAgent(location)
    earth_environment.set_agent(agent, location)
    
    retrieved_agent = earth_environment.get_agent(location)
    assert retrieved_agent == agent

def test_get_agent_none_at_empty_location(earth_environment):
    """Test getting None for an empty location."""
    location = Location(2, 2)
    assert earth_environment.get_agent(location) is None

def test_get_agent_with_wrapping(earth_environment):
    """Test that get_agent handles coordinate wrapping."""
    agent = MockAgent(Location(1,1))
    earth_environment.set_agent(agent, Location(Config.world_size + 1, Config.world_size + 1))
    assert earth_environment.get_agent(Location(1,1)) == agent

def test_get_adjacent_locations(earth_environment):
    """Test the get_adjacent_locations method."""
    location = Location(5, 5)
    adj_locs = earth_environment.get_adjacent_locations(location)
    
    # The number of adjacent locations for a scan_range of 1 should be 8.
    assert len(adj_locs) == 8
    
    # Check that the returned locations are adjacent
    for loc in adj_locs:
        assert loc.dist(location) == 1
        assert loc != location

def test_get_adjacent_locations_with_range(earth_environment):
    """Test get_adjacent_locations with a larger scan range."""
    location = Location(10, 10)
    adj_locs = earth_environment.get_adjacent_locations(location, scan_range=2)

    # For a range of 2, the total points in the square are (2*2+1)^2 = 25.
    # Subtracting the center point (1) gives 24 adjacent locations.
    assert len(adj_locs) == 24
    
def test_register_action(earth_environment):
    """Test that an action is successfully registered."""
    location = Location(3, 3)
    agent = MockAgent(location)
    action = MockAction(location, agent)
    earth_environment.register_action(action)

    # The action buffer is a private attribute, so we use a mock to check its content.
    mock_earth = MagicMock(spec=Earth)
    mock_earth.register_action(action)
    mock_earth._Earth__action_buffer.append.assert_called_once_with(action)

def test_register_action_with_none_action(earth_environment):
    """Test that a None action is not registered."""
    mock_earth = MagicMock(spec=Earth)
    mock_earth.register_action(None)
    mock_earth._Earth__action_buffer.append.assert_not_called()

def test_get_grid(earth_environment):
    """Test that get_grid returns a copy of the grid."""
    grid_copy = earth_environment.get_grid()
    assert grid_copy == earth_environment.get_grid()
    assert grid_copy is not earth_environment.get_grid()
