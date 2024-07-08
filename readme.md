# Data Gathering 

## 1. Introduction

	In recent years, the integration of drones, or Unmanned Aerial Vehicles (UAVs), in various fields such as agriculture, disaster management, and environmental monitoring has revolutionized data collection processes. 
	These UAVs can cover large areas efficiently and access hard-to-reach locations, making them indispensable in scenarios requiring real-time data collection and transmission. 
	However, one of the significant challenges in deploying UAVs for such tasks is optimizing their communication and data relay strategies to ensure minimal delay and high packet delivery ratios.
	Reinforcement Learning (RL), a subset of machine learning, offers promising solutions to optimize decision-making processes in dynamic environments. 
	By employing RL algorithms, UAVs can autonomously learn and adapt their data transmission strategies to improve overall system performance. 
	This project focuses on developing a framework using Q-Learning, a popular RL algorithm, to guide UAVs in a field containing multiple sensors that collect crucial information. 
	Each UAV operates within a predetermined path of waypoints and decides the best recipient for the data at each waypoint, choosing between a Base Station, other UAVs, or no transmission.

## 2. Abstract
	The primary challenge addressed in this project is the optimization of data transmission from UAVs to the intended recipients to minimize communication delay and maximize the packet delivery ratio. In a field densely populated with sensors, UAVs must efficiently collect and relay data to ensure timely and reliable information flow. The problem is multifaceted and involves the following key aspects:
	1. Waypoint Navigation: Each UAV must navigate through a specific path of waypoints within the field. At each waypoint, the UAV needs to make an informed decision on data transmission.
	2. Recipient Selection: The UAVs must choose the optimal recipient for the data they carry. The options include sending data to a Base Station, other UAVs, or deciding not to send data at all. The choice impacts overall network performance, including latency and delivery reliability.
	3. Reinforcement Learning Application: Implementing the Q-Learning algorithm to enable UAVs to learn the best choes to choose the optimal recipient.
	4. Simulation Environment: Creating a robust simulation environment using Python and libraries like pygame to model the UAVs, their paths, and the decision-making processes.
	By addressing these aspects, the project aims to enhance the efficiency and effectiveness of UAV-based data collection systems, ultimately contributing to improved performance in real-world applications.

## 3. Applied Techniques

	- Technique 1 DQN: [Reinforcmentr Learning Algorithm (Deep Q-Learning)]
	- Technique 2 Several Algorithm: [To Simulate the combonent (Field, UAVs, Way points, Sensores....etc) and make them work togather and with the RL agents for having done the system]


## 4. Commandline utility:

	usage: main.py [-h] --run_type {train,test,plot,plot-epsilon,generate} [--solution SOLUTION] [--id ID] [--algorithm {random,greedy,intelligent,no_forwarding}]
				   [--repeat REPEAT] [--chunk_size CHUNK_SIZE] [--visualizer {pygame,none}] [--load_from LOAD_FROM] [--episodes EPISODES] [--steps STEPS]
				   [--with_log WITH_LOG] [--log_behavior_freq LOG_BEHAVIOR_FREQ] [--title TITLE] [--grid_size GRID_SIZE] [--num_of_uavs NUM_OF_UAVS]
				   [--num_of_sensors NUM_OF_SENSORS] [--width WIDTH] [--height HEIGHT]

	options:
	  -h, --help            show this help message and exit
	  --run_type {train,test,plot,plot-epsilon,generate}
	  --solution SOLUTION   the solution index in the data/experiments dir
	  --id ID               the solution name
	  --algorithm {random,greedy,ql,no_forwarding}
	  --repeat REPEAT       times of repeating the experiment
	  --chunk_size CHUNK_SIZE
							the interval of the episode plotting
	  --visualizer {pygame,none}
	  --load_from LOAD_FROM
							the solution id to load from
	  --episodes EPISODES   for RL agent
	  --steps STEPS         for RL agent
	  --with_log WITH_LOG   log events to app.log file
	  --log_behavior_freq LOG_BEHAVIOR_FREQ
							frequency of logging the RL agent action
	  --title TITLE
	  --grid_size GRID_SIZE
							the grid square size in pygame screen
	  --num_of_uavs NUM_OF_UAVS
	  --num_of_sensors NUM_OF_SENSORS
	  --width WIDTH         environment width
	  --height HEIGHT       environment height


