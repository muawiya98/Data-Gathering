from dataclasses import dataclass

from src.environment.core.environment import Environment
from src.environment.devices.data_packet import DataPacket
from src.environment.devices.device import Device
import numpy as np
import random



@dataclass(order=True)
class Sensor(Device):
    sampling_rate: int
    capacity: int
    collection_rate: int

    def generate_data(self, collection_rate=None):
        if collection_rate is None:
            collection_rate = self.collection_rate
        if Environment.time_step % self.sampling_rate != 0:
            return
        for _ in range(collection_rate):
            self.data_packets.append(DataPacket(time_of_generation=Environment.time_step))
        if len(self.data_packets) > self.capacity:
            self.data_packets = self.data_packets[:-collection_rate]
