from dataclasses import dataclass, field
from typing import List, Any, Dict

import numpy as np
import random

from src.environment.core.environment import Environment
from src.environment.devices.uav import UAV
from src.environment.devices.base_station import BaseStation

random.seed(42)
np.random.seed(42)

@dataclass
class QLearningForwardingAgent:
    uav: UAV
    env: Environment
    action_size: int
    q_table_size: tuple
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)
    q_table: Any = field(init=False)
    solution_id: int
    gamma: float = 0.90
    alpha: float = 1
    lr: float = 0.01
    epsilon: float = 0.99 # 1
    epsilon_min: float = 0.12
    epsilon_decay: float = 0.00009 # 0.97
    # episode_return: int = 0.2
    episode_return: List = field(init=False, default_factory=list)
    log_enabled: bool = field(init=False, default=False)
    log: Dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.q_table = {} # np.zeros(self.q_table_size)

    # def calculate_return(self, current_data_pre, target, target_data_pre):
    #     alpha = 10
    #     beta = 100
    #     extra = 0
    #     if type(target) == UAV:
    #         extra = target.forward_value
    #     elif type(target) == BaseStation:
    #         extra = beta
    #     if target == self.uav:
    #         return alpha + extra
        
    #     current_uav_data2 = len(self.uav.data_packets)
    #     target_uav_data2 = len(target.data_packets)
    #     pdr = (target_uav_data2 - target_data_pre) / (current_data_pre - current_uav_data2)
    #     return pdr * alpha + extra


    def calculate_return(self, target, available_targets):
        if type(target) == BaseStation:return 100
        elif np.any([type(t) is BaseStation for t in available_targets]):return -100
        else:
            for available_target in available_targets:
                if len(self.env.get_base_stations_in_range(available_target))!=0 and available_target==target:
                    return 10
            if target == self.uav:return 0
        return -10
            

    def get_available_targets(self):
        if not self.uav.has_data():
            return []
        base_stations = self.env.get_base_stations_in_range(self.uav)
        # if len(base_stations) != 0:
        #     return base_stations
        return base_stations + self.env.get_uavs_in_range(self.uav)

    def get_available_actions(self):
        forward_targets = self.get_available_targets()
        actions = []
        for target in forward_targets:
            if type(target) is BaseStation:
                actions.append(len(self.env.uavs) + self.env.base_stations.index(target))
            else:
                actions.append(self.env.uavs.index(target))
        actions.append(self.env.uavs.index(self.uav))
            
        # if len(forward_targets) != 0 and type(forward_targets[0]) is BaseStation:
        #     actions = [len(self.env.uavs) + self.env.base_stations.index(target) for target in forward_targets]
        # else:
        #     actions = [self.env.uavs.index(target) for target in forward_targets]
        #     actions.append(self.env.uavs.index(self.uav))
        return actions, forward_targets


    def choose_action(self):
        available_actions, available_targets = self.get_available_actions()
        if max(available_actions) >= len(self.env.uavs):
            return max(available_actions), available_targets
        return random.choice(available_actions), available_targets

    def choose_best_action(self, state):
        if not tuple(state) in self.q_table.keys():
            self.q_table[tuple(state)] = np.zeros(self.action_size)
        q_values = self.q_table[tuple(state)]
        available_actions, available_targets = self.get_available_actions()
        q_value = -1e18
        action = -1e18
        for available_action in available_actions:
            if available_action >= len(q_values):
                return 0
            if q_values[available_action] > q_value:
                q_value = q_values[available_action]
                action = available_action
        return action, available_targets

    def choose_epsilon_greedy_action(self, state):

        if np.random.rand() < self.epsilon or self.env.time_step<=10:
            actions, available_targets = self.get_available_actions()
            action = random.choice(actions)
        else:
            action, available_targets = self.choose_best_action(state)
        return action, available_targets

    def get_target(self, action):
        if action >= len(self.env.uavs):
            action -= len(self.env.uavs)
            target = self.env.base_stations[action] 
        else:
            target = self.env.uavs[action]
        return target

    def take_forwarding_action(self, action):
        target = self.get_target(action)
        if target != self.uav:
            self.uav.forward_target = target
        self.env.step()

    def update_epsilon(self):
        if self.epsilon >= self.epsilon_min:
            self.epsilon -= self.epsilon*self.epsilon_decay
        # self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def update_q_table(self, state, action, reward, next_state):
        if not tuple(state) in self.q_table.keys():
            self.q_table[tuple(state)] = np.zeros(self.action_size)
        if not tuple(next_state) in self.q_table.keys():
            self.q_table[tuple(next_state)] = np.zeros(self.action_size)
            
        # x1 = self.q_table[tuple(state)][action]
        # x2 = np.max(self.q_table[tuple(next_state)])
        # x = ((1 - self.alpha) * x1) + (self.alpha * (reward + x2))
        # self.q_table[tuple(state)][action] = x

        self.q_table[tuple(state)][action] = ((1 - self.lr) * self.q_table[tuple(state)][action]) + \
                                            (self.lr * (reward + self.gamma * max(self.q_table[tuple(next_state)])))

    def get_current_state(self):
        state = [uav.current_point_index for uav in self.env.uavs]
        state.append(int(self.uav.has_data()))
        return state

    def step(self):
        state = self.get_current_state()
        action, available_targets = self.choose_epsilon_greedy_action(state)
        target = self.get_target(action)

        # current_data_pre = len(self.uav.data_packets)
        # target_data_pre = len(target.data_packets)

        self.take_forwarding_action(action)
        next_state = self.get_current_state()

        # reward = self.calculate_return(current_data_pre, target, target_data_pre)
        reward = self.calculate_return(target, available_targets)

        self.update_q_table(state, action, reward, next_state)
        self.episode_return.append(reward)
        self.update_epsilon()
