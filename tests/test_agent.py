import pytest
from unittest.mock import MagicMock
from model.location import Location
from model.agent import Agent, AgentRole, Action, Environment

# Mock concrete classes for testing abstract `Agent`
class ConcreteAgent(Agent):
    def get_state(self, environment: Environment) -> tuple:
        return (self._location.get_x(), self._location.get_y())
    
    def actions(self, environment: Environment) -> list[Optional[Action]]:
        return [MagicMock(spec=Action)]

@pytest.fixture
def agent():
    return ConcreteAgent(Location(1, 1), AgentRole.HERO, health=0.75)

def test_initialization(agent):
    assert agent.get_location() == Location(1, 1)
    assert agent.get_agent_role() == AgentRole.HERO
    assert agent.get_health() == 0.75

def test_default_health_initialization():
    new_agent = ConcreteAgent(Location(0, 0), AgentRole.HERO)
    assert new_agent.get_health() == 1.0

def test_set_location(agent):
    new_location = Location(5, 5)
    agent.set_location(new_location)
    assert agent.get_location() == new_location

def test_reduce_health(agent):
    agent.reduce_health(0.2)
    assert agent.get_health() == 0.55
    agent.reduce_health(0.6)
    assert agent.get_health() == 0.0

def test_increase_health(agent):
    # Reduce health first to test increase
    agent.reduce_health(0.5)
    assert agent.get_health() == 0.25
    
    agent.increase_health(0.5)
    assert agent.get_health() == 0.75
    
    # Test increase health cap
    agent.increase_health(0.5)
    assert agent.get_health() == 1.0

def test_eq_method():
    agent1 = ConcreteAgent(Location(1, 1), AgentRole.HERO)
    agent2 = ConcreteAgent(Location(1, 1), AgentRole.VILLAIN)
    agent3 = ConcreteAgent(Location(2, 2), AgentRole.HERO)
    
    assert agent1 == agent2
    assert agent1 != agent3
    
    # Test with non-Agent object
    assert agent1 != "not an agent"

def test_str_repr():
    agent = ConcreteAgent(Location(10, 20), AgentRole.HERO)
    assert str(agent) == "ConcreteAgent Located at (10, 20)"

def test_pick_action():
    agent = ConcreteAgent(Location(0, 0), AgentRole.HERO)
    env_mock = MagicMock(spec=Environment)
    
    # Mock the actions method to return a list of mock actions
    mock_action = MagicMock(spec=Action)
    agent.actions = MagicMock(return_value=[mock_action])
    
    picked_action = agent.pick_action(env_mock)
    
    assert picked_action == mock_action
    
def test_pick_action_none():
    agent = ConcreteAgent(Location(0, 0), AgentRole.HERO)
    env_mock = MagicMock(spec=Environment)
    
    # Mock the actions method to return None
    agent.actions = MagicMock(return_value=None)
    
    picked_action = agent.pick_action(env_mock)
    
    assert picked_action is None
