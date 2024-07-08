import csv
import os
from dataclasses import dataclass
from typing import List

from src.algorithms.forwarding_algorithms.dqn_forwarding.dqn_forwarding_agent import DQNForwardingAgent
from src.environment.core.environment import Environment


@dataclass
class DQNAgentsController:
    id: int
    forwarding_agents: List[DQNForwardingAgent]
    env: Environment
    max_steps: int
    num_of_episodes: int
    solution_id: int
    log_behavior_freq: int
    skip_range: int = 1

    def train_agents(self):
        for episode in range(self.num_of_episodes):
            self.env.reset()
            for uav, agent in zip(self.env.uavs, self.forwarding_agents):
                agent.steps = 0
                agent.episode_return = 0
                agent.uav = uav
                if episode != 0 and episode % self.log_behavior_freq == 0:
                    agent.log_enabled = True
            steps = 0
            while not self.env.has_ended() and steps <= self.max_steps:
                print(f'\r>Episode: {episode + 1} / {self.num_of_episodes}, Step: {steps} / {self.max_steps}', end='')
                steps += 1
                for _ in range(self.skip_range):
                    self.env.step()
                for i, agent in enumerate(self.forwarding_agents):
                    agent.step(episode)
                self.env.step()
            for i, agent in enumerate(self.forwarding_agents):
                agent.replay()
                agent.update_target_network()
                agent.episodes_rewards.append(agent.episode_return)
        self.log_results()

    def log_results(self):
        current_dir = os.getcwd()
        experiment_dir = f'{current_dir}/data/experiments/experiment_{self.solution_id}/output/{self.id}'
        if not os.path.isdir(experiment_dir):
            os.mkdir(experiment_dir)
        file_path = f'{experiment_dir}/agent_rewards.csv'
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
        log_path = f'{experiment_dir}/behavior'
        for i, agent in enumerate(self.forwarding_agents):
            if not os.path.isdir(log_path):
                os.mkdir(log_path)
            for episode, log in agent.log.items():
                path = f'{log_path}/episode-{episode + 1}-agent-{i + 1}.csv'
                with open(path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    header = ['step', 'time', 'state', 'action', 'next state', 'reward']
                    writer.writerow(header)
                    for row in log:
                        writer.writerow(row)
