from dataclasses import dataclass

from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV


@dataclass
class NoForwarding(ForwardingAlgorithm):
    def __call__(self, uav: UAV) -> Device:
        return None
