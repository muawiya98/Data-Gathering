from dataclasses import dataclass

from src.environment.devices.device import Device


@dataclass(order=True)
class BaseStation(Device):
    packet_life_time: int

    def __hash__(self):
        return hash(self.id)
