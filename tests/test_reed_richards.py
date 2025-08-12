import pytest
from unittest.mock import Mock
from model.agents.reed_richards import ReedRichards
from model.location import Location
from model.environment import Environment
from model.actions.move import Move
from model.actions.repair import Repair
from model.actions.protect import Protect

class TestReedRichards:
    
    @pytest.fixture
    def reed_richards(self):
        """Create a ReedRichards instance for testing."""
        return ReedRichards(Location(5, 5))
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        env = Mock(spec=Environment)
        env.get_grid.return_value = [[None] * 20 for _ in range(20)]
        return env
    
    def test_initialization(self, reed_richards):
        """Test that ReedRichards initializes correctly."""
        assert reed_richards._location.get_x() == 5
        assert reed_richards._location.get_y() == 5
        assert reed_richards._role.name == "HERO"
        assert reed_richards._health == 1.0
        assert hasattr(reed_richards, 'repair_rate')
        assert hasattr(reed_richards, 'scan_range')
        assert hasattr(reed_richards, 'damage_rate')
    
    def test_get_state(self, reed_richards, mock_environment):
        """Test that get_state returns a valid state tuple."""
        state = reed_richards.get_state(mock_environment)
        assert isinstance(state, tuple)
        assert len(state) == 4  # region_id, bridge_dist_bin, bridge_health_bin, enemy_dist_bin
    
    def test_actions_with_empty_environment(self, reed_richards, mock_environment):
        """Test actions method with empty environment."""
        # Mock adjacent locations
        mock_locations = [Location(4, 5), Location(6, 5), Location(5, 4), Location(5, 6)]
        mock_environment.get_adjacent_locations.return_value = mock_locations
        
        # Mock get_agent to return None for all locations
        mock_environment.get_agent.return_value = None
        
        actions = reed_richards.actions(mock_environment)
        
        # Should return Move actions for all adjacent empty locations
        assert len(actions) > 0
        assert all(isinstance(action, Move) for action in actions)
    
    def test_actions_with_bridge(self, reed_richards, mock_environment):
        """Test actions method with a bridge nearby."""
        from model.agents.bridge import Bridge
        
        # Mock adjacent locations
        mock_locations = [Location(4, 5), Location(6, 5)]
        mock_environment.get_adjacent_locations.return_value = mock_locations
        
        # Create a mock bridge
        mock_bridge = Mock(spec=Bridge)
        mock_bridge.get_agent_role.return_value.name = "BRIDGE"
        mock_bridge.get_health.return_value = 0.5
        
        # Mock get_agent to return bridge at one location
        def mock_get_agent(location):
            if location.get_x() == 4 and location.get_y() == 5:
                return mock_bridge
            return None
        
        mock_environment.get_agent.side_effect = mock_get_agent
        
        actions = reed_richards.actions(mock_environment)
        
        # Should include Repair and Protect actions for the bridge
        action_types = [type(action).__name__ for action in actions]
        assert 'Repair' in action_types
        assert 'Protect' in action_types