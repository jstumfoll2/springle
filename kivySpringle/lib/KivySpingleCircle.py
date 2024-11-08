from kivy.graphics import Color, Ellipse
from kivy.graphics.texture import Texture
# from kivy.core.image import Image
import math
# from functools import lru_cache
# import numpy as np

from lib.SpingleColors import SpingleColors
from lib.MouseControlSystem import MouseControlSystem
from lib.SpringleParams import SpringleParams
from lib.OrbitGroup import OrbitGroup

class GradientCache:
    """Optimized cache system for gradient textures in Kivy"""
    def __init__(self, size_step=2, alpha_step=16):
        self.size_step = size_step
        self.alpha_step = alpha_step
        self._cache = {}
        
    def get_key(self, size, color, alpha, sharpness):
        """Get cache key with minimal computation"""
        size_rounded = round(size / self.size_step) * self.size_step
        alpha_rounded = round(alpha / self.alpha_step) * self.alpha_step
        sharpness_rounded = round(sharpness * 10) / 10  # Round to nearest 0.1
        return (size_rounded, color[0], color[1], color[2], alpha_rounded, sharpness_rounded)
    
    def get(self, key):
        """Get item from cache"""
        return self._cache.get(key)
    
    def set(self, key, texture):
        """Set item in cache"""
        self._cache[key] = texture
        
        # Simple cache size management
        if len(self._cache) > 1000:  # Arbitrary limit
            # Remove oldest 20% of entries
            remove_count = len(self._cache) // 5
            for k in list(self._cache.keys())[:remove_count]:
                del self._cache[k]

