import logging
from dataclasses import dataclass

from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.environment.core.environment import Environment
from src.environment.core.environment_presenter import PygamePresenter, EnvironmentPresenter

import os

@dataclass
class EnvironmentController:
    env: Environment
    forwarding_algorithm: ForwardingAlgorithm

    def control(self):
        for uav in self.env.uavs:
            uav.forward_target = self.forwarding_algorithm(uav)

    def log_results(self, solution_id):
        # TODO: add energy consumption
        pdr, delay = self.env.get_performance_matrices()
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data', 'experiments', f'experiment_{solution_id}', 'performance', f'{self.forwarding_algorithm}.log.csv')
        with open(file_path, 'a') as file:
            file.write(f'{round(pdr, 3)},{round(delay, 3)}\n')

    @staticmethod
    def get_visualizer(visualizer):
        if visualizer == 'pygame':
            return PygamePresenter()
        logging.info('no visualizer is used')
        return EnvironmentPresenter()

    def run(self, visualizer: str, solution_id: str) -> None:
        presenter = self.get_visualizer(visualizer)
        while not self.env.has_ended():
            presenter.capture_events()
            presenter.render(self.env)
            self.env.step()
            self.control()
        self.log_results(solution_id)
