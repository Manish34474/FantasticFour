import pytest
from unittest.mock import Mock
from model.actions.move import Move
from model.location import Location
from model.environment import Environment
from model.agents.agent import Agent

class TestMove:
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = Mock(spec=Agent)
        agent.get_location.return_value = Location(5, 5)
        return agent
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        env = Mock(spec=Environment)
        env.get_grid.return_value = [[None] * 20 for _ in range(20)]
        return env
    
    def test_initialization(self, mock_agent):
        """Test that Move action initializes correctly."""
        target_location = Location(6, 5)
        move_action = Move(target_location, mock_agent)
        
        assert move_action._location == target_location
        assert move_action._agent == mock_agent
        assert not move_action._Move__move_franklin
    
    def test_initialization_with_franklin_move(self, mock_agent):
        """Test that Move action initializes correctly with Franklin move flag."""
        target_location = Location(6, 5)
        move_action = Move(target_location, mock_agent, move_franklin=True)
        
        assert move_action._location == target_location
        assert move_action._agent == mock_agent
        assert move_action._Move__move_franklin
    
    def test_get_location(self, mock_agent):
        """Test get_location method."""
        target_location = Location(6, 5)
        move_action = Move(target_location, mock_agent)
        
        assert move_action.get_location() == target_location
    
    def test_equality(self, mock_agent):
        """Test equality comparison."""
        location1 = Location(6, 5)
        location2 = Location(6, 5)
        location3 = Location(7, 5)
        
        move1 = Move(location1, mock_agent)
        move2 = Move(location2, mock_agent)
        move3 = Move(location3, mock_agent)
        
        assert move1 == move2
        assert move1 != move3
    
    def test_hash(self, mock_agent):
        """Test hash method."""
        location = Location(6, 5)
        move_action = Move(location, mock_agent)
        
        # Hash should be based on location coordinates
        expected_hash = hash((location.get_x(), location.get_y()))
        assert hash(move_action) == expected_hash
    
    def test_execute_normal_move(self, mock_agent, mock_environment):
        """Test executing a normal move action."""
        target_location = Location(6, 5)
        move_action = Move(target_location, mock_agent)
        
        # Mock Franklin not being found
        mock_environment.get_grid.return_value = [[None] * 20 for _ in range(20)]
        
        result = move_action.execute(mock_environment)
        
        # Verify environment updates
        mock_environment.set_agent.assert_any_call(None, mock_agent.get_location.return_value)
        mock_environment.set_agent.assert_any_call(mock_agent, target_location)
        
        # Verify agent location update
        mock_agent.set_location.assert_called_with(target_location)
        
        # Should return 0 reward
        assert result == 0