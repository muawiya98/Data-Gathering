from dataclasses import dataclass, field
from typing import List

from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.algorithms.forwarding_algorithms.dqn_forwarding.dqn_forwarding_agent import DQNForwardingAgent
from src.environment.core.environment import Environment
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV


@dataclass
class DQNForwarding(ForwardingAlgorithm):
    agents: List[DQNForwardingAgent] = field(default_factory=list)
    call_frequency: int = 1

    def __call__(self, uav: UAV) -> Device | None:
        """
        :param: uav
        :return: the appropriate uav based on the DQN model.
        """
        if Environment.time_step != 0 and Environment.time_step % self.call_frequency == 0:
            return None
        idx = self.env.uavs.index(uav)
        agent = self.agents[idx]
        current_state = agent.get_current_state(
            uavs_in_range=self.env.get_uavs_in_range(agent.uav),
            uavs=self.env.uavs,
            neighbouring_base_stations=self.env.get_base_stations_in_range(agent.uav),
            base_stations=self.env.base_stations
        )
        if not current_state.can_act():
            return None
        action = agent.choose_best_action(current_state.get())
        if action == agent.pass_action:
            return None
        if action < len(self.env.base_stations):
            target = self.env.base_stations[action]
        else:
            target = self.env.uavs[action - len(self.env.base_stations)]
        return target
