import os
from dataclasses import dataclass, field
from typing import List, Any, Dict

import numpy as np
import random

from src.algorithms.forwarding_algorithms.dqn_forwarding.state import DQNForwardingState
from src.environment.core.environment import Environment
from src.environment.devices.base_station import BaseStation
from src.environment.devices.uav import UAV

import tensorflow as tf


@dataclass
class DQNForwardingAgent:
    uav: UAV
    env: Environment
    action_size: int
    steps: int = field(init=False, default=0)
    episodes_rewards: List = field(init=False, default_factory=list)
    model: Any = field(init=False)
    target_model: Any = field(init=False)
    memory: List = field(init=False, default_factory=list)
    state_dim: int
    solution_id: int
    save_weights: bool
    load_from: str = None
    checkpoint_freq: int = 32
    target_update_freq: int = 2
    gamma: float = 0.95
    batch_size: int = 32
    epsilon: float = 1
    epsilon_min: float = 0
    epsilon_decay: float = 0.97
    episode_return: int = 0
    cp_callbacks: List = field(default_factory=list)
    log_enabled: bool = field(init=False, default=False)
    log: Dict = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.model = self.create_model()
        self.target_model = tf.keras.models.clone_model(self.model)
        self.pass_action = self.action_size - 1
        if self.save_weights:
            checkpoint_path = self.get_checkpoint_path(file_id=Environment.time_stamp)
            cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                             save_weights_only=True,
                                                             verbose=0)
            self.cp_callbacks = [cp_callback]
        if self.load_from is not None:
            self.model.load_weights(self.get_checkpoint_path(file_id=self.load_from))

    def get_checkpoint_path(self, file_id):
        current_dir = os.getcwd()
        path = f'{current_dir}/data/experiments/experiment_{self.solution_id}/output/'
        if not os.path.isdir(path):
            os.mkdir(path)
        path += f'{file_id}/'
        if not os.path.isdir(path):
            os.mkdir(path)
        path += 'model'
        if not os.path.isdir(path):
            os.mkdir(path)
        checkpoint_path = f'{path}/agent-{self.uav.id}-model.h5'
        return checkpoint_path

    def create_model(self):
        num_units = 24
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Dense(num_units, input_shape=(self.state_dim,), activation='relu'))
        model.add(tf.keras.layers.Dense(num_units, activation='relu'))
        model.add(tf.keras.layers.Dense(self.action_size))
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam())
        return model

    def get_current_state(self, uavs_in_range: list, uavs: list, base_stations: list, neighbouring_base_stations: list):
        return DQNForwardingState(uav=self.uav, neighbouring_uavs=uavs_in_range, uavs=uavs,
                                  neighbouring_base_stations=neighbouring_base_stations, base_stations=base_stations)

    def calculate_return(self):
        # TODO: fancy remove magic numbers
        # TODO: add the percentage of delivery of packets to the reward
        # TODO: add energy consumption
        alpha, beta, gamma = 11, 30, 0.01
        energy_return, delay_return, pdr_return = 0, 0, 0
        energy_return -= self.uav.consumed_energy / alpha
        for i, base_station in enumerate(self.env.base_stations):
            for data_packet in base_station.data_packets:
                if data_packet.arrival_time == Environment.time_step:
                    if self.uav in data_packet.route:
                        pdr_return += beta
                        delay_return -= (data_packet.arrival_time - data_packet.time_of_generation) * gamma
        total_return = pdr_return
        return total_return

    def get_available_targets(self) -> list['Device']:
        if not self.uav.has_data():
            return []
        base_stations = self.env.get_base_stations_in_range(self.uav)
        if len(base_stations) != 0:
            return base_stations
        return self.env.get_uavs_in_range(self.uav)

    def get_available_actions(self) -> List[int]:
        forward_targets = self.get_available_targets()
        actions = [self.pass_action]
        if len(forward_targets) == 0:
            return actions
        if type(forward_targets[0]) is BaseStation:
            for base_station in forward_targets:
                actions.append(self.env.base_stations.index(base_station))
        else:
            for uav in forward_targets:
                actions.append(self.env.uavs.index(uav) + len(self.env.base_stations))
        return actions

    # TODO: fix reward
    def choose_best_action(self, state):
        q_values = self.model.predict(np.array([state]), verbose=0)[0]
        available_actions = self.get_available_actions()
        q_value = -1e18
        action = -1e18
        for available_action in available_actions:
            if q_values[available_action] > q_value:
                q_value = q_values[available_action]
                action = available_action
        return action

    def choose_epsilon_greedy_action(self, state):
        if np.random.rand() < self.epsilon:
            actions = self.get_available_actions()
            action = random.choice(actions)
        else:
            action = self.choose_best_action(state)
        return action

    def take_forwarding_action(self, action):
        if action == self.pass_action:
            return
        if action < len(self.env.base_stations):
            target = self.env.base_stations[action]
        else:
            target = self.env.uavs[action - len(self.env.base_stations)]
        self.uav.forward_target = target
        self.env.step()

    def update_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def remember(self, state, action, reward, next_state):
        self.memory.append([state, action, reward, next_state])

    def log_behavior(self, episode, current_state, action, reward, next_state):
        if not self.log_enabled:
            return
        if self.log.get(episode) is None:
            self.log[episode] = []
        current_s, next_s = '', ''
        for i, j in zip(current_state, next_state):
            current_s += f'{round(i, 3)} '
            next_s += f'{round(j, 3)} '
        self.log[episode].append([self.steps, Environment.time_step, current_s, action,
                                  next_s, round(reward, 3)])

    def update_target_network(self):
        if self.steps % self.target_update_freq == 0:
            self.target_model.set_weights(self.model.get_weights())

    def replay(self):
        if len(self.memory) > self.batch_size:
            experience_sample = random.sample(self.memory, self.batch_size)
            x = np.array([e[0] for e in experience_sample])
            y = self.model.predict(x, verbose=0)
            x2 = np.array([e[3] for e in experience_sample])
            q2 = self.gamma * np.max(self.target_model.predict(x2, verbose=0), axis=1)
            for i, (s, a, r, s2) in enumerate(experience_sample):
                y[i][a] = r + q2[i]
            self.model.fit(x, y, batch_size=self.batch_size, epochs=1, verbose=0,
                           callbacks=self.cp_callbacks)
            for layer in self.model.layers:
                for weight in layer.weights:
                    weight_name = weight.name.replace(':', '_')
                    tf.summary.histogram(weight_name, weight, step=self.steps)

    def step(self, episode):
        current_state = self.get_current_state(
            uavs_in_range=self.env.get_uavs_in_range(self.uav),
            uavs=self.env.uavs,
            neighbouring_base_stations=self.env.get_base_stations_in_range(self.uav),
            base_stations=self.env.base_stations
        )
        if not current_state.can_act():
            return
        self.steps += 1
        current_state = current_state.get()
        action = self.choose_epsilon_greedy_action(current_state)
        self.take_forwarding_action(action)
        next_state = self.get_current_state(
            uavs_in_range=self.env.get_uavs_in_range(self.uav),
            uavs=self.env.uavs,
            neighbouring_base_stations=self.env.get_base_stations_in_range(self.uav),
            base_stations=self.env.base_stations
        )
        next_state = next_state.get()
        reward = self.calculate_return()
        self.remember(current_state, action, reward, next_state)
        self.episode_return += reward
        self.replay()
        self.update_target_network()
        self.update_epsilon()
        self.log_behavior(episode, current_state, action, reward, next_state)
