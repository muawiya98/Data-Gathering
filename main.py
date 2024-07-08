import argparse
import os
import pickle
from datetime import datetime
from src.algorithms.forwarding_algorithms.forwarding_algorithm import ForwardingAlgorithm
from src.algorithms.forwarding_algorithms.greedy_frowarding import GreedyForwarding
# from src.algorithms.forwarding_algorithms.dqn_forwarding.dqn_agents_controller import DQNAgentsController
# from src.algorithms.forwarding_algorithms.dqn_forwarding.dqn_forwarding_agent import DQNForwardingAgent
# from src.algorithms.forwarding_algorithms.dqn_forwarding.dqn_forwarding import DQNForwarding
from src.algorithms.forwarding_algorithms.no_forwarding import NoForwarding
from src.algorithms.forwarding_algorithms.q_learning_forwarding.q_learning_agents_controller import \
    QLearningAgentsController
from src.algorithms.forwarding_algorithms.q_learning_forwarding.q_learning_forwarding import QLearningForwarding
from src.algorithms.forwarding_algorithms.q_learning_forwarding.q_learning_forwarding_agent import \
    QLearningForwardingAgent
from src.algorithms.forwarding_algorithms.random_forwarding import RandomForwarding
from src.environment.core.environment import Environment
from src.environment.core.environment_controller import EnvironmentController
from src.helpers.file_manager import FileManager
from src.helpers.input_generator import InputGenerator
from src.helpers.logger import configure_logger
from src.helpers.plotter import Plotter

