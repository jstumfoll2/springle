import pygame
import math
import colorsys
import pygame_gui

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Expanding Orbital Patterns")

# Initialize UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create UI elements
group_size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 20), (200, 20)),
    start_value=3,
    value_range=(3, 12),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 5), (200, 20)),
    text='Circles per Group',
    manager=manager
)

expansion_rate_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 70), (200, 20)),
    start_value=30,
    value_range=(10, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 55), (200, 20)),
    text='Base Expansion Rate',
    manager=manager
)

rate_variation_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 120), (200, 20)),
    start_value=0.5,
    value_range=(0.1, 2.0),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 105), (200, 20)),
    text='Expansion Rate Variation',
    manager=manager
)

rotation_speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 170), (200, 20)),
    start_value=2,
    value_range=(0.5, 5),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 155), (200, 20)),
    text='Rotation Speed',
    manager=manager
)

# Add persistent trails toggle button
persistent_trails_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 220), (200, 30)),
    text='Toggle Persistent Trails',
    manager=manager
)

# Add clear trails button
clear_trails_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 260), (200, 30)),
    text='Clear Trails',
    manager=manager
)

class OrbitGroup:
    def __init__(self, num_circles, base_expansion_rate, rate_variation, rotation_speed):
        self.circles = []
        self.num_circles = num_circles
        self.base_expansion_rate = base_expansion_rate
        self.rate_variation = rate_variation
        self.rotation_speed = rotation_speed
        self.time_offset = 0
        self.create_circles()

    def create_circles(self):
        self.circles = []
        for i in range(self.num_circles):
            angle = (2 * math.pi * i) / self.num_circles
            self.circles.append({
                'angle': angle,
                'radius': 0,
                'hue': random.random(),
                'trail': [],
                'time_offset': self.time_offset
            })

class Circle:
    def __init__(self, group_size, base_expansion_rate, rate_variation, rotation_speed):
        self.groups = [OrbitGroup(group_size, base_expansion_rate, rate_variation, rotation_speed)]
        self.circle_radius = 4
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2

    def update(self, dt, group_size, base_expansion_rate, rate_variation, rotation_speed):
        screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        
        # Update existing groups
        for group in self.groups:
            group.num_circles = group_size
            group.base_expansion_rate = base_expansion_rate
            group.rate_variation = rate_variation
            group.rotation_speed = rotation_speed
            
            # Ensure correct number of circles in group
            while len(group.circles) < group_size:
                angle = (2 * math.pi * len(group.circles)) / group_size
                group.circles.append({
                    'angle': angle,
                    'radius': 0,
                    'hue': random.random(),
                    'trail': [],
                    'time_offset': group.time_offset
                })
            while len(group.circles) > group_size:
                group.circles.pop()

            # Update each circle in the group
            for circle in group.circles:
                # Calculate expansion rate with sinusoidal variation
                variation = math.sin((circle['time_offset'] + group.time_offset) * 0.5) * rate_variation
                current_expansion_rate = base_expansion_rate * (1 + variation)
                
                # Update radius
                circle['radius'] += current_expansion_rate * dt
                
                # Update rotation angle
                circle['angle'] += rotation_speed * dt
                
                # Calculate position
                x = self.center_x + math.cos(circle['angle']) * circle['radius']
                y = self.center_y + math.sin(circle['angle']) * circle['radius']
                
                # Update trail
                circle['trail'].append((x, y, circle['hue']))
                if not PERSISTENT_TRAILS and len(circle['trail']) > 50:
                    circle['trail'].pop(0)
                
                # Update hue
                circle['hue'] += 0.002
                
                # Update time offset
                circle['time_offset'] += dt

        # Check if we need a new group
        for group in self.groups[:]:
            all_circles_outside = all(
                circle['radius'] > screen_diagonal / 2 
                for circle in group.circles
            )
            if all_circles_outside:
                self.groups.remove(group)
                
        # Add new group if needed
        if len(self.groups) < 3:  # Maintain multiple groups
            new_group = OrbitGroup(group_size, base_expansion_rate, rate_variation, rotation_speed)
            new_group.time_offset = random.random() * 10  # Random time offset for variation
            self.groups.append(new_group)

    def draw(self, screen):
        for group in self.groups:
            for circle in group.circles:
                # Draw trail
                for i, (x, y, hue) in enumerate(circle['trail']):
                    if not (0 <= x <= WIDTH and 0 <= y <= HEIGHT):
                        continue
                        
                    if PERSISTENT_TRAILS:
                        alpha = 64
                        trail_radius = max(2, self.circle_radius * 0.8)
                    else:
                        alpha = int(255 * (i / len(circle['trail'])))
                        trail_radius = int(self.circle_radius * (i / len(circle['trail'])))
                    
                    rgb = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
                    color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                    
                    circle_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(circle_surface, (*color, alpha), 
                                    (trail_radius, trail_radius), trail_radius)
                    screen.blit(circle_surface, (x - trail_radius, y - trail_radius))
                
                # Draw current circle
                x = self.center_x + math.cos(circle['angle']) * circle['radius']
                y = self.center_y + math.sin(circle['angle']) * circle['radius']
                if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                    rgb = colorsys.hsv_to_rgb(circle['hue'] % 1.0, 1.0, 1.0)
                    color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
                    pygame.draw.circle(screen, color, (int(x), int(y)), self.circle_radius)

# Initial parameters
import random
GROUP_SIZE = 3
BASE_EXPANSION_RATE = 30
RATE_VARIATION = 0.5
ROTATION_SPEED = 2
PERSISTENT_TRAILS = False

# Create circle system
circle_system = Circle(GROUP_SIZE, BASE_EXPANSION_RATE, RATE_VARIATION, ROTATION_SPEED)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == group_size_slider:
                GROUP_SIZE = int(event.value)
            elif event.ui_element == expansion_rate_slider:
                BASE_EXPANSION_RATE = event.value
            elif event.ui_element == rate_variation_slider:
                RATE_VARIATION = event.value
            elif event.ui_element == rotation_speed_slider:
                ROTATION_SPEED = event.value
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == persistent_trails_button:
                PERSISTENT_TRAILS = not PERSISTENT_TRAILS
                persistent_trails_button.set_text(
                    'Persistent Trails: ON' if PERSISTENT_TRAILS else 'Persistent Trails: OFF'
                )
            elif event.ui_element == clear_trails_button:
                for group in circle_system.groups:
                    for circle in group.circles:
                        circle['trail'] = []
                
        manager.process_events(event)
    
    manager.update(time_delta)
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update and draw circle system
    circle_system.update(time_delta, GROUP_SIZE, BASE_EXPANSION_RATE, RATE_VARIATION, ROTATION_SPEED)
    circle_system.draw(screen)
    
    # Draw UI
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()