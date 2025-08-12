import pytest
from unittest.mock import Mock
from model.agents.sue_storm import SueStorm
from model.location import Location
from model.environment import Environment
from model.actions.move import Move
from model.actions.repair import Repair
from model.actions.protect import Protect

class TestSueStorm:
    
    @pytest.fixture
    def sue_storm(self):
        """Create a SueStorm instance for testing."""
        return SueStorm(Location(5, 5))
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        env = Mock(spec=Environment)
        env.get_grid.return_value = [[None] * 20 for _ in range(20)]
        return env
    
    def test_initialization(self, sue_storm):
        """Test that SueStorm initializes correctly."""
        assert sue_storm._location.get_x() == 5
        assert sue_storm._location.get_y() == 5
        assert sue_storm._role.name == "HERO"
        assert sue_storm._health == 1.0
        assert hasattr(sue_storm, 'repair_rate')
        assert hasattr(sue_storm, 'scan_range')
        assert hasattr(sue_storm, 'barrier_range')
        assert hasattr(sue_storm, 'damage_rate')
    
    def test_get_state(self, sue_storm, mock_environment):
        """Test that get_state returns a valid state tuple."""
        state = sue_storm.get_state(mock_environment)
        assert isinstance(state, tuple)
        assert len(state) == 4  # region_id, bridge_dist_bin, bridge_health_bin, enemy_dist_bin
    
    def test_actions_includes_protect(self, sue_storm, mock_environment):
        """Test that actions always includes a Protect action for current location."""
        # Mock adjacent locations
        mock_locations = [Location(4, 5)]
        mock_environment.get_adjacent_locations.return_value = mock_locations
        
        # Mock get_agent to return None
        mock_environment.get_agent.return_value = None
        
        actions = sue_storm.actions(mock_environment)
        
        # Should include Protect action for current location
        protect_actions = [action for action in actions if isinstance(action, Protect)]
        assert len(protect_actions) > 0
        
        # Check that one Protect action is for the current location
        current_loc_protect = any(
            action.get_location().get_x() == 5 and action.get_location().get_y() == 5
            for action in protect_actions
        )
        assert current_loc_protect