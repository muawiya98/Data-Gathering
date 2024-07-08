from typing import List
from dataclasses import dataclass

from src.environment.devices.base_station import BaseStation
from src.environment.devices.uav import UAV


@dataclass
class DQNForwardingState:
    uav: UAV
    uavs: List[UAV]
    neighbouring_uavs: List[UAV]
    base_stations: List[BaseStation]
    neighbouring_base_stations: List[BaseStation]

    def __str__(self):
        return f'{self.get()}'

    def can_act(self) -> bool:
        if not self.uav.has_data():
            return False
        if len(self.neighbouring_base_stations) == 0 and len(self.neighbouring_uavs) == 0:
            return False
        return True

    def get(self):
        state = []
        uav_positions = []
        base_stations = []
        uav_energies = []
        for uav in self.uavs:
            uav_energies.append(uav.consumed_energy)
            if uav is self.uav:
                continue
            if uav in self.neighbouring_uavs:
                uav_positions.append(uav.current_point_index)
            else:
                uav_positions.append(-1)
        for base_station in self.base_stations:
            if base_station in self.neighbouring_base_stations:
                base_stations.append(base_station.id)
            else:
                base_stations.append(-1)
        state.append(self.uav.current_point_index)
        state.extend(uav_positions)
        state.extend(base_stations)
        state.append(len(self.uav.data_packets))
        state.extend(uav_energies)
        return state