## 5. examples:

	- to run the input generator:
		python main.py  --run_type generate --title train102 --num_of_uavs 3 --num_of_sensors 250
						--height 1000 --width 1000 --grid_size 2
	- to run the plotter:
		python main.py --run_type plot --solution 0 --id 3 --chunk_size 1
		python main.py --run_type plot-epsilon --episodes 100

	- to run the algorithm testing:
		python main.py --run_type test --solution 5 --algorithm random --repeat 1 --visualizer none

	- to run the RL training:
		python main.py --run_type train --solution 0 --episodes 3 --steps 200

	- to run the input generator:
	  python main.py --run_type generate --title train102 --num_of_uavs 3 --num_of_sensors 250
	  --height 1000 --width 1000 --grid_size 2

	- to run the plotter:
	  python main.py --run_type plot --solution 0 --id 3 --chunk_size 1
	  python main.py --run_type plot-epsilon --episodes 100

	- to run the algorithm testing:
	  python main.py --run_type test --solution 1 --algorithm ql --repeat 1 --visualizer none
	- to run the RL training:
	  python main.py --run_type train --solution 0 --episodes 3 --steps 200 --log_behavior_freq 5 
	  --load_from 31241

## 6. Src dir file structure:

	.
	├── algorithms
	│ ├── collecting_algorithms
	│ │ └── __init__.py
	│ ├── forwarding_algorithms
	│ │ ├── forwarding_algorithm.py
	│ │ ├── greedy_frowarding.py
	│ │ ├── __init__.py
	│ │ ├── intelligent_forwarding
	│ │ │ ├── agents_controller.py
	│ │ │ ├── data_forwarding_agent.py
	│ │ │ ├── __init__.py
	│ │ │ ├── intelligent_forwarding.py
	│ │ │ └── state.py
	│ │ ├── no_forwarding.py
	│ │ └── random_forwarding.py
	│ └── __init__.py
	├── environment
	│ ├── core
	│ │ ├── environment_controller.py
	│ │ ├── environment_presenter.py
	│ │ ├── environment.py
	│ │ └── __init__.py
	│ ├── devices
	│ │ ├── base_station.py
	│ │ ├── data_packet.py
	│ │ ├── device.py
	│ │ ├── __init__.py
	│ │ ├── sensor.py
	│ │ └── uav.py
	│ ├── __init__.py
	│ ├── models
	│ │ ├── energy_model.py
	│ │ └── __init__.py
	│ └── utils
	│ ├── helper_functions.py
	│ ├── __init__.py
	│ ├── priority_queue.py
	│ └── vector.py
	├── helpers
	│ ├── file_manager.py
	│ ├── __init__.py
	│ ├── input_generator.py
	│ ├── logger.py
	│ ├── plotter.py
	│ └── plotter.py
	└── __init__.py

## 7. Simulation basic features:

	- The basic behaviors captured by the simulation:
		- The movement of the UAVs based on their speed.
		- The data storage inside a device:
		  the data storage is simply implemented in the simplest possible way, the data is represented as List of data
		  packets
		  [[DataPacket](src/environment/devices/data_packet.py)] stored in the [[Device](src/environment/devices/device.py)]
		  class
		- The data collection in the Sensors [[Sensor](src/environment/devices/sensor.py)] is done simply by appending a
		  number of data packets to the sensor memory each time the sensor takes a sample from the environment.
		- The data transfer between two devices is done simply by:
			- pop the data packets from the first device.
			- append the data packets to the second device.
		- it is worth noticing that the data transfer in the simulation takes <ins> **no time** <ins>
		- The energy consumption in the environment is implemented using the energy model explained in the
		  docs [[EnergyModel](src/environment/models/energy_model.py)].

## 8. Simulation

	- The simulation starts executing from the [[EnvironmentController](src/environment/core/environment_controller.py)]
	  class.
	- The simulation runs as the following:
		- The controller handles:
			- choosing the proper environment, presenter and used agent algorithm to run the simulation.
			- loads the environment variables and them using the [[FileManager](src/helpers/file_manager.py)]
			- the end of the simulation condition.
				- the simulation ends either when:
					- the current time step is equal to the predefined time step in the input
					  file: [[environment_basics.csv](data/experiments/experiment_0/input/environment_basics.csv)]
					- all the UAVs have finished all their missions (collecting the data from the way points or forwarding
					  the data to a data target)
		- the environment [step()] function is executed as the following:
			- if the environment has 
			- execute the UAV [step()] function for each UAV:
				- if the UAV has collection rate it collects the data from the environment.
				- if the UAV has forwarding target the UAV forwards data to that target.
				- if the UAV does not have any of the previous missions it moves to the next point along the predefined
				  path.
			- execute the Sensor [step()] function for each sensor:
				- if the current time step go along with the sensor sampling rate the sensors collects data.
## 9. Results

	[You can find the final results and a snapshot about the environment by looking at the report above.]