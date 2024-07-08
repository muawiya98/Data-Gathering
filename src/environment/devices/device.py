from dataclasses import dataclass
from typing import List

from src.environment.core.environment import Environment
from src.environment.devices.data_packet import DataPacket
from src.environment.utils.vector import Vector


@dataclass(order=True)
class Device:
    id: int
    position: Vector

    def __post_init__(self):
        self.data_packets: List[DataPacket] = []

    def transfer_data(self, device: 'Device', num_of_packets: int) -> None:
        from src.environment.devices.uav import UAV
        while num_of_packets > 0 and len(self.data_packets) > 0:
            data_packet = self.data_packets.pop(0)
            if isinstance(device, UAV):
                data_packet.route.append(device)
            device.data_packets.append(data_packet)
            num_of_packets -= 1
            if type(device).__name__ == 'BaseStation':
                data_packet.arrival_time = Environment.time_step
                delay = data_packet.arrival_time - data_packet.time_of_generation
                if delay >= device.packet_life_time:
                    device.data_packets.pop()

    def __str__(self) -> str:
        return f'{type(self).__name__}-{self.id}'
