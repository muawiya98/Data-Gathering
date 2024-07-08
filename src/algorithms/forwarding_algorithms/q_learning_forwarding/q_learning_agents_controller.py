import csv
import os
import pickle
from dataclasses import dataclass
from typing import List
from src.algorithms.forwarding_algorithms.q_learning_forwarding.q_learning_forwarding_agent import \
    QLearningForwardingAgent
from src.environment.core.environment import Environment

import numpy as np
import random

random.seed(42)
np.random.seed(42)

@dataclass
class QLearningAgentsController:
    id: int
    forwarding_agents: List[QLearningForwardingAgent]
    env: Environment
    max_steps: int
    num_of_episodes: int
    solution_id: int
    log_behavior_freq: int

    def train_agents(self, agent_sequence):
        trained_agents = []
        for idx in agent_sequence:
            selected_agent = self.forwarding_agents[idx]
            print(f'\ntraining agent-{selected_agent.uav.id}')
            for episode in range(self.num_of_episodes):
                self.env.reset()
                for uav, agent in zip(self.env.uavs, self.forwarding_agents):
                    agent.steps = 0
                    # agent.episode_return = 0
                    agent.episode_return = []
                    agent.uav = uav
                    if episode != 0 and episode % self.log_behavior_freq == 0:
                        agent.log_enabled = True
                steps = 0
                while not self.env.has_ended() and steps <= self.max_steps:
                    print(f'\r>Episode: {episode + 1} / {self.num_of_episodes}, Step: {steps} / {self.max_steps}',
                          end='')
                    steps += 1
                    self.env.step()
                    for i, agent in enumerate(self.forwarding_agents):
                        if agent.uav.has_collected:
                            if agent == selected_agent:
                                agent.step()
                            elif agent in trained_agents:
                                state = agent.get_current_state()
                                action, available_targets = agent.choose_best_action(state)
                                agent.take_forwarding_action(action)
                            else:
                                action, available_targets = agent.choose_action()
                                agent.take_forwarding_action(action)
                selected_agent.episodes_rewards.append(np.mean(selected_agent.episode_return))
                selected_agent.uav.forward_value = max(selected_agent.episodes_rewards)
            trained_agents.append(selected_agent)
        self.log_results()
        self.save_models()

    def save_models(self):
        current_dir = os.getcwd()
        experiment_dir = os.path.join(current_dir, 'data', 'experiments', f'experiment_{self.solution_id}', 'output', f'{self.id}')
        path = os.path.join(experiment_dir, 'model')
        if not os.path.exists(path):
            os.mkdir(path)
        for agent in self.forwarding_agents:
            with open(os.path.join(path, f'agent-{agent.uav.id}.pkl'), 'wb') as file:
                pickle.dump(agent, file)

    def log_results(self):
        current_dir = os.getcwd()
        experiment_dir = os.path.join(current_dir, 'data', 'experiments', f'experiment_{self.solution_id}', 'output', f'{self.id}')
        if not os.path.isdir(experiment_dir):
            os.mkdir(experiment_dir)
        file_path = os.path.join(experiment_dir, 'agent_rewards.csv')
        for agent in self.forwarding_agents:
            for i, _ in enumerate(agent.episodes_rewards):
                agent.episodes_rewards[i] = round(agent.episodes_rewards[i], 3)
        transposed_values = list(map(list, zip(*[agent.episodes_rewards for agent in self.forwarding_agents])))
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            header = [f'agent-{i + 1}' for i in range(len(self.forwarding_agents))]
            writer.writerow(header)
            for values in transposed_values:
                writer.writerow(values)
        log_path = os.path.join(experiment_dir, 'behavior')
        for i, agent in enumerate(self.forwarding_agents):
            if not os.path.isdir(log_path):
                os.mkdir(log_path)
            for episode, log in agent.log.items():
                path = os.path.join(log_path, f'episode-{episode + 1}-agent-{i + 1}.csv')
                with open(path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    header = ['step', 'time', 'state', 'action', 'next state', 'reward']
                    writer.writerow(header)
                    for row in log:
                        writer.writerow(row)
