import pygame
import math
import random

# Local imports
from OrbitGroup import OrbitGroup
from SpingleColors import SpingleColors
from MouseControlSystem import MouseControlSystem

MAX_GROUPS = 7
class SpringleCircle:
    def __init__(self, min_circles, max_circles, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration,  
                 base_size, WIDTH, HEIGHT):
        
        self.groups = [OrbitGroup(min_circles, max_circles, 0, base_size,
                                  radial_velocity, angular_velocity,
                                  radial_acceleration, angular_acceleration, False)]
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        
        self.color_transition_speed = 0.2
        self.spawn_cooldown = 0  # Add cooldown for spawning new groups
        self.fade_duration = 10.0  # Time in seconds for trails to fully fade

        self.colors = SpingleColors()  # Create instance of SpingleColors
        self.mouse_control = MouseControlSystem()

    def should_add_trail_point(self, new_pos, last_pos, circle_size, space_factor, dt=0):
        """Determine if a new trail point should be added based on distance."""
        if last_pos is None:
            return True
        dx = new_pos[0] - last_pos[0]
        dy = new_pos[1] - last_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return (distance >= circle_size * space_factor)

    def calculate_circle_size(self, radius, base_size, size_variation):
        """Calculate circle size based on radius from center."""
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        return base_size * size_variation * size_factor
    
    def update(self, dt, min_circles, max_circles, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration, 
                 base_size, mouse_button_pressed, mouse_pos, fade_duration,
              space_factor):
        """Update all groups and handle mouse interaction."""
        # Update fade duration from slider
        self.fade_duration = fade_duration
        need_new_group = False
        
        # Handle mouse input
        if mouse_button_pressed and mouse_pos:
            if not self.mouse_control.is_dragging:
                # Start new drag
                self.mouse_control.start_drag(mouse_pos)
                
                # Create new group at click position
                new_group = OrbitGroup(
                    min_circles, max_circles, 0, base_size, 
                    0, 0,
                    0, 0, True
                )
                new_group.set_group_position(mouse_pos, self.center)
                self.groups.append(new_group)
            else:
                # Update existing drag
                self.mouse_control.update_drag(mouse_pos, dt)
                
                # Update most recent group's position
                if self.groups:
                    latest_group = self.groups[-1]
                    latest_group.set_group_position(mouse_pos, self.center)
        
        elif self.mouse_control.is_dragging:
            # Handle mouse release
            velocity = self.mouse_control.end_drag()
            if self.groups:
                latest_group = self.groups[-1]
                latest_group.handle_mouse_release(mouse_pos, velocity, self.center)
        
        # Update spawn cooldown
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= dt

        # Update all groups
        active_groups = 0
        for group in self.groups:
            if not group.active:
                continue

            active_groups += 1
                
            # Update parameters from sliders
            group.update_circle_acceleration(radial_acceleration, angular_acceleration)

            # TODO update the base size via some randomizing function
            group.update_circle_size(base_size)
            
            # Update color transition
            group.color_transition += dt * self.color_transition_speed
            if group.color_transition >= 1:
                group.color_transition = 0
                group.palette_index = (group.palette_index + 1) % self.colors.numPatterns()
            
            # Update circle positions
            group.update_circle_positions(dt)
            
            # Update trails
            for circle in group.circles:
                # Get current position
                x, y = group.get_circle_cartesian_pos(circle, self.center)
                
                # Calculate circle properties
                current_size = self.calculate_circle_size(
                    circle['motion'].radius,
                    circle['base_size'],
                    circle['size_variation']
                )
                
                # Calculate color
                color = self.colors.getColor(group.palette_index, circle['color_index'], group.color_transition)
                
                # Add trail point if needed
                if self.should_add_trail_point((x, y), circle['last_trail_pos'], 
                                             current_size, space_factor):
                    circle['trail'].append((x, y, color, current_size, 0.0))
                    circle['last_trail_pos'] = (x, y)
                
                # Update trail ages and remove old points
                updated_trail = []
                for point in circle['trail']:
                    px, py, pcolor, psize, age = point
                    new_age = age + dt
                    if new_age < self.fade_duration:
                        updated_trail.append((px, py, pcolor, psize, new_age))
                circle['trail'] = updated_trail
            
            # Check if group is still visible
            if not group.is_circle_visible((self.WIDTH, self.HEIGHT)):
                group.active = False
    
        if self.spawn_cooldown <= 0:
                need_new_group = True
                self.spawn_cooldown = 4.0
                
        # Spawn new group if needed
        if need_new_group and active_groups < MAX_GROUPS:
            new_group = OrbitGroup(
                    min_circles, max_circles, 0, base_size, 
                    radial_velocity, angular_velocity,
                    radial_acceleration, angular_acceleration, False
                )
            self.groups.append(new_group)

    def draw(self, screen, max_alpha):
        """Draw all groups and their trails."""
        drawable_elements = []
        
        for group in self.groups:
            if not group.active:
                continue
                
            # Add trails
            for circle in group.circles:
                for x, y, color, size, age in circle['trail']:
                    if 0 <= x <= self.WIDTH and 0 <= y <= self.HEIGHT:
                        fade_progress = age / self.fade_duration
                        alpha = int(max_alpha * (1 - fade_progress))
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
            
            # Add current circles
            for circle in group.circles:
                x, y = group.get_circle_cartesian_pos(circle, self.center)
                
                if 0 <= x <= self.WIDTH*1.2 and 0 <= y <= self.HEIGHT*1.2:
                    color = self.colors.getColor(group.palette_index, circle['color_index'], group.color_transition)
                    
                    size = self.calculate_circle_size(
                        circle['motion'].radius,
                        circle['base_size'],
                        circle['size_variation']
                    )
                    
                    drawable_elements.append({
                        'type': 'circle',
                        'x': x,
                        'y': y,
                        'color': color,
                        'size': size,
                        'age': -1,
                        'alpha': 255
                    })
        
        # Sort by age so older trails are drawn first
        drawable_elements.sort(key=lambda x: x.get('age', -1), reverse=True)
        
        # Draw all elements
        for element in drawable_elements:
            circle_surface = pygame.Surface((element['size'] * 2, element['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (*element['color'], element['alpha']),
                             (element['size'], element['size']), element['size'])
            screen.blit(circle_surface, (element['x'] - element['size'],
                                       element['y'] - element['size']))
    