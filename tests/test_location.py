import pytest
from model.location import Location
from controller.config.config import Config

@pytest.fixture
def loc1():
    return Location(5, 5)

@pytest.fixture
def loc2():
    return Location(6, 6)

def test_init(loc1):
    assert loc1.get_x() == 5
    assert loc1.get_y() == 5
    assert loc1.get_range() == 0

def test_init_with_range():
    loc = Location(10, 10, range=2)
    assert loc.get_x() == 10
    assert loc.get_y() == 10
    assert loc.get_range() == 2

def test_eq(loc1, loc2):
    assert loc1 == Location(5, 5)
    assert loc1 != loc2

def test_repr(loc1):
    assert repr(loc1) == "Location(5, 5)"

def test_str(loc1):
    assert str(loc1) == "Located at (5, 5)"

def test_set_x(loc1):
    loc1.set_x(10)
    assert loc1.get_x() == 10

def test_set_y(loc1):
    loc1.set_y(15)
    assert loc1.get_y() == 15

def test_set_range(loc1):
    loc1.set_range(1)
    assert loc1.get_range() == 1

def test_dist(loc1):
    # Test distance to itself
    assert loc1.dist(loc1) == 0

    # Test straight line distance
    loc_straight = Location(5, 8)
    assert loc1.dist(loc_straight) == 3

    # Test diagonal distance
    loc_diag = Location(7, 7)
    assert loc1.dist(loc_diag) == 2

    # Test wraparound distance
    world_size = Config.world_size
    loc_wrapped_x = Location(world_size - 1, 5)
    assert loc1.dist(loc_wrapped_x) == 6

    loc_wrapped_y = Location(5, world_size - 1)
    assert loc1.dist(loc_wrapped_y) == 6

    loc_wrapped_both = Location(world_size - 1, world_size - 1)
    assert loc1.dist(loc_wrapped_both) == 6

def test_get_points():
    # Test points for a location with range 0
    loc_range_0 = Location(5, 5)
    points_0 = loc_range_0.get_points()
    assert len(points_0) == 1
    assert points_0[0] == loc_range_0

    # Test points for a location with range 1
    loc_range_1 = Location(1, 1, range=1)
    points_1 = loc_range_1.get_points()
    assert len(points_1) == 9
    expected_points = {
        Location(0, 0), Location(0, 1), Location(0, 2),
        Location(1, 0), Location(1, 1), Location(1, 2),
        Location(2, 0), Location(2, 1), Location(2, 2)
    }
    assert set(points_1) == expected_points

    # Test points with wraparound
    world_size = Config.world_size
    loc_wrapped = Location(world_size - 1, world_size - 1, range=1)
    points_wrapped = loc_wrapped.get_points()
    assert len(points_wrapped) == 9
    expected_wrapped_points = {
        Location(world_size - 2, world_size - 2), Location(world_size - 2, world_size - 1), Location(world_size - 2, 0),
        Location(world_size - 1, world_size - 2), Location(world_size - 1, world_size - 1), Location(world_size - 1, 0),
        Location(0, world_size - 2), Location(0, world_size - 1), Location(0, 0)
    }
    assert set(points_wrapped) == expected_wrapped_points
