from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.algorithms.forwarding_algorithms.q_learning_forwarding.q_learning_forwarding_agent import \
    QLearningForwardingAgent
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV

from typing import List
from dataclasses import dataclass, field


@dataclass
class QLearningForwarding(ForwardingAlgorithm):
    agents: List[QLearningForwardingAgent] = field(default_factory=list)

    def __call__(self, uav: UAV):# -> Device | None:
        idx = self.env.uavs.index(uav)
        agent = self.agents[idx]
        if agent.uav.has_collected:
            state = agent.get_current_state()
            action, _ = agent.choose_best_action(state)
            target = agent.get_target(action)
            if target != uav:
                print(f'Action taken: forward from {uav} to {target}')
                return target
