from __future__ import annotations

from model.agents.agent import Agent, AgentRole
from model.actions.action import Action

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.environment import Environment
    from model.location import Location


class Attack(Action):
    """
    Represents an attack action in the environment.
    """

    def __init__(self, attack_location: Location, agent: Agent) -> None:
        """
        Initialize the attack action with a target location.

        :param attack_location: The location where the attack is to be executed.
        """
        super().__init__(attack_location, agent)


    def execute(self, environment: Environment) -> None:
        """
        Execute the attack action in the given environment at the specified location.

        :param environment: The environment in which the action is executed.
        :param agent: The agent performing the attack.
        """
        import math

        target_agent = environment.get_agent(self._location)
        reward = 0

        is_target_villain = 0 if target_agent is None else 1 if target_agent.get_agent_role() is AgentRole.VILLAIN else -1

        attack_rate = self._agent.attack_rate

        if hasattr(self._agent, "close_attack_rate") and self._agent.close_attack_rate is not None:
            attack_rate = self._agent.close_attack_rate
        
        if hasattr(self._agent, "ranged_attack_effect") and self._agent.ranged_attack_effect is not None:
            distance = math.ceil(self._location.dist(self._agent.get_location()))
            if(distance > 1):
                attack_rate -= self._agent.ranged_attack_effect * distance
                self._agent.reduce_health(self._agent.ranged_attack_health_reduce)
                reward = 3 * is_target_villain

        if hasattr(self._agent, "attack_health_reduce") and self._agent.attack_health_reduce is not None:
            self._agent.reduce_health(self._agent.attack_health_reduce)
            reward = 3 * is_target_villain


        if target_agent is not None:
            damage_rate = target_agent.damage_rate if target_agent.damage_rate is not None else 1.0
            target_agent.reduce_health(self._agent.attack_rate * damage_rate)
            reward = 3 * is_target_villain

        return reward

        
