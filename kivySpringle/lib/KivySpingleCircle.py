from kivy.graphics import Color, Ellipse
from kivy.graphics.texture import Texture
import math

from lib.SpingleColors import SpingleColors
from lib.MouseControlSystem import MouseControlSystem
from lib.SpringleParams import SpringleParams
from lib.OrbitGroup import OrbitGroup
from lib.TrailStore import TrailStore

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
                
        # Window dimensions
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        
        # Initialize with default parameters
        self.params = SpringleParams.from_defaults()
        
        # Initialize trail store
        self.trail_store = TrailStore(
            fade_duration=self.params.fade_duration,
            max_points=50000  # Adjust based on performance needs
        )
        
        # Initialize groups with an ID counter
        self._next_group_id = 0
        self.groups = [self._create_group(
            min_circles, max_circles, 0, base_size,
            radial_velocity, angular_velocity,
            radial_acceleration, angular_acceleration, False
        )]
        self.groups[0].creation_time = 0.0
        self.max_groups = 7
        
        # Add cleanup tracking
        self.last_cleanup_time = 0
        self.cleanup_interval = 1.0  # Cleanup check every second
        self.max_inactive_age = 5.0  # Maximum time to keep inactive groups
        
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

        # Initialize gradient cache
        self.gradient_cache = GradientCache(size_step=2, alpha_step=2)
        self.max_cached_size = 10000

    def _create_gradient_texture(self, size, color, alpha, sharpness=2.0):
        """Create a circular gradient texture for Kivy"""
        import numpy as np

        # Create texture
        texture_size = int(size * 1.2)
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
    
    def _create_group(self, min_circles, max_circles, radius, base_size, 
                     radial_velocity, angular_velocity,
                     radial_acceleration, angular_acceleration, 
                     is_mouse_group=False):
        """Create a new group with unique ID."""
        group = OrbitGroup(
            trail_store=self.trail_store,
            group_id=self._next_group_id,
            min_circles=min_circles,
            max_circles=max_circles,
            radius=radius,
            base_size=base_size,
            radial_velocity=radial_velocity,
            angular_velocity=angular_velocity,
            radial_acceleration=radial_acceleration,
            angular_acceleration=angular_acceleration,
            is_mouse_group=is_mouse_group
        )
        self._next_group_id += 1
        group.center = self.center  # Ensure group has center reference
        return group
    
    def create_new_group(self, min_circles, max_circles, radial_velocity, 
                        angular_velocity, base_size):
        """Create a new orbit group with current parameters"""
        new_group = OrbitGroup(
            min_circles=min_circles,
            max_circles=max_circles,
            radius=0,  # Start at center
            base_size=base_size,
            radial_velocity=radial_velocity,
            angular_velocity=angular_velocity,
            radial_acceleration=self.params.radial_acceleration,
            angular_acceleration=self.params.angular_acceleration,
            is_mouse_group=False
        )
        new_group.creation_time = self.simulation_time
        self.groups.append(new_group)
        return new_group

    def _create_new_group(self, params):
        """Separated group creation for better organization and performance."""
        new_group = self._create_group(
            params.min_circles,
            params.max_circles,
            0,
            params.base_size,
            params.radial_velocity,
            params.angular_velocity,
            params.radial_acceleration,
            params.angular_acceleration,
            False
        )
        new_group.creation_time = self.simulation_time
        self.groups.append(new_group)
    
    def _handle_mouse_input(self, mouse_pos, dt):
        """Separated mouse handling for better organization and performance."""
        if not self.mouse_control.is_dragging:
            self.mouse_control.start_drag(mouse_pos)
            new_group = self._create_group(
                self.params.min_circles,
                self.params.max_circles,
                0,
                self.params.base_size,
                0, 0, 0, 0,
                True
            )
            new_group.creation_time = self.simulation_time
            new_group.set_group_position(mouse_pos, self.center)
            self.groups.append(new_group)
        else:
            self.mouse_control.update_drag(mouse_pos, dt)
            if self.groups:
                latest_group = self.groups[-1]
                latest_group.set_group_position(mouse_pos, self.center)
                
    def clear_trails(self):
        """Clear all trails."""
        self.trail_store.clear_all()
                
    def clear_groups(self):
        """Clear all groups and associated resources."""
        self.groups.clear()
        self.trail_store.clear_all()
        
    def set_max_groups(self, value):
        """Set the maximum number of allowed groups."""
        self.max_groups = int(value)
        # Remove excess groups if needed
        while len([g for g in self.groups if g.active]) > self.max_groups:
            oldest_group = min((g for g in self.groups if g.active), 
                             key=lambda g: g.creation_time)
            self.groups.remove(oldest_group)
        
    # Optimized update method for KivySpingleCircle class
    def kivy_circle_update(self, dt, params):
        """Optimized update simulation state."""
        # Update simulation time
        self.simulation_time = self.simulation_time + dt
        
        # Handle the group updates
        active_groups = self.group_update(dt, params)

        # Handle mouse input - optimized
        self.update_mouse(dt, params)

        # check if we need to spawn new group
        self.update_group_spawn(dt, params, active_groups)

        # Batch update trail store
        self.trail_store.trail_store_update(dt, self.simulation_time, params.max_alpha)
            
    def group_update(self, dt, params):
        active_groups = 0

        for i, group in enumerate(self.groups):
            # Check if still visible
            group.active = group.is_circle_visible((self.WIDTH, self.HEIGHT))
                
            if group.active:
                active_groups += 1
                
                # Update motion parameters - only if needed
                if (group.radial_acceleration != params.radial_acceleration or 
                    group.angular_acceleration != params.angular_acceleration):
                    group.update_circle_acceleration(
                        params.radial_acceleration,
                        params.angular_acceleration
                    )
                
                if group.base_size != params.base_size:
                    group.update_circle_size(params.base_size)
                
                # Update color transition
                group.color_transition += dt * params.color_transition_speed
                if group.color_transition >= 1:
                    group.color_transition = 0
                    group.palette_index = (group.palette_index + 1) % self.colors.numPatterns()
                    
                # Update group
                group.group_update(dt, self.simulation_time, params.space_factor, self.center)
                
            else:
                self.groups.pop(i) # clear out the inactive group      
                
        return active_groups
            
    def update_mouse(self, dt, params):
        if params.mouse_button_pressed and params.mouse_pos:
            self._handle_mouse_input(params.mouse_pos, dt)
        elif self.mouse_control.is_dragging:
            velocity = self.mouse_control.end_drag()
            if self.groups:
                latest_group = self.groups[-1]
                latest_group.handle_mouse_release(params.mouse_pos, velocity, self.center)
            
    def update_group_spawn(self, dt, params, active_groups):
        spawn_needed = False

        # Update spawn cooldown
        if self.spawn_cooldown_current >= 0:
            self.spawn_cooldown_current -= dt
            if self.spawn_cooldown_current <= 0 and params.auto_generate:
                spawn_needed = True
                self.spawn_cooldown_current = self.spawn_cooldown_start
        
        # Create new group if needed and under limit
        if spawn_needed and active_groups < params.max_groups:
            self._create_new_group(params)
          
        
    def draw(self, screen, gradient_sharpness=2.0):
        """Draw all circles and trails."""
        # Get drawable elements from trail store
        trail_elements = self.trail_store.get_drawable_elements()
        
        # Draw all elements in order
        # print ('Elements: ', len(trail_elements))
        for element in trail_elements: # + circle_elements:
            texture = self._get_cached_gradient(
                element.size,
                element.color,
                element.alpha,
                gradient_sharpness  # Pass sharpness parameter
            )

            # Color(element.color[0]/255, element.color[1]/255,element.color[2]/255, element.alpha)  # Reset color to white for texture blending
            Ellipse(
                texture=texture,
                pos=(element.x - element.size/2,
                     element.y - element.size/2),
                size=(element.size, element.size),
                segments=12
            )
