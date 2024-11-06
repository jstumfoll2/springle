import pygame
import math
import colorsys
import pygame_gui
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 1280
HEIGHT = 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Expanding Orbital Patterns")

# Initialize UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create UI elements
min_circles_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 20), (200, 20)),
    start_value=3,
    value_range=(3, 15),
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
    value_range=(3, 15),
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
    value_range=(1, 1000),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 105), (200, 20)),
    text='Base Expansion Rate',
    manager=manager
)

rate_variation_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 170), (200, 20)),
    start_value=5,
    value_range=(0.01, 20.0),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 155), (200, 20)),
    text='Expansion Rate Variation',
    manager=manager
)

rotation_speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 220), (200, 20)),
    start_value=1,
    value_range=(0.1, 10),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 205), (200, 20)),
    text='Rotation Speed',
    manager=manager
)

base_size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 270), (200, 20)),
    start_value=20,
    value_range=(2, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 255), (200, 20)),
    text='Base Circle Size',
    manager=manager
)

# Add new slider after the base_size_slider:
fade_duration_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 320), (200, 20)),
    start_value=10.0,
    value_range=(1.0, 30.0),  # 1 to 30 seconds
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 305), (200, 20)),
    text='Fade Duration (seconds)',
    manager=manager
)

# Move clear trails button down
clear_trails_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 370), (200, 30)),
    text='Clear Trails',
    manager=manager
)

