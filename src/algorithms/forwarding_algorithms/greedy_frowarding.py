from dataclasses import dataclass

from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.environment.core.environment import Environment
from src.environment.devices.device import Device
from src.environment.devices.uav import UAV


@dataclass
class GreedyForwarding(ForwardingAlgorithm):

    def __call__(self, uav: UAV) -> Device:
        """
        :param: uav
        :return: the closest neighbour uav
        """
        target = None
        if Environment.time_step != 0 and Environment.time_step % self.call_frequency == 0:
            return target
        optimal_distance = 1e32
        for base_station in self.env.base_stations:
            if uav.position.distance_from(base_station.position) <= uav.coverage_radius:
                return base_station
        for neighbour_uav in self.env.uavs:
            if neighbour_uav == self:
                continue
            distance = uav.position.distance_from(neighbour_uav.position)
            if distance <= uav.coverage_radius and distance < optimal_distance:
                target = neighbour_uav
                optimal_distance = distance
        return target
