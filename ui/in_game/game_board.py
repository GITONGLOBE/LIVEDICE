import pygame
import math
import random
import pymunk
from pymunk import Vec2d
from typing import List, Tuple

class GameBoard:
    def __init__(self, screen: pygame.Surface, rect: pygame.Rect):
        self.screen = screen
        self.rect = rect
        self.dice_positions: List[Tuple[int, int, float]] = []
        self.dice_size = 120
        self.stash_dice_size = 60
        self.padding = 10
        self.space = pymunk.Space()
        self.space.damping = 0.85
        self.dice_bodies = []
        self.dice_shapes = []
        self.hexagon_points = []
        self.setup_hexagon()
        self.animation_time = 0
        self.max_animation_time = 1.0
        self.dice_stop_times = []

    def setup_hexagon(self):
        center = (self.rect.centerx, self.rect.centery)
        size = 500  # This will make the hexagon 1000px from point to point vertically
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            point = (center[0] + size * math.cos(angle_rad),
                    center[1] + size * math.sin(angle_rad))
            self.hexagon_points.append(point)

        for i in range(6):
            start = self.hexagon_points[i]
            end = self.hexagon_points[(i + 1) % 6]
            line = pymunk.Segment(self.space.static_body, start, end, 5)
            line.elasticity = 0.5
            line.friction = 0.5
            self.space.add(line)
                
    def generate_dice_positions(self, num_dice: int) -> None:
        center = (self.rect.centerx, self.rect.centery)
        size = min(self.rect.width, self.rect.height) * 0.45
        effective_size = size - self.dice_size * math.sqrt(2) / 2

        for body, shape in zip(self.dice_bodies, self.dice_shapes):
            self.space.remove(body, shape)
        self.dice_bodies.clear()
        self.dice_shapes.clear()

        for _ in range(num_dice):
            x, y = self.get_random_position_in_hexagon(center, effective_size)
            mass = 1
            moment = pymunk.moment_for_box(mass, (self.dice_size, self.dice_size))
            body = pymunk.Body(mass, moment)
            body.position = x + self.dice_size/2, y + self.dice_size/2
            body.angle = random.uniform(0, 2*math.pi)

            shape = pymunk.Poly.create_box(body, (self.dice_size, self.dice_size))
            shape.elasticity = 0.8
            shape.friction = 0.5

            self.space.add(body, shape)
            self.dice_bodies.append(body)
            self.dice_shapes.append(shape)

            impulse = Vec2d(random.uniform(-600, 600), random.uniform(-600, 600))
            body.apply_impulse_at_local_point(impulse)

        self.animation_time = 0
        self.dice_stop_times = [random.uniform(0.2, 0.8) for _ in range(num_dice)]

    def get_random_position_in_hexagon(self, center, size):
        while True:
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, size)
            x = center[0] + r * math.cos(angle)
            y = center[1] + r * math.sin(angle)
            if self.is_point_in_hexagon(center, size, (x, y)):
                return int(x - self.dice_size/2), int(y - self.dice_size/2)

    def is_point_in_hexagon(self, center, size, point):
        x, y = point[0] - center[0], point[1] - center[1]
        return abs(x) <= size * 0.866 and abs(y) <= size and abs(x) * 0.577 + abs(y) <= size

    def draw_hexagon(self, color: Tuple[int, int, int], center: Tuple[int, int], size: int) -> None:
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            points.append((center[0] + size * math.cos(angle_rad),
                        center[1] + size * math.sin(angle_rad)))
        pygame.draw.polygon(self.screen, color, points)

    def draw(self) -> None:
        center = (self.rect.centerx, self.rect.centery)
        size = min(self.rect.width, self.rect.height) * 0.45
        self.draw_hexagon((204, 0, 0), center, size)  # #CC0000 red

    def update(self, dt):
        if self.animation_time < self.max_animation_time:
            self.space.step(dt)
            self.animation_time += dt

            for i, (body, stop_time) in enumerate(zip(self.dice_bodies, self.dice_stop_times)):
                if self.animation_time >= stop_time:
                    body.velocity = (0, 0)
                    body.angular_velocity = 0

        self.dice_positions = [(int(body.position.x - self.dice_size/2), 
                                int(body.position.y - self.dice_size/2), 
                                math.degrees(body.angle)) for body in self.dice_bodies]

    def update_dice_positions(self, stashed_indices: List[int]) -> None:
        for index in sorted(stashed_indices, reverse=True):
            if 0 <= index < len(self.dice_bodies):
                self.space.remove(self.dice_bodies[index], self.dice_shapes[index])
                del self.dice_bodies[index]
                del self.dice_shapes[index]
                del self.dice_stop_times[index]
        self.dice_positions = [(int(body.position.x - self.dice_size/2), 
                                int(body.position.y - self.dice_size/2), 
                                math.degrees(body.angle)) for body in self.dice_bodies]