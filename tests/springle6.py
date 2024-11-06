import pygame
import math
import colorsys
import pygame_gui
import random

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
min_circles_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 20), (200, 20)),
    start_value=3,
    value_range=(3, 8),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 5), (200, 20)),
    text='Min Circles per Group',
    manager=manager
)

max_circles_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 70), (200, 20)),
    start_value=8,
    value_range=(3, 12),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 55), (200, 20)),
    text='Max Circles per Group',
    manager=manager
)

expansion_rate_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 120), (200, 20)),
    start_value=30,
    value_range=(10, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 105), (200, 20)),
    text='Base Expansion Rate',
    manager=manager
)

rate_variation_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 170), (200, 20)),
    start_value=0.5,
    value_range=(0.1, 2.0),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 155), (200, 20)),
    text='Expansion Rate Variation',
    manager=manager
)

rotation_speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 220), (200, 20)),
    start_value=2,
    value_range=(0.5, 5),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 205), (200, 20)),
    text='Rotation Speed',
    manager=manager
)

circle_size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 270), (200, 20)),
    start_value=4,
    value_range=(2, 10),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 255), (200, 20)),
    text='Circle Size',
    manager=manager
)

# Clear trails button
clear_trails_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 320), (200, 30)),
    text='Clear Trails',
    manager=manager
)

# Color palettes (each with 5 colors)
COLOR_PALETTES = [
    # Sunset palette
    [(255, 171, 0), (255, 105, 0), (255, 45, 0), (225, 0, 108), (165, 0, 168)],
    # Ocean palette
    [(64, 224, 208), (0, 116, 217), (127, 219, 255), (57, 204, 204), (1, 191, 236)],
    # Forest palette
    [(34, 139, 34), (0, 100, 0), (107, 142, 35), (85, 107, 47), (154, 205, 50)],
    # Neon palette
    [(255, 0, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 128)],
    # Galaxy palette
    [(123, 31, 162), (32, 0, 255), (103, 58, 183), (244, 143, 177), (156, 39, 176)]
]

def lerp_color(color1, color2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

class OrbitGroup:
    def __init__(self, min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed):
        self.circles = []
        self.num_circles = random.randint(min_circles, max_circles)
        self.base_expansion_rate = base_expansion_rate
        self.rate_variation = rate_variation
        self.rotation_speed = rotation_speed
        self.time_offset = random.random() * 10
        self.palette_index = random.randint(0, len(COLOR_PALETTES) - 1)
        self.color_transition = 0
        self.create_circles()

    def create_circles(self):
        self.circles = []
        for i in range(self.num_circles):
            angle = (2 * math.pi * i) / self.num_circles
            self.circles.append({
                'angle': angle,
                'radius': 0,
                'color_index': i % len(COLOR_PALETTES[0]),
                'trail': [],
                'time_offset': self.time_offset
            })

class Circle:
    def __init__(self, min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed):
        self.groups = [OrbitGroup(min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed)]
        self.circle_radius = 4
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.color_transition_speed = 0.2

    def update(self, dt, min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed, circle_radius):
        screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        self.circle_radius = circle_radius
        
        # Update existing groups
        for group in self.groups:
            group.base_expansion_rate = base_expansion_rate
            group.rate_variation = rate_variation
            group.rotation_speed = rotation_speed
            
            # Update color transition
            group.color_transition += dt * self.color_transition_speed
            if group.color_transition >= 1:
                group.color_transition = 0
                group.palette_index = (group.palette_index + 1) % len(COLOR_PALETTES)

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
                
                # Get current color (with transition)
                current_palette = COLOR_PALETTES[group.palette_index]
                next_palette = COLOR_PALETTES[(group.palette_index + 1) % len(COLOR_PALETTES)]
                current_color = current_palette[circle['color_index']]
                next_color = next_palette[circle['color_index']]
                color = lerp_color(current_color, next_color, group.color_transition)
                
                # Update trail
                circle['trail'].append((x, y, color))
                
                # Update time offset
                circle['time_offset'] += dt

        # Check if we need a new group
        for group in self.groups[:]:
            all_circles_outside = all(
                circle['radius'] > screen_diagonal / 1.5
                for circle in group.circles
            )
            if all_circles_outside:
                # Start a new group but keep the old one
                new_group = OrbitGroup(min_circles, max_circles, base_expansion_rate, 
                                     rate_variation, rotation_speed)
                self.groups.append(new_group)
                break

    def draw(self, screen):
        for group in self.groups:
            for circle in group.circles:
                # Draw trail
                for x, y, color in circle['trail']:
                    if not (0 <= x <= WIDTH and 0 <= y <= HEIGHT):
                        continue
                    
                    trail_radius = self.circle_radius
                    circle_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(circle_surface, (*color, 64), 
                                    (trail_radius, trail_radius), trail_radius)
                    screen.blit(circle_surface, (x - trail_radius, y - trail_radius))
                
                # Draw current circle
                x = self.center_x + math.cos(circle['angle']) * circle['radius']
                y = self.center_y + math.sin(circle['angle']) * circle['radius']
                if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                    pygame.draw.circle(screen, color, (int(x), int(y)), self.circle_radius)

# Initial parameters
MIN_CIRCLES = 3
MAX_CIRCLES = 8
BASE_EXPANSION_RATE = 30
RATE_VARIATION = 0.5
ROTATION_SPEED = 2
CIRCLE_SIZE = 4

# Create circle system
circle_system = Circle(MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE, RATE_VARIATION, ROTATION_SPEED)

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == min_circles_slider:
                MIN_CIRCLES = int(event.value)
            elif event.ui_element == max_circles_slider:
                MAX_CIRCLES = max(MIN_CIRCLES, int(event.value))
            elif event.ui_element == expansion_rate_slider:
                BASE_EXPANSION_RATE = event.value
            elif event.ui_element == rate_variation_slider:
                RATE_VARIATION = event.value
            elif event.ui_element == rotation_speed_slider:
                ROTATION_SPEED = event.value
            elif event.ui_element == circle_size_slider:
                CIRCLE_SIZE = event.value
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == clear_trails_button:
                for group in circle_system.groups:
                    for circle in group.circles:
                        circle['trail'] = []
                
        manager.process_events(event)
    
    manager.update(time_delta)
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update and draw circle system
    circle_system.update(time_delta, MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE, 
                        RATE_VARIATION, ROTATION_SPEED, CIRCLE_SIZE)
    circle_system.draw(screen)
    
    # Draw UI
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()