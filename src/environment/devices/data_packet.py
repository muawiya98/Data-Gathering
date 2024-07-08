from typing import List
from dataclasses import dataclass, field


@dataclass
class DataPacket:
    time_of_generation: int
    arrival_time: int = -1
    route: List['UAV'] = field(default_factory=list)

    @property
    def id(self):
        return hash(self)
