class HeroConfig:
    """Class representing configuration parameters for a general hero agent."""
    
    # scan radius
    scan_radius = 1

    # bridge repairing rate
    bridge_repair_rate = 0.2

    # default attack rate
    attack_rate = 0.1

    # default heal rate
    heal_rate = 0.05

    # attack health reduce
    attack_health_reduce = None

    # damage receiving rate
    damage_rate = 1.0

    # close range attack rate
    close_attack_rate = None

    # health consumption for ranged attacks
    ranged_attack_health_reduce = None

    # attack efficacy rate reduction on the basis of distance
    ranged_attack_effect = None

    # protective barrier range
    barrier_range = 1 # every hero can protect a cell


class ReedRichardConfig(HeroConfig):
    """Class representing configuration parameters for Reed Richards agent."""
    # higher scan radius for RR
    scan_radius = 3


class SueStormConfig(HeroConfig):
    """Class representing configuration parameters for Sue Storm agent."""

    # protective barrier range, width by height, widht = height
    barrier_range = 3


class HumanTorchConfig(HeroConfig):
    """Class representing configuration parameters for Human Torch agent."""

    # higher scan radius for HT
    scan_radius = 5

    # extra energy consumed for ranged attacks, per usage rate
    ranged_attack_health_reduce = 0.02

    # attack efficacy rate reduction on the basis of distance, efficacy reduced by 0.001 per cell
    ranged_attack_effect = 0.001

class TheThingConfig(HeroConfig):
    """Class representing configuration parameters for The Thing agent."""

    # attack rate for close range
    close_attack_rate = 0.2

    # faster physical repairs than others
    bridge_repair_rate = 0.4
