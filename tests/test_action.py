import pytest
from unittest.mock import MagicMock
from model.location import Location
from model.agent import Agent, AgentRole, Environment
from model.action import Action

# Mock concrete classes for testing abstract `Action`
class ConcreteAction(Action):
    def execute(self, environment: Environment) -> int:
        return 0

@pytest.fixture
def agent_mock():
    return MagicMock(spec=Agent, get_location=lambda: Location(1, 1), __class__=MagicMock(name="MockAgent"))

@pytest.fixture
def location_mock():
    return MagicMock(spec=Location, __str__=lambda: "Mock Location")

def test_initialization(location_mock, agent_mock):
    action = ConcreteAction(location_mock, agent_mock)
    assert action.get_location() == location_mock
    assert action._agent == agent_mock

def test_str(location_mock, agent_mock):
    action = ConcreteAction(location_mock, agent_mock)
    agent_mock.__class__.name = "MockAgent" # Set a mock name
    assert str(action) == "ConcreteAction by MockAgent Mock Location"

def test_get_location(location_mock, agent_mock):
    action = ConcreteAction(location_mock, agent_mock)
    assert action.get_location() == location_mock
    
def test_execute_abstract_method():
    action = ConcreteAction(MagicMock(), MagicMock())
    # The concrete implementation should not raise a NotImplementedError
    assert action.execute(MagicMock(spec=Environment)) == 0