# Color palettes (each with 12 colors)
COLOR_PALETTES = [
    # Sunset Gradient
    [(255, 171, 0), (255, 140, 0), (255, 99, 71), (255, 69, 0), (255, 45, 0), 
     (255, 20, 47), (255, 0, 80), (225, 0, 108), (195, 0, 126), (165, 0, 168),
     (135, 0, 189), (105, 0, 204)],
    
    # Ocean Depths
    [(64, 224, 208), (0, 216, 217), (0, 186, 217), (0, 156, 217), (0, 116, 217),
     (30, 144, 255), (0, 191, 255), (135, 206, 250), (0, 150, 255), (0, 120, 255),
     (0, 90, 255), (0, 60, 255)],
    
    # Forest Canopy
    [(34, 139, 34), (0, 128, 0), (0, 100, 0), (107, 142, 35), (85, 107, 47),
     (154, 205, 50), (124, 252, 0), (50, 205, 50), (46, 139, 87), (60, 179, 113),
     (32, 178, 170), (47, 79, 79)],
    
    # Neon Lights
    [(255, 0, 255), (255, 0, 204), (255, 0, 153), (255, 0, 102), (255, 0, 51),
     (255, 51, 0), (255, 102, 0), (255, 153, 0), (255, 204, 0), (255, 255, 0),
     (204, 255, 0), (153, 255, 0)],
    
    # Galaxy Nebula
    [(123, 31, 162), (84, 13, 110), (32, 0, 255), (103, 58, 183), (156, 39, 176),
     (170, 7, 107), (244, 143, 177), (199, 0, 57), (255, 87, 51), (255, 141, 0),
     (170, 0, 255), (138, 43, 226)],
     
    # Northern Lights
    [(16, 255, 133), (39, 255, 175), (80, 255, 201), (132, 255, 217), (175, 255, 228),
     (202, 255, 251), (216, 255, 204), (171, 228, 155), (128, 200, 107), (86, 172, 59),
     (43, 144, 11), (0, 116, 0)],
     
    # Desert Sands
    [(242, 209, 158), (235, 189, 118), (217, 164, 65), (191, 144, 0), (166, 123, 0),
     (140, 103, 0), (115, 82, 0), (89, 62, 0), (64, 41, 0), (38, 21, 0),
     (217, 179, 130), (230, 197, 158)],
     
    # Deep Sea
    [(0, 119, 190), (0, 147, 196), (0, 174, 203), (0, 202, 209), (0, 229, 216),
     (0, 255, 222), (0, 229, 216), (0, 202, 209), (0, 174, 203), (0, 147, 196),
     (0, 119, 190), (0, 92, 183)],
     
    # Volcanic
    [(153, 0, 0), (179, 0, 0), (204, 0, 0), (230, 0, 0), (255, 0, 0),
     (255, 26, 0), (255, 51, 0), (255, 77, 0), (255, 102, 0), (255, 128, 0),
     (255, 153, 0), (255, 179, 0)],
     
    # Cotton Candy
    [(255, 183, 213), (255, 154, 204), (255, 124, 196), (255, 95, 187), (255, 66, 179),
     (255, 36, 170), (255, 7, 162), (255, 0, 153), (255, 0, 144), (255, 0, 135),
     (255, 0, 127), (255, 0, 118)],
     
    # Emerald City
    [(0, 201, 87), (0, 178, 89), (0, 154, 91), (0, 131, 93), (0, 107, 95),
     (0, 84, 97), (0, 60, 99), (0, 37, 101), (0, 13, 103), (0, 0, 105),
     (0, 0, 107), (0, 0, 109)],
     
    # Twilight
    [(25, 25, 112), (48, 25, 112), (72, 25, 112), (95, 25, 112), (119, 25, 112),
     (142, 25, 112), (165, 25, 112), (189, 25, 112), (212, 25, 112), (236, 25, 112),
     (255, 25, 112), (255, 48, 112)],
     
    # Rainbow Sherbet
    [(255, 192, 203), (255, 182, 193), (255, 160, 122), (255, 127, 80), (255, 99, 71),
     (255, 69, 0), (255, 140, 0), (255, 165, 0), (255, 215, 0), (255, 255, 0),
     (255, 255, 224), (255, 228, 196)],
     
    # Deep Purple
    [(48, 25, 52), (72, 38, 78), (95, 50, 104), (119, 63, 130), (142, 75, 156),
     (165, 88, 182), (189, 100, 208), (212, 113, 234), (236, 125, 255), (255, 138, 255),
     (255, 150, 255), (255, 163, 255)],
     
    # Electric Blue
    [(0, 255, 255), (0, 238, 255), (0, 221, 255), (0, 204, 255), (0, 187, 255),
     (0, 170, 255), (0, 153, 255), (0, 136, 255), (0, 119, 255), (0, 102, 255),
     (0, 85, 255), (0, 68, 255)],
     
    # Autumn Leaves
    [(255, 69, 0), (255, 99, 71), (255, 127, 80), (255, 140, 0), (255, 165, 0),
     (255, 191, 0), (255, 215, 0), (255, 239, 0), (255, 255, 0), (238, 232, 170),
     (240, 230, 140), (189, 183, 107)],
     
    # Cyberpunk
    [(255, 0, 128), (255, 0, 255), (178, 0, 255), (102, 0, 255), (25, 0, 255),
     (0, 128, 255), (0, 255, 255), (0, 255, 128), (0, 255, 0), (128, 255, 0),
     (255, 255, 0), (255, 128, 0)],
     
    # Arctic Aurora
    [(127, 255, 212), (64, 224, 208), (0, 255, 255), (0, 255, 127), (60, 179, 113),
     (46, 139, 87), (34, 139, 34), (50, 205, 50), (144, 238, 144), (152, 251, 152),
     (143, 188, 143), (102, 205, 170)],
     
    # Cosmic Dust
    [(148, 0, 211), (138, 43, 226), (123, 104, 238), (106, 90, 205), (72, 61, 139),
     (147, 112, 219), (153, 50, 204), (186, 85, 211), (128, 0, 128), (216, 191, 216),
     (221, 160, 221), (238, 130, 238)],
     
    # Tropical Paradise
    [(0, 255, 127), (0, 250, 154), (0, 255, 127), (124, 252, 0), (127, 255, 0),
     (173, 255, 47), (50, 205, 50), (152, 251, 152), (144, 238, 144), (0, 255, 127),
     (60, 179, 113), (46, 139, 87)],
     
    # Candy Shop
    [(255, 105, 180), (255, 182, 193), (255, 192, 203), (255, 20, 147), (219, 112, 147),
     (255, 160, 122), (255, 127, 80), (255, 99, 71), (255, 69, 0), (255, 140, 0),
     (255, 160, 122), (255, 127, 80)],
     
    # Deep Ocean
    [(0, 0, 139), (0, 0, 205), (0, 0, 255), (30, 144, 255), (0, 191, 255),
     (135, 206, 235), (135, 206, 250), (176, 224, 230), (173, 216, 230), (0, 255, 255),
     (127, 255, 212), (64, 224, 208)],
     
    # Cherry Blossom
    [(255, 192, 203), (255, 182, 193), (255, 160, 122), (255, 127, 80), (255, 99, 71),
     (255, 69, 0), (255, 0, 0), (255, 20, 147), (255, 105, 180), (255, 182, 193),
     (255, 192, 203), (219, 112, 147)],
     
    # Golden Hour
    [(255, 215, 0), (255, 223, 0), (255, 231, 0), (255, 239, 0), (255, 247, 0),
     (255, 255, 0), (255, 247, 0), (255, 239, 0), (255, 231, 0), (255, 223, 0),
     (255, 215, 0), (255, 207, 0)],
     
    # Moonlight
    [(25, 25, 112), (0, 0, 128), (0, 0, 139), (0, 0, 205), (0, 0, 255),
     (65, 105, 225), (100, 149, 237), (135, 206, 235), (135, 206, 250), (176, 224, 230),
     (173, 216, 230), (240, 248, 255)]
]