class KivySpingleCircle:
    def __init__(self, min_circles, max_circles, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration,  
                 base_size, WIDTH, HEIGHT):
        
        # Initialize with default parameters
        self.params = SpringleParams.from_defaults()
        
        # Create initial group
        self.groups = [OrbitGroup(min_circles, max_circles, 0, base_size,
                                radial_velocity, angular_velocity,
                                radial_acceleration, angular_acceleration, False)]
        self.groups[0].creation_time = 0.0
        self.max_groups = 7
        
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        
        # System parameters
        self.color_transition_speed = 0.2
        self.spawn_cooldown_start = 4.0
        self.spawn_cooldown_current = self.spawn_cooldown_start
        self.fade_duration = 10.0
        self.simulation_time = 0.0

        # Initialize systems
        self.colors = SpingleColors()
        self.mouse_control = MouseControlSystem()
        self.mouse_control.set_screen_center(self.center)
        
        # Fading trails list
        self.fading_trails = []

        # Initialize gradient cache
        self.gradient_cache = GradientCache(size_step=2, alpha_step=16)
        self.max_cached_size = 100
    
    def _create_gradient_texture(self, size, color, alpha, sharpness=2.0):
        """Create a circular gradient texture for Kivy"""
        import numpy as np
        
        # Create texture
        texture_size = int(size * 2)
        # Ensure even size for texture
        texture_size = texture_size + (texture_size % 2)
        
        # Create gradient data
        x = np.linspace(-1, 1, texture_size)
        y = np.linspace(-1, 1, texture_size)
        xx, yy = np.meshgrid(x, y)
        
        # Calculate radial gradient with adjustable sharpness
        distance = np.sqrt(xx*xx + yy*yy)
        # Apply sharpness to the gradient calculation
        gradient = np.clip(1 - distance, 0, 1) ** sharpness
        
        # Create RGBA array
        rgba = np.zeros((texture_size, texture_size, 4), dtype=np.uint8)
        rgba[..., 0] = np.minimum(color[0] * gradient, 255).astype(np.uint8)
        rgba[..., 1] = np.minimum(color[1] * gradient, 255).astype(np.uint8)
        rgba[..., 2] = np.minimum(color[2] * gradient, 255).astype(np.uint8)
        rgba[..., 3] = np.minimum(alpha * gradient, alpha).astype(np.uint8)
        
        # Create Kivy texture
        texture = Texture.create(size=(texture_size, texture_size), colorfmt='rgba')
        texture.blit_buffer(rgba.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        
        return texture
    
    def _get_cache_key(self, size: float, color: tuple, alpha: int, sharpness: float) -> tuple:
        """Get cache key with minimal computation"""
        # Round size and alpha to reduce cache variations
        size_rounded = round(size / self.size_step) * self.size_step
        alpha_rounded = round(alpha / self.alpha_step) * self.alpha_step
        sharpness_rounded = round(sharpness * 10) / 10  # Round to nearest 0.1
        return (size_rounded, color[0], color[1], color[2], alpha_rounded, sharpness_rounded)
    
    def _get_cached_gradient(self, size, color, alpha, sharpness):
        """Get or create cached gradient texture"""
        cache_key = self.gradient_cache.get_key(size, color, alpha, sharpness)
        texture = self.gradient_cache.get(cache_key)
        
        if texture is None and size <= self.max_cached_size:
            texture = self._create_gradient_texture(size, color, alpha, sharpness)
            self.gradient_cache.set(cache_key, texture)
            
        return texture
    
    def draw(self, canvas, max_alpha, gradient_sharpness=2.0):
        """Draw all circles and trails using Kivy graphics instructions"""
        # First draw the background rectangle
        with canvas:
            # Clear any previous drawing
            canvas.clear()
            
            # Draw all elements in order
            group_elements = {}
            
            # Add fading trails
            for creation_time, (x, y, color, size, age) in self.fading_trails:
                fade_progress = age / self.fade_duration
                eased_fade = 1 - (fade_progress * fade_progress * fade_progress)
                alpha = int(max(0, max_alpha * eased_fade))
                
                if alpha > 0:
                    if creation_time not in group_elements:
                        group_elements[creation_time] = []
                    group_elements[creation_time].append({
                        'type': 'trail',
                        'x': x,
                        'y': y,
                        'color': color,
                        'size': size,
                        'alpha': alpha
                    })
            
            # Add active groups' elements
            for group in self.groups:
                if not group.active:
                    continue
                    
                if group.creation_time not in group_elements:
                    group_elements[group.creation_time] = []
                
                # Add trails
                for circle in group.circles:
                    for x, y, color, size, age, _ in circle['trail']:
                        fade_progress = age / self.fade_duration
                        eased_fade = 1 - (fade_progress * fade_progress * fade_progress)
                        alpha = int(max(0, max_alpha * eased_fade))
                        
                        if alpha > 0:
                            group_elements[group.creation_time].append({
                                'type': 'trail',
                                'x': x,
                                'y': y,
                                'color': color,
                                'size': size,
                                'alpha': alpha
                            })
                    
                    # Add current circles
                    x, y = group.get_circle_cartesian_pos(circle, self.center)
                    if (0 <= x <= self.WIDTH * 1.2 and 0 <= y <= self.HEIGHT * 1.2):
                        color = self.colors.getColor(
                            group.palette_index, 
                            circle['color_index'], 
                            group.color_transition
                        )
                        size = self.calculate_circle_size(
                            circle['motion'].radius,
                            circle['base_size'],
                            circle['size_variation']
                        )
                        
                        group_elements[group.creation_time].append({
                            'type': 'circle',
                            'x': x,
                            'y': y,
                            'color': color,
                            'size': size,
                            'alpha': 255
                        })
            
            # Draw all elements using Kivy graphics instructions
            for creation_time in sorted(group_elements.keys()):
                for element in group_elements[creation_time]:
                    size = max(4, element['size'])  # Ensure minimum size
                    texture = self._get_cached_gradient(
                        size,
                        element['color'],
                        element['alpha'],
                        gradient_sharpness  # Pass sharpness parameter
                    )
                    
                    if texture:
                        size_px = size * 2
                        Color(1, 1, 1, 1)  # Reset color to white for texture blending
                        Ellipse(
                            texture=texture,
                            pos=(element['x'] - size,
                                 element['y'] - size),
                            size=(size_px, size_px)
                        )
    
    # The rest of the methods remain largely unchanged
    def calculate_circle_size(self, radius, base_size, size_variation):
        """Calculate circle size based on radius from center."""
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        return base_size * size_variation * size_factor
    
    def set_max_groups(self, value):
        """Set the maximum number of allowed groups."""
        self.max_groups = value
        
    def create_new_group(self, min_circles, max_circles, radial_velocity, angular_velocity, base_size):
        """Create a new orbit group."""
        new_group = OrbitGroup(
            min_circles,
            max_circles,
            0,
            base_size,
            radial_velocity,
            angular_velocity,
            0,  # Initial radial acceleration
            0,  # Initial angular acceleration
            False  # Not a mouse group
        )
        new_group.creation_time = self.simulation_time
        self.groups.append(new_group)
        return new_group
        
    def update(self, dt, params):
        """Update all groups and handle mouse interaction."""
        # Update simulation time
        self.simulation_time += dt
        
        self.fade_duration = params.fade_duration
        need_new_group = False
        
        # Handle mouse input
        if params.mouse_button_pressed and params.mouse_pos:
            if not self.mouse_control.is_dragging:
                self.mouse_control.start_drag(params.mouse_pos)
                new_group = OrbitGroup(
                    params.min_circles, params.max_circles, 0, params.base_size, 
                    0, 0, 0, 0, True
                )
                new_group.creation_time = self.simulation_time
                new_group.set_group_position(params.mouse_pos, self.center)
                self.groups.append(new_group)
            else:
                self.mouse_control.update_drag(params.mouse_pos, dt)
                if self.groups:
                    latest_group = self.groups[-1]
                    latest_group.set_group_position(params.mouse_pos, self.center)
        
        elif self.mouse_control.is_dragging:
            velocity = self.mouse_control.end_drag()
            if self.groups:
                latest_group = self.groups[-1]
                latest_group.handle_mouse_release(params.mouse_pos, velocity, self.center)
        
        active_groups = 0
        for group in self.groups:
            was_active = group.active
            
            # Update parameters from current settings
            if group.active:
                active_groups += 1
                group.update_circle_acceleration(params.radial_acceleration, params.angular_acceleration)
                group.update_circle_size(params.base_size)
                
                # Update color transition
                group.color_transition += dt * self.color_transition_speed
                if group.color_transition >= 1:
                    group.color_transition = 0
                    group.palette_index = (group.palette_index + 1) % self.colors.numPatterns()
                
                # Update circle positions
                group.update_circle_positions(dt)
                
                # Check if group is still visible
                group.active = group.is_circle_visible((self.WIDTH, self.HEIGHT))
                
                # Update trails for active groups
                self._update_group_trails(group, dt, params.space_factor)
            
            # If group just became inactive, move its trails to fading_trails
            if was_active and not group.active:
                for circle in group.circles:
                    if circle['trail']:
                        self.fading_trails.extend([
                            (group.creation_time, (x, y, color, size, age))
                            for x, y, color, size, age, _ in circle['trail']
                        ])
                        circle['trail'] = []
        
        # Update fading trails
        updated_fading_trails = []
        for creation_time, (x, y, color, size, age) in self.fading_trails:
            new_age = age + dt
            if new_age < self.fade_duration:
                updated_fading_trails.append((creation_time, (x, y, color, size, new_age)))
        self.fading_trails = updated_fading_trails
        
        # Rest of update logic (spawn cooldown, new groups, etc.)
        if self.spawn_cooldown_current >= 0:
            self.spawn_cooldown_current -= dt
            
        if self.spawn_cooldown_current <= 0 and params.auto_generate:
            need_new_group = True
            self.spawn_cooldown_current = self.spawn_cooldown_start
                
        # Update max_groups when checking for new group creation
        if need_new_group and active_groups < self.max_groups:
            new_group = OrbitGroup(
                params.min_circles, params.max_circles, 0, params.base_size, 
                params.radial_velocity, params.angular_velocity,
                params.radial_acceleration, params.angular_acceleration, False
            )
            new_group.creation_time = self.simulation_time
            self.groups.append(new_group)
            self.spawn_cooldown_current = self.spawn_cooldown_start
            
        # Only remove completely inactive groups (no trails)
        self.groups = [group for group in self.groups if group.active]

    def _update_group_trails(self, group, dt, space_factor):
        """Update trails for a single group."""
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
                circle['trail'].append((x, y, color, current_size, 0.0, self.simulation_time))
                circle['last_trail_pos'] = (x, y)
            
            # Update trail ages and remove old points
            updated_trail = []
            for point in circle['trail']:
                px, py, pcolor, psize, age, creation_time = point
                new_age = age + dt
                if new_age < self.fade_duration:
                    updated_trail.append((px, py, pcolor, psize, new_age, creation_time))
            circle['trail'] = updated_trail

    def should_add_trail_point(self, new_pos, last_pos, circle_size, space_factor, dt=0):
        """Determine if a new trail point should be added based on distance."""
        if last_pos is None:
            return True
        dx = new_pos[0] - last_pos[0]
        dy = new_pos[1] - last_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return (distance >= circle_size * space_factor)