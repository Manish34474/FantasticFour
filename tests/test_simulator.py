import pytest
from unittest.mock import Mock, patch
from simulator import Simulator
from model.earth import Earth
from model.location import Location
from model.agents.reed_richards import ReedRichards
from model.agents.sue_storm import SueStorm
from model.agents.human_torch import HumanTorch
from model.agents.bridge import Bridge
from controller.config.config import Config

class TestSimulator:
    
    @pytest.fixture
    def simulator(self):
        """Create a simulator instance for testing."""
        return Simulator()
    
    def test_initialization(self, simulator):
        """Test that simulator initializes correctly."""
        assert simulator._Simulator__simulation_step == 0
        assert isinstance(simulator._Simulator__earth, Earth)
        assert isinstance(simulator._Simulator__agents, list)
        assert not simulator._Simulator__is_running
    
    def test_generate_initial_population(self, simulator):
        """Test that initial population is generated correctly."""
        # Clear any existing agents
        simulator._Simulator__agents = []
        simulator._Simulator__earth.clear()
        
        # Generate population
        simulator._Simulator__generate_initial_population()
        
        # Check that agents were created
        assert len(simulator._Simulator__agents) > 0
        
        # Check that specific agent types exist
        agent_types = [type(agent).__name__ for agent in simulator._Simulator__agents]
        assert 'Bridge' in agent_types
        assert 'ReedRichards' in agent_types
        assert 'SueStorm' in agent_types
        assert 'HumanTorch' in agent_types
        assert 'Franklin' in agent_types
        assert 'Headquarter' in agent_types
    
    def test_find_empty_locations(self, simulator):
        """Test finding empty locations."""
        # Clear the grid
        simulator._Simulator__earth.clear()
        
        # Test finding empty location with radius 0
        empty_loc = simulator._Simulator__find_empty_locations(r=0)
        assert empty_loc is not None
        assert isinstance(empty_loc, Location)
        
        # Test with a larger radius
        empty_loc = simulator._Simulator__find_empty_locations(r=1)
        assert empty_loc is not None
    
    @patch('simulator.SilverSurfer')
    @patch('simulator.Galactus')
    def test_add_silver_surfer_and_galactus(self, mock_galactus, mock_silver_surfer, simulator):
        """Test adding Silver Surfer and Galactus."""
        # Mock the empty location finding
        mock_location = Location(10, 10)
        simulator._Simulator__find_empty_locations = Mock(return_value=mock_location)
        
        # Mock the agent classes
        mock_silver_surfer_instance = Mock()
        mock_silver_surfer.return_value = mock_silver_surfer_instance
        mock_galactus_instance = Mock()
        mock_galactus.return_value = mock_galactus_instance
        
        # Test adding Silver Surfer
        simulator._Simulator__add_silver_surfer()
        mock_silver_surfer.assert_called_with(mock_location)
        assert mock_silver_surfer_instance in simulator._Simulator__agents
        
        # Test adding Galactus
        simulator._Simulator__add_galactus()
        mock_galactus.assert_called_with(mock_location)
        assert mock_galactus_instance in simulator._Simulator__agents
    
    def test_run_method_starts(self, simulator):
        """Test that run method sets the running flag."""
        # Mock the update method to avoid infinite loop
        simulator._Simulator__update = Mock(return_value=(0, 0))
        simulator._Simulator__gui = Mock()
        simulator._Simulator__gui.is_closed.return_value = True
        
        # Run the simulation briefly
        simulator.run()
        
        # Check that running flag was set
        assert simulator._Simulator__is_running