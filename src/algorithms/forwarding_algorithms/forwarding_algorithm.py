from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.environment.core.environment import Environment
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV


@dataclass
class ForwardingAlgorithm:
    env: Environment
    call_frequency: int = field(default=5)

    @abstractmethod
    def __call__(self, uav: UAV) -> Device:
        """
        implement this method to create a new forwarding algorithm
        the algorithm should have the following input and output
        :param uav:
        :return: the forwarding target according to your policy
        """
        pass

    def __str__(self):
        return f'{self.__class__.__name__}'