def main():
    def get_algorithm(name: str) -> ForwardingAlgorithm:
        if name == 'none':
            return NoForwarding(env)
        elif name == 'random':
            return RandomForwarding(env)
        elif name == 'greedy':
            return GreedyForwarding(env)
        elif name == 'dqn':
            raise NotImplementedError()
            # agents = get_dqn_forwarding_agents(save_weights=False)
            # return DQNForwarding(env, call_frequency=40, agents=agents)
        elif name == 'ql':
            agents = get_ql_forwarding_agents(load_from_file=True)
            return QLearningForwarding(env, agents=agents)
        else:
            raise NotImplementedError()

    def get_args():
        parser = argparse.ArgumentParser()
        # Basic args
        parser.add_argument('--run_type', type=str, required=True,
                            choices=['train-dqn', 'train-ql', 'test', 'plot', 'plot-epsilon', 'generate'], )
        parser.add_argument('--solution', help='the solution index in the data/experiments dir', type=int)
        parser.add_argument('--id', help='the solution name', type=str)

        # Testing args
        parser.add_argument('--algorithm', type=str,
                            choices=['random', 'greedy', 'ql', 'dqn', 'none'])
        parser.add_argument('--repeat', help='times of repeating the experiment', type=int, default=1)
        parser.add_argument('--chunk_size', help='the interval of the episode plotting', type=int, default=1)
        parser.add_argument('--visualizer', type=str, choices=['pygame', 'none'])
        parser.add_argument('--load_from', help='the solution id to load from', type=str, default=None)

        # Training args
        parser.add_argument('--episodes', help='for RL agent', type=int)
        parser.add_argument('--steps', help='for RL agent', type=int)
        parser.add_argument('--with_log', help='log events to app.log file', type=bool, default=True)
        parser.add_argument('--log_behavior_freq', help='frequency of logging the RL agent action', type=int,
                            default=1e8)

        # Generator args
        parser.add_argument('--title', type=str, default='test_sample')
        parser.add_argument('--grid_size', help='the grid square size in pygame screen', type=int, default=10)
        parser.add_argument('--num_of_uavs', type=int)
        parser.add_argument('--num_of_sensors', type=int)
        parser.add_argument('--width', help='environment width', type=int)
        parser.add_argument('--height', help='environment height', type=int)

        return parser.parse_args()

    # def get_dqn_forwarding_agents(save_weights=True):
    #     agents = []
    #     for i, uav in enumerate(env.uavs):
    #         # TODO: calculate state dim
    #         agent = DQNForwardingAgent(uav=uav, env=env, solution_id=args.solution,
    #                                    state_dim=2 * len(env.uavs) + len(env.base_stations) + 1,
    #                                    action_size=len(env.uavs) + len(env.base_stations) + 1,
    #                                    load_from=args.load_from, save_weights=save_weights)
    #         agents.append(agent)
    #     return agents

    def get_ql_forwarding_agents(load_from_file=False):
        agents = []
        if load_from_file:
            current_dir = os.getcwd()
            model_dir = os.path.join(current_dir, 'data', 'experiments', f'experiment_{args.solution}', 'output', f'{args.id}', 'model')
            for uav in env.uavs:
                path = os.path.join(model_dir, f'agent-{uav.id}.pkl')
                assert os.path.exists(path), f'No model saved for this experiments for agent {uav.id}'
                with open(path, 'rb') as file:
                    agent = pickle.load(file)
                    agent.uav = uav
                    agent.env = env
                    agents.append(agent)
            return agents
        q_table_size_list = []
        action_size = len(env.uavs) + len(env.base_stations)
        for _ in env.uavs:
            q_table_size = []
            for other in env.uavs:
                q_table_size.append(len(other.path))
            # add the (has data) parameter
            q_table_size.append(2)
            q_table_size.append(action_size)
            q_table_size_list.append(tuple(q_table_size))
        for i, uav in enumerate(env.uavs):
            agent = QLearningForwardingAgent(uav=uav, env=env, solution_id=args.solution,
                                             q_table_size=q_table_size_list[i], action_size=action_size)
            agents.append(agent)
        return agents

    def init_environment():
        assert args.solution is not None, '/.You should add --solution {solution_name} variable'
        file = FileManager(args.solution)
        configure_logger(write_on_file=args.with_log)
        Environment.time_stamp = datetime.now().microsecond
        return file.load_environment()

    args = get_args()
    if args.run_type == 'train-dqn':
        raise NotImplementedError()
        # env = init_environment()
        # forwarding_agents = get_dqn_forwarding_agents()
        # controller = DQNAgentsController(id=Environment.time_stamp, forwarding_agents=forwarding_agents,
        #                                  num_of_episodes=args.episodes, max_steps=args.steps, env=env,
        #                                  solution_id=args.solution, log_behavior_freq=args.log_behavior_freq)
        # controller.train_agents()
    elif args.run_type == 'train-ql':
        env = init_environment()
        forwarding_agents = get_ql_forwarding_agents()
        controller = QLearningAgentsController(id=Environment.time_stamp, forwarding_agents=forwarding_agents,
                                               num_of_episodes=args.episodes, max_steps=args.steps, env=env,
                                               solution_id=args.solution, log_behavior_freq=args.log_behavior_freq)
        agent_sequence = list(reversed([*range(len(forwarding_agents))]))
        controller.train_agents(agent_sequence)
    elif args.run_type == 'test':
        env = init_environment()
        for _ in range(args.repeat):
            forwarding_algorithm = get_algorithm(args.algorithm)
            controller = EnvironmentController(env, forwarding_algorithm)
            controller.run(visualizer=args.visualizer, solution_id=args.solution)
            env.reset()
    elif args.run_type == 'plot':
        plotter = Plotter(solution=args.solution, id=args.id, chunk_size=args.chunk_size)
        plotter.plot()
    elif args.run_type == 'plot-epsilon':
        Plotter.plot_epsilon_decay(args.episodes)
    elif args.run_type == 'generate':
        input_generator = InputGenerator(height=args.height, width=args.width, grid_size=args.grid_size,
                                         num_of_uavs=args.num_of_uavs, num_of_sensors=args.num_of_sensors,
                                         title=args.title)
        input_generator.generate()


if __name__ == '__main__':
    main()
# python main.py --run_type train-ql --solution 1 --episodes 300 --steps 50
# python main.py --run_type plot --solution 1 --id 12389883

# 5436365 agent number 2 # (0, 1, 2 ,3)
# 8511317 agent number 3 # (0, 1, 2 ,3)
# 9646939 agent number 3 and over all the agent are goode # (0, 1, 2 ,3)
# python main.py --run_type train-ql --solution 1 --episodes 300 --steps 100