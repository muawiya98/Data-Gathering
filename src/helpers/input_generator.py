from dataclasses import dataclass
import sys
import pygame
import random
import os

# TODO: update to create the whole input
@dataclass
class InputGenerator:
    title: str
    num_of_uavs: int
    num_of_sensors: int
    width: int
    height: int
    grid_size: int

    def __post_init__(self):
        self.grid_size = self.grid_size
        self.grid_width = self.width * self.grid_size
        self.grid_height = self.height * self.grid_size
        self.grid_rows = self.grid_height // self.grid_size
        self.grid_cols = self.grid_width // self.grid_size

    def generate(self):
        with open(os.path.join('data', 'gen', 'sensors'), 'a') as f:
            f.write(f'{self.title}\n')

        with open(os.path.join('data', 'gen', 'uavs'), 'a') as f:
            f.write(f'{self.title}\n')
            
        with open(os.path.join('data', 'gen', 'way_points'), 'a') as f:
            f.write(f'{self.title}\n')
                
        with open(os.path.join('data', 'gen', 'sensors'), 'a') as f:
            for _ in range(self.num_of_sensors):
                x = random.uniform(1, self.width)
                y = random.uniform(1, self.height)
                f.write(f'{round(x, 1)},{round(y, 1)},0,20,3,200,20\n')
        pygame.init()

        white_color = (255, 255, 255)
        black_color = (0, 0, 0)
        green_color = (0, 255, 0)
        screen = pygame.display.set_mode((self.grid_width, self.grid_height))
        pygame.display.set_caption("Point Selection Tool")

        selected_points = []

        for uav_id in range(self.num_of_uavs):
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        grid_x = mouse_x // self.grid_size
                        grid_y = mouse_y // self.grid_size
                        selected_points.append((grid_x, grid_y))
                screen.fill(white_color)

                for row in range(self.grid_rows):
                    pygame.draw.line(screen, black_color, (0, row * self.grid_size),
                                     (self.grid_width, row * self.grid_size))
                for col in range(self.grid_cols):
                    pygame.draw.line(screen, black_color, (col * self.grid_size, 0),
                                     (col * self.grid_size, self.grid_height))

                for point in selected_points:
                    pygame.draw.rect(screen, green_color, (
                        point[0] * self.grid_size, point[1] * self.grid_size, self.grid_size, self.grid_size))

                pygame.display.flip()
                    
            with open(os.path.join('data', 'gen', 'way_points'), 'a') as f:
                for point in selected_points:
                    f.write(f'{uav_id + 1},{point[0]},{point[1]},0,0\n')
            with open(os.path.join('data', 'gen', 'uavs'), 'a') as f:
                f.write(
                    f'{selected_points[0][0]},{selected_points[0][1]},0,0,0,0,0,0,0,100,15\n')
            selected_points.clear()

        with open(os.path.join('data', 'gen', 'sensors'), 'a') as f:
            f.write('= = = = = = = = = = = =\n')

        with open(os.path.join('data', 'gen', 'uavs'), 'a') as f:
            f.write('= = = = = = = = = = = =\n')

        with open(os.path.join('data', 'gen', 'way_points'), 'a') as f:
            f.write('= = = = = = = = = = = =\n')

        pygame.quit()
        sys.exit()
