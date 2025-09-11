import pytest
from unittest.mock import Mock, patch
from model.agents.galactus import Galactus
from model.location import Location
from model.environment import Environment
from model.actions.move import Move
from model.agents.agent import AgentRole

class TestGalactus:
    
    @pytest.fixture
    def galactus(self):
        """Create a Galactus instance for testing."""
        return Galactus(Location(10, 10))
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        env = Mock(spec=Environment)
        env.get_grid.return_value = [[None] * 20 for _ in range(20)]
        return env
    
    def test_initialization(self, galactus):
        """Test that Galactus initializes correctly."""
        assert galactus._location.get_x() == 10
        assert galactus._location.get_y() == 10
        assert galactus._role.name == "VILLAIN"
        assert galactus._health == 1.0
        assert hasattr(galactus, 'attack_rate')
        assert hasattr(galactus, 'damage_rate')
    
    def test_next_location_calculation(self, galactus):
        """Test the next location calculation logic."""
        # Create mock bridges and Franklin
        bridges = [Location(5, 5), Location(15, 5), Location(5, 15), Location(15, 15)]
        franklin = Location(8, 8)
        
        # Test the next location calculation
        next_loc = galactus._Galactus__next_location(bridges, franklin)
        
        # Should return a valid Location
        assert isinstance(next_loc, Location)
        assert 0 <= next_loc.get_x() < 20
        assert 0 <= next_loc.get_y() < 20
    
    @patch('model.agents.galactus.WorldConfig')
    def test_actions_with_franklin(self, mock_config, galactus, mock_environment):
        """Test actions when Franklin is present."""
        mock_config.world_size = 20
        
        # Mock environment to return Franklin
        from model.agents.franklin import Franklin
        
        mock_franklin = Mock(spec=Franklin)
        mock_franklin.get_agent_role.return_value = AgentRole.FRANKLIN
        mock_franklin.get_location.return_value = Location(8, 8)
        
        # Mock environment grid to include Franklin
        mock_grid = [[None] * 20 for _ in range(20)]
        mock_grid[8][8] = mock_franklin
        mock_environment.get_grid.return_value = mock_grid
        
        # Mock bridges
        from model.agents.bridge import Bridge
        
        mock_bridges = []
        for x, y in [(5, 5), (15, 5), (5, 15), (15, 15)]:
            mock_bridge = Mock(spec=Bridge)
            mock_bridge.get_agent_role.return_value = AgentRole.BRIDGE
            mock_bridge.get_location.return_value = Location(x, y)
            mock_bridges.append(mock_bridge)
            mock_grid[y][x] = mock_bridge
        
        # Mock get_agent to return appropriate agents
        def mock_get_agent(location):
            x, y = location.get_x(), location.get_y()
            if 0 <= x < 20 and 0 <= y < 20:
                return mock_grid[y][x]
            return None
        
        mock_environment.get_agent.side_effect = mock_get_agent
        
        actions = galactus.actions(mock_environment)
        
        # Should return a Move action
        assert len(actions) == 1
        assert isinstance(actions[0], Move)