import pygame
import math
import colorsys
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rainbow Circular Motion")

# Circle class to manage multiple circles
class Circle:
    def __init__(self, center_x, center_y, orbit_radius, speed, phase, circle_radius):
        self.center_x = center_x
        self.center_y = center_y
        self.orbit_radius = orbit_radius
        self.speed = speed
        self.phase = phase
        self.circle_radius = circle_radius
        self.angle = 0
        self.trail = []
        self.hue = random.random()
        
    def update(self):
        # Update position using parametric equations of a circle
        self.angle += self.speed
        x = self.center_x + self.orbit_radius * math.cos(self.angle + self.phase)
        y = self.center_y + self.orbit_radius * math.sin(self.angle + self.phase)
        
        # Update trail
        self.trail.append((x, y, self.hue))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)
            
        # Update hue for rainbow effect
        self.hue += 0.005
        
        return x, y
        
    def draw(self, screen):
        # Draw trail
        for i, (trail_x, trail_y, trail_hue) in enumerate(self.trail):
            # Calculate alpha and size for trail effect
            alpha = int(255 * (i / TRAIL_LENGTH))
            trail_radius = int(self.circle_radius * (i / TRAIL_LENGTH))
            
            # Convert HSV to RGB
            rgb = colorsys.hsv_to_rgb(trail_hue % 1.0, 1.0, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            # Create surface for semi-transparent circle
            circle_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*color, alpha), (trail_radius, trail_radius), trail_radius)
            screen.blit(circle_surface, (trail_x - trail_radius, trail_y - trail_radius))
        
        # Draw current circle
        x, y = self.update()
        rgb = colorsys.hsv_to_rgb(self.hue % 1.0, 1.0, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        pygame.draw.circle(screen, color, (int(x), int(y)), self.circle_radius)

# Configurable parameters
NUM_CIRCLES = 5  # Number of circles
TRAIL_LENGTH = 50  # Length of the trail
BASE_SPEED = 0.03  # Base speed of rotation
BASE_ORBIT_RADIUS = 100  # Base radius of the circular motion
BASE_CIRCLE_RADIUS = 15  # Base radius of each circle

# Create circles with varying parameters
circles = []
for i in range(NUM_CIRCLES):
    # Create circles with different orbits and phases
    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    orbit_radius = BASE_ORBIT_RADIUS * (1 + i * 0.5)  # Each circle has a larger orbit
    speed = BASE_SPEED * (1 - i * 0.1)  # Each circle moves slightly slower
    phase = (2 * math.pi * i) / NUM_CIRCLES  # Evenly space the circles
    circle_radius = BASE_CIRCLE_RADIUS - i  # Each circle is slightly smaller
    
    circles.append(Circle(center_x, center_y, orbit_radius, speed, phase, circle_radius))

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Press UP/DOWN to change number of circles
            if event.key == pygame.K_UP and NUM_CIRCLES < 10:
                NUM_CIRCLES += 1
                circles.append(Circle(
                    WIDTH // 2, 
                    HEIGHT // 2,
                    BASE_ORBIT_RADIUS * (1 + len(circles) * 0.5),
                    BASE_SPEED * (1 - len(circles) * 0.1),
                    (2 * math.pi * len(circles)) / NUM_CIRCLES,
                    BASE_CIRCLE_RADIUS - len(circles)
                ))
            elif event.key == pygame.K_DOWN and NUM_CIRCLES > 1:
                NUM_CIRCLES -= 1
                circles.pop()
            # Press LEFT/RIGHT to change orbit radius
            elif event.key == pygame.K_LEFT:
                for circle in circles:
                    circle.orbit_radius = max(50, circle.orbit_radius - 20)
            elif event.key == pygame.K_RIGHT:
                for circle in circles:
                    circle.orbit_radius = min(300, circle.orbit_radius + 20)
            # Press SPACE to randomize speeds
            elif event.key == pygame.K_SPACE:
                for circle in circles:
                    circle.speed = BASE_SPEED * random.uniform(0.5, 1.5)
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update and draw all circles
    for circle in circles:
        circle.draw(screen)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()