def lerp_color(color1, color2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(color1, color2))

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
        self.palette_index = random.randint(0, len(COLOR_PALETTES) - 1)
        self.color_transition = 0
        self.active = True  # New flag to track if group is still moving
        self.create_circles(self.radius)

    def create_circles(self, radius):
        self.circles = []
        for i in range(self.num_circles):
            angle = (2 * math.pi * i) / self.num_circles
            self.circles.append({
                'angle': angle,
                'radius': radius,
                'color_index': i % len(COLOR_PALETTES[0]),
                'trail': [],
                'time_offset': self.time_offset,
                'last_trail_pos': None,
                'size_variation': random.uniform(0.8, 1.2)  # Random size multiplier
            })

class Circle:
    def __init__(self, min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed, base_size):
        self.groups = [OrbitGroup(min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed, base_size, 0)]
        self.center_x = WIDTH // 2
        self.center_y = HEIGHT // 2
        self.color_transition_speed = 0.2
        self.spawn_cooldown = 0  # Add cooldown for spawning new groups
        self.fade_duration = 10.0  # Time in seconds for trails to fully fade
        self.last_mouse_pos = None
        self.mouse_positions = []  # Store recent mouse positions for velocity calculation
        self.mouse_history_length = 5  # Number of positions to track
        self.add_mouse_group = False
        self.onegrouppermouseclick = True
        
    def calculate_mouse_vector(self, current_pos):
        if not self.mouse_positions:
            return (0, 0, 0)  # x, y, speed
            
        # Calculate average velocity from recent mouse positions
        dx = current_pos[0] - self.mouse_positions[0][0]
        dy = current_pos[1] - self.mouse_positions[0][1]
        time_diff = sum(p[2] for p in self.mouse_positions) / len(self.mouse_positions)
        
        if time_diff > 0:
            speed = math.sqrt(dx * dx + dy * dy) / time_diff
            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
            return (dx, dy, min(speed, 1000))  # Cap speed to prevent extreme values
        return (0, 0, 0)

    def add_mouse_position(self, pos, dt):
        self.mouse_positions.append((pos[0], pos[1], dt))
        if len(self.mouse_positions) > self.mouse_history_length:
            # self.mouse_positions.pop(0)
            self.add_mouse_group = True

    def create_mouse_group(self, pos, min_circles, max_circles, base_expansion_rate, 
                        rate_variation, rotation_speed, base_size):
        # Calculate mouse movement vector
        mouse_dx, mouse_dy, mouse_speed = self.calculate_mouse_vector(pos)
        
        # Base angle from mouse movement
        base_angle = math.atan2(mouse_dy, mouse_dx) if (mouse_dx or mouse_dy) else 0
        speed_factor = max(0.2, min(2.0, mouse_speed / 200))  # Scale mouse speed to reasonable range
        
        radius = math.sqrt(math.pow(mouse_dx, 2) + math.pow(mouse_dy, 2))
        
        # Create new group with mouse-influenced parameters
        new_group = OrbitGroup(min_circles, max_circles, base_expansion_rate, 
                            rate_variation, speed_factor, base_size, radius)
        
        # clear mouse history for next click  
        self.mouse_positions.clear()
        
        return new_group
       
    def is_circle_visible(self, x, y, radius, screen_diagonal):
        # Check if circle is still within a visible range
        distance_from_center = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        return distance_from_center <= screen_diagonal / 1.5
    
    def calculate_circle_size(self, radius, base_size, size_variation):
        # Size grows with radius but levels off
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        return base_size * size_variation * size_factor

    def should_add_trail_point(self, x, y, last_pos, circle_size):
        if last_pos is None:
            return True
        # Calculate distance between points
        dx = x - last_pos[0]
        dy = y - last_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        # Add point if distance is greater than a fraction of the circle size
        return distance >= circle_size * 0.5

    def is_group_active(self, group, screen_diagonal):
        # Check if any circle in the group is still within active range
        for circle in group.circles:
            x = self.center_x + math.cos(circle['angle']) * circle['radius']
            y = self.center_y + math.sin(circle['angle']) * circle['radius']
            distance_from_center = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
            if distance_from_center <= screen_diagonal / 1.5:
                return True
        return False
    
    def update(self, dt, min_circles, max_circles, base_expansion_rate, rate_variation, 
              rotation_speed, base_size, mouse_button_pressed, mouse_pos, fade_duration):
        screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        need_new_group = False
        
        # Update fade duration from slider
        self.fade_duration = fade_duration
        
        # Handle mouse input
        if mouse_button_pressed and mouse_pos:
            self.add_mouse_position(mouse_pos, dt)
            if self.add_mouse_group and self.onegrouppermouseclick:
                self.onegrouppermouseclick = False
                new_group = self.create_mouse_group(mouse_pos, min_circles, max_circles,
                                                  base_expansion_rate, rate_variation,
                                                  rotation_speed, base_size)
                self.groups.append(new_group)
                
                self.add_mouse_group = False    
                self.spawn_cooldown = 0.1  # Short cooldown for mouse spawning
        
        if mouse_button_pressed is False:
            self.onegrouppermouseclick = True
        
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= dt

        active_groups = sum(1 for group in self.groups if group.active)
        
        for group in self.groups:
            # Update all trails with age
            for circle in group.circles:
                updated_trail = []
                for point in circle['trail']:
                    x, y, color, size, age = point
                    new_age = age + dt
                    if new_age < self.fade_duration:
                        updated_trail.append((x, y, color, size, new_age))
                circle['trail'] = updated_trail

            if not group.active:
                continue
                
            if not self.is_group_active(group, screen_diagonal):
                group.active = False
                if self.spawn_cooldown <= 0:
                    need_new_group = True
                    self.spawn_cooldown = 2.0
                continue

            group.base_expansion_rate = base_expansion_rate
            group.rate_variation = rate_variation
            group.rotation_speed = rotation_speed
            group.base_size = base_size
            
            group.color_transition += dt * self.color_transition_speed
            if group.color_transition >= 1:
                group.color_transition = 0
                group.palette_index = (group.palette_index + 1) % len(COLOR_PALETTES)

            for circle in group.circles:
                # Get circle's center (either mouse position or screen center)
                center_x = circle.get('center_x', self.center_x)
                center_y = circle.get('center_y', self.center_y)
                
                # Calculate expansion rate with mouse speed influence
                speed_factor = circle.get('speed_factor', 1.0)
                variation = math.sin((circle['time_offset'] + group.time_offset) * 0.5) * rate_variation
                current_expansion_rate = base_expansion_rate * (1 + variation) * speed_factor
                
                # Update radius
                circle['radius'] += current_expansion_rate * dt
                
                # Calculate position using either mouse direction or normal orbital motion
                if 'direction_x' in circle:
                    # Mouse-directed movement with orbital component
                    base_angle = circle['base_angle']
                    radius = circle['radius']
                    orbit_offset = math.sin(circle['time_offset'] * rotation_speed) * math.pi/4  # Add orbital motion
                    current_angle = base_angle + orbit_offset
                    
                    # Combine linear and orbital motion
                    dx = math.cos(current_angle)
                    dy = math.sin(current_angle)
                    
                    # Calculate position with both directional and orbital components
                    x = center_x + radius * dx
                    y = center_y + radius * dy
                else:
                    # Normal orbital motion
                    circle['angle'] += rotation_speed * (1 + circle['radius'] / screen_diagonal) * dt
                    x = center_x + math.cos(circle['angle']) * circle['radius']
                    y = center_y + math.sin(circle['angle']) * circle['radius']
                
                current_size = self.calculate_circle_size(circle['radius'], base_size, circle['size_variation'])
                
                # Color calculation
                current_palette = COLOR_PALETTES[group.palette_index]
                next_palette = COLOR_PALETTES[(group.palette_index + 1) % len(COLOR_PALETTES)]
                current_color = current_palette[circle['color_index']]
                next_color = next_palette[circle['color_index']]
                color = lerp_color(current_color, next_color, group.color_transition)
                
                if self.should_add_trail_point(x, y, circle.get('last_trail_pos'), current_size):
                    circle['trail'].append((x, y, color, current_size, 0.0))
                    circle['last_trail_pos'] = (x, y)
                
                circle['time_offset'] += dt

        # Automatic group spawning
        if need_new_group and active_groups < 10:
            new_group = OrbitGroup(min_circles, max_circles, base_expansion_rate, 
                                 rate_variation, rotation_speed, base_size, 0)
            self.groups.append(new_group)

    def draw(self, screen):
        for group in self.groups:
            for circle in group.circles:
                # Draw trail
                for x, y, color, size, age in circle['trail']:
                    if not (0 <= x <= WIDTH and 0 <= y <= HEIGHT):
                        continue
                    
                    # Calculate opacity based on age
                    fade_progress = age / self.fade_duration
                    alpha = int(64 * (1 - fade_progress))  # Start at 64 and fade to 0
                    
                    if alpha > 0:  # Only draw if not completely transparent
                        circle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                        pygame.draw.circle(circle_surface, (*color, alpha), 
                                        (size, size), size)
                        screen.blit(circle_surface, (x - size, y - size))
                
                # Draw current circle only if group is active
                if group.active:
                    x = self.center_x + math.cos(circle['angle']) * circle['radius']
                    y = self.center_y + math.sin(circle['angle']) * circle['radius']
                    if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
                        # Calculate current color
                        current_palette = COLOR_PALETTES[group.palette_index]
                        next_palette = COLOR_PALETTES[(group.palette_index + 1) % len(COLOR_PALETTES)]
                        current_color = current_palette[circle['color_index']]
                        next_color = next_palette[circle['color_index']]
                        circle_color = lerp_color(current_color, next_color, group.color_transition)
                        
                        current_size = self.calculate_circle_size(circle['radius'], 
                                                            group.base_size, 
                                                            circle['size_variation'])
                        pygame.draw.circle(screen, circle_color, (int(x), int(y)), int(current_size))
                        
