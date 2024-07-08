from typing import List, ClassVar
from copy import deepcopy
from dataclasses import dataclass, field
import random

@dataclass
class Environment:
    land_width: float
    land_height: float
    uavs: List['UAV'] = field(default_factory=list)
    sensors: List['Sensor'] = field(default_factory=list)
    base_stations: List['BaseStation'] = field(default_factory=list)
    run_until: int = 100
    time_step: ClassVar[int] = field(init=False, default=0)
    time_stamp: ClassVar[int] = field(init=False)

    def __post_init__(self) -> None:
        self.initial_state = deepcopy(self)

    def get_sensors_in_range(self, uav: 'UAV') -> List['Sensor']:
        sensors = []
        for sensor in self.sensors:
            if uav.position.distance_from(sensor.position) <= uav.coverage_radius:
                sensors.append(sensor)
        return sensors

    def get_uavs_in_range(self, uav: 'UAV') -> List['UAV']:
        uavs = []
        for other_uav in self.uavs:
            if uav == other_uav:
                continue
            if uav.in_range(other_uav):
                uavs.append(other_uav)
        return uavs

    def get_base_stations_in_range(self, uav: 'UAV') -> List['BaseStation']:
        base_stations = []
        for base_station in self.base_stations:
            if uav.in_range(base_station):
                base_stations.append(base_station)
        return base_stations

    def step(self) -> None:
        Environment.time_step += 1
        for uav in self.uavs:
            uav.has_collected = False
            collection_point = uav.get_collection_point()
            sensors_in_range = []
            can_move = True
            if collection_point != -1:
                sensors_in_range = self.get_sensors_in_range(uav)
            if collection_point != -1 and len(sensors_in_range) != 0:
                can_move = False
                uav.collect_data(collection_point, sensors=sensors_in_range)
            if uav.forward_target is not None:
                can_move = False
                uav.forward_data()
            if can_move:
                uav.move()
        for sensor in self.sensors:
            print(random.randint(20, 100))
            sensor.generate_data(random.randint(20, 100))

    # TODO: fancy fix logical assumption: pdr assumes that collection rates
    #  for all UAVs are completely collected
    def calculate_pdr(self) -> float:
        generated_packets = 0
        for uav in self.initial_state.uavs:
            generated_packets += sum(collection_rate for collection_rate in uav.collection_rates)
        if generated_packets == 0:
            return 0
        arrived_packets = sum(len(base_station.data_packets) for base_station in self.base_stations)
        return arrived_packets / generated_packets

    def calculate_end_to_end_delay(self) -> float:
        end_to_end_delay = 0
        arrived_packets = sum(len(base_station.data_packets) for base_station in self.base_stations)
        if arrived_packets == 0:
            return 0
        for base_station in self.base_stations:
            for packet in base_station.data_packets:
                delay = packet.arrival_time - packet.time_of_generation
                if delay < base_station.packet_life_time:
                    end_to_end_delay += delay
        return end_to_end_delay / arrived_packets

    def calculate_energy_consumption(self):
        return sum(uav.consumed_energy for uav in self.uavs)

    def get_performance_matrices(self):
        pdr = self.calculate_pdr()
        delay = self.calculate_end_to_end_delay()
        # energy_consumption = self.calculate_energy_consumption()
        return pdr, delay

    def has_ended(self) -> bool:
        for uav in self.uavs:
            if not uav.has_done():
                return False
        return True

    def reset(self) -> None:
        Environment.time_step = 0
        self.uavs = deepcopy(self.initial_state.uavs)
        self.sensors = deepcopy(self.initial_state.sensors)
        self.base_stations = deepcopy(self.initial_state.base_stations)
