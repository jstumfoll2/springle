import pygame
import math
import random

# Local imports
from OrbitGroup import OrbitGroup
from SpingleColors import SpingleColors

class SpringleCircle:
    def __init__(self, min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed, base_size, WIDTH, HEIGHT):
        self.groups = [OrbitGroup(min_circles, max_circles, base_expansion_rate, rate_variation, rotation_speed, base_size, 0)]
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
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
        self.colors = SpingleColors()  # Create instance of SpingleColors
        
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
        speed_factor = max(0.2, min(2.0, mouse_speed / 50))  # Scale mouse speed to reasonable range
        
        radius = math.sqrt(math.pow(pos[0], 2) + math.pow(pos[1], 2))/4
        
        # Create new group with mouse-influenced parameters
        new_group = OrbitGroup(min_circles, max_circles, base_expansion_rate, 
                            rate_variation, speed_factor, base_size, radius)
        
        # clear mouse history for next click  
        self.mouse_positions.clear()
        
        return new_group
       
    def is_circle_visible(self, x, y, radius, screen_diagonal):
        # Check if circle is still within a visible range
        distance_from_center = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        return distance_from_center <= screen_diagonal / 1.3
    
    def calculate_circle_size(self, radius, base_size, size_variation):
        # Size grows with radius but levels off
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        return base_size * size_variation * size_factor

    def should_add_trail_point(self, x, y, last_pos, circle_size, space_factor):
        if last_pos is None:
            return True
        # Calculate distance between points
        dx = x - last_pos[0]
        dy = y - last_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        # Add point if distance is greater than a fraction of the circle size
        return distance >= circle_size * space_factor

    def is_group_active(self, group, screen_diagonal):
        # Check if any circle in the group is still within active range
        for circle in group.circles:
            x = self.center_x + math.cos(circle['angle']) * circle['radius']
            y = self.center_y + math.sin(circle['angle']) * circle['radius']
            distance_from_center = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
            if distance_from_center <= screen_diagonal / 1.2:
                return True
        return False
    

    def update(self, dt, min_circles, max_circles, base_expansion_rate, rate_variation, 
              rotation_speed, base_size, mouse_button_pressed, mouse_pos, fade_duration,
              space_factor):
        screen_diagonal = math.sqrt(self.WIDTH**2 + self.HEIGHT**2)
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
            group.rotation_speed = rotation_speed * (random.uniform(0, 2.5)-1.25)
            group.base_size = base_size
            
            group.color_transition += dt * self.color_transition_speed
            if group.color_transition >= 1:
                group.color_transition = 0
                group.palette_index = (group.palette_index + 1) % self.colors.numPatterns()

            for circle in group.circles:
                # Update angle based on group direction
                circle['angle'] += group.direction * rotation_speed * (1 + circle['radius'] / screen_diagonal) * dt
                
                # Calculate position
                x = self.center_x + math.cos(circle['angle']) * circle['radius']
                y = self.center_y + math.sin(circle['angle']) * circle['radius']
                
                # Update radius with expansion rate
                variation = math.sin((circle['time_offset'] + group.time_offset) * 0.5) * rate_variation
                current_expansion_rate = base_expansion_rate * (1 + variation)
                circle['radius'] += current_expansion_rate * dt
                
                current_size = self.calculate_circle_size(circle['radius'], base_size, circle['size_variation'])
                
                # Color calculation
                current_palette = self.colors.getPalette(group.palette_index)
                next_palette =  self.colors.getPalette((group.palette_index + 1) % self.colors.numPatterns())
                current_color = current_palette[circle['color_index']]
                next_color = next_palette[circle['color_index']]
                color = self.colors.lerp_color(current_color, next_color, group.color_transition)
                
                if self.should_add_trail_point(x, y, circle.get('last_trail_pos'), current_size, space_factor):
                    circle['trail'].append((x, y, color, current_size, 0.0))
                    circle['last_trail_pos'] = (x, y)
                
                circle['time_offset'] += dt

        # Automatic group spawning
        if need_new_group and active_groups < 7:
            new_group = OrbitGroup(min_circles, max_circles, base_expansion_rate, 
                                 rate_variation, rotation_speed, base_size, 0)
            self.groups.append(new_group)

    def draw(self, screen, max_alpha):
        drawable_elements = []
        
        for group in self.groups:
            # Add trail points
            for circle in group.circles:
                for x, y, color, size, age in circle['trail']:
                    if 0 <= x <= self.WIDTH and 0 <= y <= self.HEIGHT:
                        fade_progress = age / self.fade_duration
                        alpha = int(max_alpha * (1 - fade_progress))  # Use max_alpha parameter
                        if alpha > 0:
                            drawable_elements.append({
                                'type': 'trail',
                                'x': x,
                                'y': y,
                                'color': color,
                                'size': size,
                                'age': age,
                                'alpha': alpha
                            })
            
            # Add active circles
            if group.active:
                for circle in group.circles:
                    x = self.center_x + math.cos(circle['angle']) * circle['radius']
                    y = self.center_y + math.sin(circle['angle']) * circle['radius']
                    if 0 <= x <= self.WIDTH*1.2 and 0 <= y <= self.HEIGHT*1.2:
                        current_palette = self.colors.getPalette(group.palette_index)
                        next_palette = self.colors.getPalette((group.palette_index + 1) % self.colors.numPatterns())
                        current_color = current_palette[circle['color_index']]
                        next_color = next_palette[circle['color_index']]
                        circle_color = self.colors.lerp_color(current_color, next_color, group.color_transition)
                        current_size = self.calculate_circle_size(circle['radius'], 
                                                            group.base_size, 
                                                            circle['size_variation'])
                        drawable_elements.append({
                            'type': 'circle',
                            'x': x,
                            'y': y,
                            'color': circle_color,
                            'size': current_size,
                            'age': -1,
                            'alpha': 255
                        })
        
        drawable_elements.sort(key=lambda x: x['age'], reverse=True)
        
        for element in drawable_elements:
            circle_surface = pygame.Surface((element['size'] * 2, element['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*element['color'], element['alpha']), 
                            (element['size'], element['size']), element['size'])
            screen.blit(circle_surface, (element['x'] - element['size'], 
                                    element['y'] - element['size']))                    
