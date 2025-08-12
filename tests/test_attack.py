import pytest
from unittest.mock import Mock
from model.actions.attack import Attack
from model.location import Location
from model.environment import Environment
from model.agents.agent import Agent, AgentRole

class TestAttack:
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent for testing."""
        agent = Mock(spec=Agent)
        agent.get_location.return_value = Location(5, 5)
        agent.attack_rate = 0.2
        return agent
    
    @pytest.fixture
    def mock_environment(self):
        """Create a mock environment for testing."""
        env = Mock(spec=Environment)
        env.get_grid.return_value = [[None] * 20 for _ in range(20)]
        return env
    
    def test_initialization(self, mock_agent):
        """Test that Attack action initializes correctly."""
        target_location = Location(6, 5)
        attack_action = Attack(target_location, mock_agent)
        
        assert attack_action._location == target_location
        assert attack_action._agent == mock_agent
    
    def test_execute_attack_on_villain(self, mock_agent, mock_environment):
        """Test executing an attack on a villain."""
        target_location = Location(6, 5)
        attack_action = Attack(target_location, mock_agent)
        
        # Create a mock villain
        mock_villain = Mock(spec=Agent)
        mock_villain.get_agent_role.return_value = AgentRole.VILLAIN
        mock_villain.damage_rate = 1.0
        
        # Mock get_agent to return the villain
        mock_environment.get_agent.return_value = mock_villain
        
        result = attack_action.execute(mock_environment)
        
        # Verify villain's health was reduced
        mock_villain.reduce_health.assert_called_with(0.2)  # attack_rate * damage_rate
        
        # Should return positive reward for attacking villain
        assert result == 3
    
    def test_execute_attack_on_hero(self, mock_agent, mock_environment):
        """Test executing an attack on a hero."""
        target_location = Location(6, 5)
        attack_action = Attack(target_location, mock_agent)
        
        # Create a mock hero
        mock_hero = Mock(spec=Agent)
        mock_hero.get_agent_role.return_value = AgentRole.HERO
        mock_hero.damage_rate = 1.0
        
        # Mock get_agent to return the hero
        mock_environment.get_agent.return_value = mock_hero
        
        result = attack_action.execute(mock_environment)
        
        # Verify hero's health was reduced
        mock_hero.reduce_health.assert_called_with(0.2)  # attack_rate * damage_rate
        
        # Should return negative reward for attacking hero
        assert result == -3
    
    def test_execute_attack_on_empty_location(self, mock_agent, mock_environment):
        """Test executing an attack on an empty location."""
        target_location = Location(6, 5)
        attack_action = Attack(target_location, mock_agent)
        
        # Mock get_agent to return None (empty location)
        mock_environment.get_agent.return_value = None
        
        result = attack_action.execute(mock_environment)
        
        # No health reduction should occur
        assert not mock_agent.reduce_health.called
        
        # Should return 0 reward for attacking empty location
        assert result == 0