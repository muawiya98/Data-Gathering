import random
from dataclasses import dataclass

from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.environment.core.environment import Environment
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV


@dataclass
class RandomForwarding(ForwardingAlgorithm):
    def __call__(self, uav: UAV) -> Device:
        """
        :param: uav
        :return: random uav in range
        """
        targets = [None]
        if Environment.time_step % self.call_frequency == 0:
            return None
        for base_station in self.env.base_stations:
            if uav.in_range(base_station):
                targets.append(base_station)
        for neighbour_uav in self.env.uavs:
            if neighbour_uav == self:
                continue
            if uav.position.distance_from(neighbour_uav.position) <= uav.coverage_radius:
                targets.append(neighbour_uav)
        return random.choice(targets)
