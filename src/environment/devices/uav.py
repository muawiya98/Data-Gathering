import math
from typing import List

from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.models.energy_model import EnergyModel
from src.environment.utils.vector import Vector

from copy import deepcopy
import numpy as np
import random

random.seed(42)
np.random.seed(42)

@dataclass(order=True)
class UAV(Device):
    speed: int
    coverage_radius: int
    collection_rates: List[int]
    path: List[Vector] = field(default_factory=list)
    current_point_index: int = 0
    consumed_energy: int = 0
    forward_target: Device = None
    has_collected: bool = False
    forward_value: int = 0

    def move(self) -> None:
        if self.current_point_index == len(self.path) - 1:
            return
        p1 = self.path[self.current_point_index]
        p2 = self.path[self.current_point_index + 1]
        d = p1.distance_from(p2)
        step = self.speed / d
        x_dir, y_dir, z_dir = 1, 1, 1
        if p1.x > p2.x:
            x_dir = -1
        if p1.y > p2.y:
            y_dir = -1
        if p1.z > p2.z:
            z_dir = -1
        self.position.x += abs(p2.x - p1.x) * step * x_dir
        self.position.y += abs(p2.y - p1.y) * step * y_dir
        self.position.z += abs(p2.z - p1.z) * step * z_dir
        if math.copysign(1, self.position.x - p2.x) != math.copysign(1, p1.x - p2.x):
            self.current_point_index += 1
            self.path[self.current_point_index] = deepcopy(self.position)

    def get_collection_point(self):
        for point in self.path:
            if self.position.distance_from(point) <= self.speed:
                if self.collection_rates[self.path.index(point)] > 0:
                    return self.path.index(point)
                break
        return -1

    def has_done(self):
        if self.current_point_index != len(self.collection_rates) - 1:
            return False
        return self.collection_rates[self.current_point_index] <= 0

    # def forwarded_for(self, device: 'Device') -> bool:
    #     return device in self.forwarded_previously

    def collect_data(self, collection_point: int, sensors: List['Sensor']) -> None:
        self.has_collected = True
        for sensor in sensors:
            if self.collection_rates[collection_point] <= 0:
                return
            # TODO: fancy remove this magic number
            # TODO: notice
            sensor.transfer_data(device=self, num_of_packets=1)
            # self.transfer_data(device=sensor, num_of_packets=1)
            self.collection_rates[collection_point] -= 1

    def transfer_data(self, device: 'Device', num_of_packets: int) -> None:
        super().transfer_data(device, num_of_packets)
        self.consume_energy(transition_distance=self.position.distance_from(device.position),
                            num_of_packets=num_of_packets)

    def consume_energy(self, transition_distance: float, num_of_packets: int):
        self.consumed_energy += EnergyModel.calculate_consumed_energy(transition_distance, num_of_packets)

    def forward_data(self) -> None:
        self.transfer_data(self.forward_target, num_of_packets=len(self.data_packets))
        self.forward_target = None

    def has_data(self):
        return len(self.data_packets) > 0

    def in_range(self, other):
        return self.position.distance_from(other.position) <= self.coverage_radius