# Initial parameters
MIN_CIRCLES = 3
MAX_CIRCLES = 15
BASE_EXPANSION_RATE = 30
RATE_VARIATION = 5
ROTATION_SPEED = 1
BASE_SIZE = 20
FADE_DURATION = 10.0

# Create circle system
circle_system = Circle(MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE, RATE_VARIATION, ROTATION_SPEED, BASE_SIZE)

# Modify main game loop to handle mouse input
running = True
clock = pygame.time.Clock()
mouse_button_pressed = False

while running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_button_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_button_pressed = False
            
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
            elif event.ui_element == base_size_slider:
                BASE_SIZE = event.value
            elif event.ui_element == fade_duration_slider:
                FADE_DURATION = event.value
                
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == clear_trails_button:
                for group in circle_system.groups:
                    for circle in group.circles:
                        circle['trail'] = []
                        circle['last_trail_pos'] = None
                
        manager.process_events(event)
    
    manager.update(time_delta)
    
    # Get current mouse position if button is pressed
    mouse_pos = pygame.mouse.get_pos() if mouse_button_pressed else None
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update and draw circle system with mouse input
    circle_system.update(time_delta, MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE, 
                        RATE_VARIATION, ROTATION_SPEED, BASE_SIZE, 
                        mouse_button_pressed, mouse_pos, FADE_DURATION)
    
    circle_system.draw(screen)
    
    # Draw UI
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()