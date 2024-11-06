import pygame
import math
import colorsys
import random
import pygame_gui

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rainbow Bouncing Circles")

# Initialize UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create UI elements
# Sliders for controlling parameters
num_circles_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 20), (200, 20)),
    start_value=5,
    value_range=(1, 20),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 5), (200, 20)),
    text='Number of Circles',
    manager=manager
)

trail_length_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 70), (200, 20)),
    start_value=50,
    value_range=(10, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 55), (200, 20)),
    text='Trail Length',
    manager=manager
)

speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 120), (200, 20)),
    start_value=5,
    value_range=(1, 15),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 105), (200, 20)),
    text='Speed',
    manager=manager
)

orbit_radius_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 170), (200, 20)),
    start_value=50,
    value_range=(20, 150),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 155), (200, 20)),
    text='Orbit Radius',
    manager=manager
)

# Circle class to manage multiple circles
class Circle:
    def __init__(self, x, y, orbit_radius, speed, phase, circle_radius):
        self.x = x
        self.y = y
        self.orbit_center_x = x
        self.orbit_center_y = y
        self.orbit_radius = orbit_radius
        self.speed = speed
        self.phase = phase
        self.circle_radius = circle_radius
        self.angle = 0
        self.trail = []
        self.hue = random.random()
        self.direction_x = 1
        self.direction_y = 1
        
    def update(self, dt, orbit_radius, speed):
        # Update orbital motion
        self.angle += speed * dt
        self.orbit_radius = orbit_radius
        self.speed = speed
        
        # Calculate orbital position
        orbit_x = self.orbit_center_x + self.orbit_radius * math.cos(self.angle + self.phase)
        orbit_y = self.orbit_center_y + self.orbit_radius * math.sin(self.angle + self.phase)
        
        # Move orbit center and check boundaries
        if orbit_x - self.circle_radius <= 0 or orbit_x + self.circle_radius >= WIDTH:
            self.direction_x *= -1
        if orbit_y - self.circle_radius <= 0 or orbit_y + self.circle_radius >= HEIGHT:
            self.direction_y *= -1
            
        self.orbit_center_x += self.speed * self.direction_x
        self.orbit_center_y += self.speed * self.direction_y
        
        # Calculate final position
        self.x = orbit_x
        self.y = orbit_y
        
        # Update trail
        self.trail.append((self.x, self.y, self.hue))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)
            
        # Update hue for rainbow effect
        self.hue += 0.005
        
    def draw(self, screen):
        # Draw trail
        for i, (trail_x, trail_y, trail_hue) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_radius = int(self.circle_radius * (i / len(self.trail)))
            
            rgb = colorsys.hsv_to_rgb(trail_hue % 1.0, 1.0, 1.0)
            color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            
            circle_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*color, alpha), (trail_radius, trail_radius), trail_radius)
            screen.blit(circle_surface, (trail_x - trail_radius, trail_y - trail_radius))
        
        # Draw current circle
        rgb = colorsys.hsv_to_rgb(self.hue % 1.0, 1.0, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.circle_radius)

# Initial parameters
NUM_CIRCLES = 5
TRAIL_LENGTH = 50
BASE_SPEED = 5
BASE_ORBIT_RADIUS = 50
BASE_CIRCLE_RADIUS = 15

# Create initial circles
circles = []
def create_circles(num):
    global circles
    circles = []
    for i in range(num):
        x = random.randint(BASE_ORBIT_RADIUS, WIDTH - BASE_ORBIT_RADIUS)
        y = random.randint(BASE_ORBIT_RADIUS, HEIGHT - BASE_ORBIT_RADIUS)
        orbit_radius = BASE_ORBIT_RADIUS
        speed = BASE_SPEED
        phase = (2 * math.pi * i) / num
        circle_radius = BASE_CIRCLE_RADIUS - min(i, 5)
        circles.append(Circle(x, y, orbit_radius, speed, phase, circle_radius))

create_circles(NUM_CIRCLES)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == num_circles_slider:
                NUM_CIRCLES = int(event.value)
                create_circles(NUM_CIRCLES)
            elif event.ui_element == trail_length_slider:
                TRAIL_LENGTH = int(event.value)
            elif event.ui_element == speed_slider:
                BASE_SPEED = event.value
            elif event.ui_element == orbit_radius_slider:
                BASE_ORBIT_RADIUS = event.value
                
        manager.process_events(event)
    
    manager.update(time_delta)
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update and draw all circles
    for circle in circles:
        circle.update(time_delta, BASE_ORBIT_RADIUS, BASE_SPEED)
        circle.draw(screen)
    
    # Draw UI
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()