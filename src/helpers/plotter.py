import csv
import os
from typing import Any

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
from dataclasses import dataclass
import random

random.seed(42)
np.random.seed(42)

@dataclass
class Plotter:
    id: int
    solution: int
    chunk_size: int

    def _get_file_path(self):
        current_dir = os.getcwd()
        print(self.id)
        solution_dir = os.path.join(current_dir, 'data', 'experiments', f'experiment_{self.solution}', 'output' , f'{self.id}')
        if not os.path.isdir(solution_dir):
            os.mkdir(solution_dir)
        file_path = os.path.join(solution_dir, 'agent_rewards.csv')
        return file_path

    @staticmethod
    def _read_df(file_path) -> Any:
        return pd.read_csv(file_path)

    @staticmethod
    def _get_rewards_array(data_frame):
        rewards = []
        for _ in range(data_frame.shape[1]):
            rewards.append(list())
        for index, row in data_frame.iterrows():
            for i in range(data_frame.shape[1]):
                rewards[i].append(row[f'agent-{i + 1}'])
        return rewards

    @staticmethod
    def _plot_rewards(rewards_list, file_path, chunk_size):
        plt.title('Agents rewards')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        # handlers = []
        t_rewards_list = rewards_list
        for ii in range(len(rewards_list)+1):
            if ii >= len(rewards_list):t_rewards_list = rewards_list
            else:t_rewards_list = [rewards_list[ii]]
            for idx, rewards in enumerate(t_rewards_list):
                # data_mean = np.mean(rewards)
                # data_std = np.std(rewards)
                # rewards = list((rewards - data_mean) / data_std)
                y_points = np.array([])
                for chunk in range(len(rewards) // chunk_size):
                    avg = np.sum(rewards[chunk * chunk_size: chunk * chunk_size + chunk_size]) / chunk_size
                    y_points = np.append(y_points, avg)
                x_points = np.arange(0, len(rewards) // chunk_size)
                for i in range(len(x_points)):
                    x_points[i] += 1
                label=f'Agent {idx + 1}'
                if ii < len(rewards_list):label=f'Agent {idx + ii + 1}'
                line, = plt.plot(x_points, y_points, label=label)
                # handlers.append(line)
            file_path = f'{file_path[:-4]}-{chunk_size}-{str(ii)}.png'
            # plt.legend(handles=handlers, loc='upper left')
            plt.legend(loc='best')
            plt.savefig(file_path)
            plt.cla()

    def plot(self):
        file_path = self._get_file_path()
        df = self._read_df(file_path)
        rewards = self._get_rewards_array(df)
        plot_path = f'{file_path[:-4]}.png'
        self._plot_rewards(rewards, plot_path, self.chunk_size)

    @staticmethod
    def plot_epsilon_decay(episodes):
        epsilon = 1
        epsilon_decay = 0.985
        epsilon_min = 0
        xs, ys, ds = range(1, episodes), [], []
        for _ in xs:
            ys.append(epsilon)
            if np.random.rand() < epsilon:
                ds.append('explore')
            else:
                ds.append('exploit')
            epsilon = max(epsilon_min, epsilon * epsilon_decay)
            
        with open(os.path.join('data', 'plots', 'greedy_update.csv'), mode='w', newline='') as file:
            writer = csv.writer(file)
            header = ['episode', 'epsilon', 'decisions']
            writer.writerow(header)
            for x, y, d in zip(xs, ys, ds):
                writer.writerow([x, y, d])
        plt.title('Epsilon updates')
        plt.xlabel('Episode')
        plt.ylabel('Epsilon')
        # plt.legend(loc='best')
        plt.plot(xs, ys)
        plt.savefig(os.path.join('data', 'plots', 'greedy_update.png'))
