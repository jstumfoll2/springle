import random
import math
from SpingleColors import SpingleColors

class OrbitGroup:
    def __init__(self, min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed, base_size, radius):
        self.circles = []
        self.num_circles = random.randint(min_circles, max_circles)
        self.base_expansion_rate = base_expansion_rate
        self.rate_variation = rate_variation
        self.rotation_speed = rotation_speed
        self.base_size = base_size
        self.time_offset = random.random() * 10
        self.radius = radius
        self.colors = SpingleColors()  # Create instance of SpingleColors
        self.palette_index = random.randint(0, self.colors.numPatterns() - 1)
        self.color_transition = 0
        self.active = True  # New flag to track if group is still moving
        self.direction = random.choice([-1, 1])  # Random direction for the group
        self.create_circles(self.radius)

    def create_circles(self, radius):
        self.circles = []
        for i in range(self.num_circles):
            angle = (2 * math.pi * i) / self.num_circles
            self.circles.append({
                'angle': angle,
                'radius': radius,
                'color_index': 0, # i % len(COLOR_PALETTES[0]),
                'trail': [],
                'time_offset': self.time_offset,
                'last_trail_pos': None,
                'size_variation': 1 # keep all cirlces in a group the same size random.uniform(0.8, 1.2)  # Random size multiplier
            })
