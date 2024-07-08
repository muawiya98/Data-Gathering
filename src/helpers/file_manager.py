import os
from dataclasses import dataclass
from typing import Any, List, Tuple

import pandas as pd
from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation
from src.environment.devices.sensor import Sensor
from src.environment.devices.uav import UAV
from src.environment.utils.vector import Vector
import random


@dataclass
class FileManager:
    """
    reads the solution input data from the dir [{current_dir}/data/experiments/experiment_{self.solution_id}/input/]
    """
    solution_id: int

    def __post_init__(self):
        current_dir = os.getcwd()
        self.input_dir = os.path.join(current_dir, 'data', 'experiments', f'experiment_{self.solution_id}', 'input')

    def read_data_frame(self, name: str) -> Any:
        if len(name) <= 4 or name[-4:] != '.csv':
            name += '.csv'
        return pd.read_csv(os.path.join(self.input_dir, name))

    def load_basic_variables(self) -> Tuple:
        df = self.read_data_frame(name='environment_basics')
        assert len(
            list(df.iterrows())) == 1, 'environment_basics should not contains more than one row'
        data = []
        for index, row in df.iterrows():
            data.append((row['width'], row['height'], row['run until']))
        return data[0]

    def load_sensors(self) -> List[Sensor]:
        sensors = []
        df = self.read_data_frame(name='sensors.csv')
        for index, row in df.iterrows():
            id = int(str(index)) + 1
            position = Vector(row['x'], row['y'], row['z'])
            initial_data = random.randint(5, 50) # int(row['initial data packets'])
            capacity = random.randint(500, 1000) #row['capacity']
            sampling_rate = random.randint(5, 10) # row['sampling rate']
            collection_rate = random.randint(5, 50) #int(row['collection rate'])
            sensor = Sensor(id=id, position=position, sampling_rate=sampling_rate, capacity=capacity,
                            collection_rate=collection_rate)
            sensor.generate_data(initial_data)
            sensors.append(sensor)
        return sensors

    def load_base_stations(self) -> List[BaseStation]:
        base_stations = []
        df = self.read_data_frame(name='base_stations.csv')
        for index, row in df.iterrows():
            id = int(str(index)) + 1
            position = Vector(row['x'], row['y'], row['z'])
            packet_life_time = row['packet life time']
            base_station = BaseStation(id=id, position=position, packet_life_time=packet_life_time)
            base_stations.append(base_station)
        return base_stations

    def load_uavs(self) -> List[UAV]:
        uavs = []
        uav_df = self.read_data_frame(name='uavs.csv')
        way_points_df = self.read_data_frame(name='way_points.csv')
        for index, row in uav_df.iterrows():
            id = int(str(index)) + 1
            position = Vector(row['x'], row['y'], row['z'])
            speed = row['speed']
            coverage_radius = row['coverage radius']
            uav = UAV(id=id, position=position, speed=speed, coverage_radius=coverage_radius, collection_rates=[])
            uavs.append(uav)
        for index, row in way_points_df.iterrows():
            position = Vector(row['x'], row['y'], row['z'])
            collection_rate = random.randint(5, 50) # row['collection rate']
            id = int(row['uav id'])
            found = None
            for uav in uavs:
                if uav.id == id:
                    found = uav
                    break
            found.path.append(position)
            found.collection_rates.append(collection_rate)
        return uavs

    def load_environment(self) -> Environment:
        height, width, run_until = self.load_basic_variables()
        uavs = self.load_uavs()
        sensors = self.load_sensors()
        base_stations = self.load_base_stations()
        return Environment(land_height=height, land_width=width, uavs=uavs, sensors=sensors,
                           base_stations=base_stations, run_until=run_until)
