import sys
from dataclasses import dataclass

import pygame

from src.environment.core.environment import Environment
import numpy as np
import random

random.seed(42)
np.random.seed(42)

# TODO: fancy add cool features
@dataclass
class EnvironmentPresenter:
    def capture_events(self):
        pass

    def render(self, env):
        pass


class Color:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    TEAL = (0, 128, 128)
    BROWN = (139, 69, 19)
    GREY = (128, 128, 128)
    BLACK = (0, 0, 0)
    LIGHT_GREY = (64, 64, 64)


class PygamePresenter(EnvironmentPresenter):
    def __init__(self):
        self.screen, self.color, self.clock, self.height, self.width = self.init_pygame()
        self.uav_width, self.uav_height = 10, 10
        self.point_width, self.point_height = 7, 7
        self.sensor_width, self.sensor_height = 3, 3
        self.base_station_width, self.base_station_height = 15, 15
        self.uav_colors = [Color.BLUE, Color.TEAL, Color.ORANGE, Color.MAGENTA]
        font_path = pygame.font.get_default_font()
        self.font = pygame.font.Font(font_path, 36)
        self.ticking_speed = 5 # 20
        # TODO: add to args
        self.save_first_image = False

    @staticmethod
    def init_pygame():
        pygame.init()

        width, height = 1000, 1200 #1000, 1000
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("fanet-data-gathering")
        white = (255, 255, 255)
        clock = pygame.time.Clock()
        return screen, white, clock, height, width

    def draw_grid(self):
        grid_size = 20
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.screen, Color.GREY, (x, 0), (x, self.height))
        for y in range(0, self.height, grid_size):
            pygame.draw.line(self.screen, Color.GREY, (0, y), (self.width, y))

    def capture_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def draw_sensor(self, sensor):
        pygame.draw.circle(self.screen, Color.RED, (sensor.position.x, sensor.position.y), 5)

    def draw_uav(self, uav, color):
        pygame.draw.polygon(self.screen, color,
                            [(uav.position.x, uav.position.y - 10), (uav.position.x - 10, uav.position.y + 10),
                             (uav.position.x + 10, uav.position.y + 10)])
        pygame.draw.circle(self.screen, color, (uav.position.x, uav.position.y), uav.coverage_radius, 1)

    def draw_path(self, uav, color):
        for point in uav.path:
            x, y = point.x, point.y
            pygame.draw.line(self.screen, color, (x - 8, y - 8), (x + 8, y + 8), 5)
            pygame.draw.line(self.screen, color, (x + 8, y - 8), (x - 8, y + 8), 5)
        for i, _ in enumerate(uav.path[:-1]):
            pygame.draw.line(self.screen, color, (uav.path[i].x, uav.path[i].y),
                             (uav.path[i + 1].x, uav.path[i + 1].y))

    def draw_base_station(self, base_station):
        pygame.draw.rect(self.screen, Color.PURPLE,
                         (base_station.position.x - 15, base_station.position.y - 15, 30, 30))

    def draw_white_square(self, x, y, width, height):
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height))

    def draw_legend(self, text, position, color):
        font = pygame.font.Font(None, 24)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def draw_legends(self):
        # TODO: add shapes
        self.draw_white_square(805, 785, 190, 120)
        self.draw_legend('^: UAV', (820, 800), Color.BLUE)
        self.draw_legend('[]: Base Station', (820, 825), Color.PURPLE)
        self.draw_legend('o: Sensor', (820, 850), Color.RED)
        self.draw_legend('x: Rendezvous Point', (820, 875), Color.BLUE)

    def render(self, env):
        if self.save_first_image and Environment.time_step == 2:
            # TODO: add the experiment folder
            pygame.image.save(self.screen, 'pygame_image.png')
        self.screen.fill(self.color)
        self.draw_grid()
        for sensor in env.sensors:
            self.draw_sensor(sensor)
        for i, uav in enumerate(env.uavs):
            uav_color = self.uav_colors[i % len(self.uav_colors)]
            self.draw_path(uav, uav_color)
            self.draw_uav(uav, uav_color)
        for base_station in env.base_stations:
            self.draw_base_station(base_station)
        self.draw_legends()
        pygame.display.flip()
        self.clock.tick(self.ticking_speed)
