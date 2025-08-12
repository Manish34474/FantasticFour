import pytest
from unittest.mock import Mock
from model.agents.human_torch import HumanTorch
from model.location import Location
from model.environment import Environment
from model.actions.move import Move
from model.actions.attack import Attack
from model.actions.repair import Repair
from model.actions.protect import Protect
from model.actions.heal import Heal

class TestHumanTorch:
    
    @pytest.fixture
    def human_torch(self):
        """Create a HumanTorch instance for testing."""
        return HumanTorch(Location(5, 5))
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        env = Mock(spec=Environment)
        env.get_grid.return_value = [[None] * 20 for _ in range(20)]
        return env
    
    def test_initialization(self, human_torch):
        """Test that HumanTorch initializes correctly."""
        assert human_torch._location.get_x() == 5
        assert human_torch._location.get_y() == 5
        assert human_torch._role.name == "HERO"
        assert human_torch._health == 1.0
        assert hasattr(human_torch, 'repair_rate')
        assert hasattr(human_torch, 'scan_range')
        assert hasattr(human_torch, 'attack_rate')
        assert hasattr(human_torch, 'damage_rate')
    
    def test_get_state(self, human_torch, mock_environment):
        """Test that get_state returns a valid state tuple."""
        state = human_torch.get_state(mock_environment)
        assert isinstance(state, tuple)
        assert len(state) == 4  # region_id, bridge_dist_bin, bridge_health_bin, enemy_dist_bin
    
    def test_actions_with_villain(self, human_torch, mock_environment):
        """Test actions method with a villain nearby."""
        from model.agents.agent import AgentRole
        
        # Mock adjacent locations
        mock_locations = [Location(4, 5), Location(6, 5)]
        mock_environment.get_adjacent_locations.return_value = mock_locations
        
        # Create a mock villain
        mock_villain = Mock()
        mock_villain.get_agent_role.return_value = AgentRole.VILLAIN
        mock_villain.get_health.return_value = 0.8
        
        # Mock get_agent to return villain at one location
        def mock_get_agent(location):
            if location.get_x() == 4 and location.get_y() == 5:
                return mock_villain
            return None
        
        mock_environment.get_agent.side_effect = mock_get_agent
        
        actions = human_torch.actions(mock_environment)
        
        # Should include Attack action for the villain
        action_types = [type(action).__name__ for action in actions]
        assert 'Attack' in action_types
    
    def test_actions_with_low_health(self, human_torch, mock_environment):
        """Test actions method when health is low."""
        # Set low health
        human_torch._health = 0.1
        
        # Mock adjacent locations
        mock_locations = [Location(4, 5)]
        mock_environment.get_adjacent_locations.return_value = mock_locations
        
        # Mock get_agent to return None
        mock_environment.get_agent.return_value = None
        
        actions = human_torch.actions(mock_environment)
        
        # Should still return actions even with low health
        assert len(actions) > 0