import pygame
import math
from functools import lru_cache

# Local imports
from lib.OrbitGroup import OrbitGroup
from lib.SpingleColors import SpingleColors
from lib.MouseControlSystem import MouseControlSystem
from lib.SpringleParams import SpringleParams


class GradientCache:
    """Optimized cache system for gradient surfaces"""
    def __init__(self, size_step=2, alpha_step=16):
        self.size_step = size_step
        self.alpha_step = alpha_step
        self._cache = {}
        
    @staticmethod
    @lru_cache(maxsize=1024)
    def _make_cache_key(size: int, r: int, g: int, b: int, alpha: int) -> tuple:
        """Create a cache key using the lru_cache decorator for memoization"""
        return (size, r, g, b, alpha)
    
    def get_key(self, size: float, color: tuple, alpha: int) -> tuple:
        """Get cache key with minimal computation and object creation"""
        # Round size and alpha to reduce cache variations
        size_rounded = round(size / self.size_step) * self.size_step
        alpha_rounded = round(alpha / self.alpha_step) * self.alpha_step
        
        # Unpack color tuple directly into key creation
        return self._make_cache_key(size_rounded, color[0], color[1], color[2], alpha_rounded)
    
    def get(self, key: tuple) -> pygame.Surface:
        """Get item from cache"""
        return self._cache.get(key)
    
    def set(self, key: tuple, surface: pygame.Surface) -> None:
        """Set item in cache"""
        self._cache[key] = surface
    
    def __len__(self) -> int:
        return len(self._cache)
    
class SpringleCircle:
    def __init__(self, min_circles, max_circles, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration,  
                 base_size, WIDTH, HEIGHT):
        
        # Add simulation time tracking
        self.simulation_time = 0.0
        
        # Initialize with default parameters
        self.params = SpringleParams.from_defaults()
        
        self.groups = [OrbitGroup(min_circles, max_circles, 0, base_size,
                                  radial_velocity, angular_velocity,
                                  radial_acceleration, angular_acceleration, False)]
        # Store creation time with the initial group
        self.groups[0].creation_time = 0.0
        self.max_groups = 7  # Change from constant to instance variable
        
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.center = (WIDTH // 2, HEIGHT // 2)
        self.screen_diagonal = math.sqrt(WIDTH**2 + HEIGHT**2)
        
        self.color_transition_speed = 0.2
        self.spawn_cooldown_start = 4.0  # Starting value for cooldown timer
        self.spawn_cooldown_current = self.spawn_cooldown_start  # Initialize with full cooldown to prevent immediate spawn
        self.fade_duration = 10.0  # Time in seconds for trails to fully fade

        self.colors = SpingleColors()  # Create instance of SpingleColors
        self.mouse_control = MouseControlSystem()
        self.mouse_control.set_screen_center(self.center)
        
        # New: Separate list for fading trails
        self.fading_trails = []

        # Initialize gradient cache
        self.gradient_cache = GradientCache(size_step=2, alpha_step=16)
        self.max_cached_size = 100
        
        # Initialize gradient cache
        # self.gradient_cache = {}
        # self.max_cached_size = 100  # Maximum circle size to cache
        # self.size_step = 2         # Round sizes to nearest multiple of 2
        # self.alpha_step = 16       # Round alpha to nearest multiple of 16

        # # Pre-generate common gradients
        # self._init_gradient_cache()

        
        
    def _get_cached_gradient(self, size, color, alpha):
        """Get or create a cached gradient surface with optimized caching."""
        # Get cache key with minimal overhead
        cache_key = self.gradient_cache.get_key(size, color, alpha)
        
        # Fast cache lookup
        surface = self.gradient_cache.get(cache_key)
        if surface is not None:
            return surface
            
        # Create new gradient surface if not in cache
        surface = self._create_gradient_circle(size, color, alpha)
        
        # Only cache if size is within reasonable limits
        if size <= self.max_cached_size:
            self.gradient_cache.set(cache_key, surface)
            
        return surface

    def _create_gradient_circle(self, size, color, alpha):
        """Create a circle with a radial gradient effect - optimized version."""
        # Round size to int once at the start
        int_size = int(size)
        surface_size = int_size * 2
        
        # Create surface with exact size needed
        surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
        center = (int_size, int_size)
        
        # Pre-calculate gradient steps
        num_steps = 15
        r, g, b = color
        
        # Pre-calculate all colors and radii
        steps = []
        for i in range(num_steps):
            factor = i / num_steps
            radius = int_size * (1 - factor)
            gradient_color = (
                int(r * (1 - factor * 0.5)),
                int(g * (1 - factor * 0.5)),
                int(b * (1 - factor * 0.5)),
                int(alpha * (1 - factor * 0.3))
            )
            steps.append((radius, gradient_color))
        
        # Draw circles in a single pass
        for radius, gradient_color in steps:
            pygame.draw.circle(surface, gradient_color, center, radius)
        
        return surface
    
    
    # def _init_gradient_cache(self):
    #     """Pre-generate commonly used gradient surfaces."""
    #     base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),  # Primary colors
    #                   (255, 255, 0), (0, 255, 255), (255, 0, 255)]  # Secondary colors

    #     # Cache gradients for common sizes and colors
    #     for size in range(4, self.max_cached_size + 1, self.size_step):
    #         for color in base_colors:
    #             for alpha in range(64, 256, self.alpha_step):
    #                 self._get_cached_gradient(size, color, alpha)

    # def _get_cache_key(self, size, color, alpha):
    #     """Generate a cache key for a given size, color, and alpha."""
    #     # Round size and alpha to reduce cache variations
    #     rounded_size = round(size / self.size_step) * self.size_step
    #     rounded_alpha = round(alpha / self.alpha_step) * self.alpha_step
    #     return (rounded_size, color, rounded_alpha)

    # def _get_cached_gradient(self, size, color, alpha):
    #     """Get or create a cached gradient surface."""
    #     cache_key = self._get_cache_key(size, color, alpha)

    #     if cache_key not in self.gradient_cache:
    #         # Create new gradient surface if not in cache
    #         surface = self._create_gradient_circle(size, color, alpha)

    #         # Only cache if size is within reasonable limits
    #         if size <= self.max_cached_size:
    #             self.gradient_cache[cache_key] = surface
    #         return surface

    #     return self.gradient_cache[cache_key]

    # def _create_gradient_circle(self, size, color, alpha):
    #     """Create a circle with a radial gradient effect."""
    #     surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
    #     center = (size, size)

    #     # Optimize number of steps based on size
    #     num_steps = 15 # min(15, max(5, int(size / 4)))

    #     # Draw base gradient circles
    #     for i in range(num_steps):
    #         current_radius = size * (1 - (i / num_steps))
    #         gradient_factor = i / num_steps
    #         gradient_color = (
    #             int(color[0] * (1 - gradient_factor * 0.5)),
    #             int(color[1] * (1 - gradient_factor * 0.5)),
    #             int(color[2] * (1 - gradient_factor * 0.5)),
    #             int(alpha * (1 - gradient_factor * 0.3))
    #         )
    #         pygame.draw.circle(surface, gradient_color, center, current_radius)

    #     return surface

    # def create_gradient_circle(self, size, color, alpha):
    #     """Create a circle with a radial gradient effect."""
    #     surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    #     center = (size, size)

    #     # Calculate gradient steps
    #     num_steps = 15
    #     for i in range(num_steps):
    #         current_radius = size * (1 - (i / num_steps))

    #         # Calculate gradient color
    #         gradient_factor = i / num_steps
    #         gradient_color = (
    #             int(color[0] * (1 - gradient_factor * 0.5)),  # Reduce RGB values for depth
    #             int(color[1] * (1 - gradient_factor * 0.5)),
    #             int(color[2] * (1 - gradient_factor * 0.5)),
    #             int(alpha * (1 - gradient_factor * 0.3))      # Slightly reduce alpha for depth
    #         )

    #         pygame.draw.circle(surface, gradient_color, center, current_radius)

    #     return surface
    
    def should_add_trail_point(self, new_pos, last_pos, circle_size, space_factor, dt=0):
        """Determine if a new trail point should be added based on distance."""
        if last_pos is None:
            return True
        dx = new_pos[0] - last_pos[0]
        dy = new_pos[1] - last_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return (distance >= circle_size * space_factor)

    def set_max_groups(self, value):
        """Set the maximum number of allowed groups."""
        self.max_groups = value
        # Remove excess groups if current count exceeds new maximum
        active_groups = [g for g in self.groups if g.active]
        while len(active_groups) > self.max_groups:
            oldest_group = min(active_groups, key=lambda g: g.creation_time)
            self.groups.remove(oldest_group)
            active_groups.remove(oldest_group)
            
    def calculate_circle_size(self, radius, base_size, size_variation):
        """Calculate circle size based on radius from center."""
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        return base_size * size_variation * size_factor
        
    def update(self, dt: float, params: SpringleParams) -> None:
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
                new_group.creation_time = self.simulation_time  # Store creation time
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
                group_trails = []
                for circle in group.circles:
                    if circle['trail']:
                        # Store circle index with trail points to maintain identity
                        group_trails.extend([
                            (circle_idx, x, y, color, size, age)
                            for circle_idx, (x, y, color, size, age, _) 
                            in enumerate(circle['trail'])
                        ])
                        circle['trail'] = []
                
                if group_trails:  # Only add if there are trails
                    self.fading_trails.append({
                        'creation_time': group.creation_time,
                        'palette_index': group.palette_index,
                        'color_transition': group.color_transition,
                        'trails': group_trails
                    })
        
        # Update fading trails with group context
        updated_fading_trails = []
        for group_data in self.fading_trails:
            updated_trails = []
            for circle_idx, x, y, color, size, age in group_data['trails']:
                new_age = age + dt
                if new_age < self.fade_duration:
                    updated_trails.append((circle_idx, x, y, color, size, new_age))
            
            if updated_trails:  # Only keep groups with remaining trails
                group_data['trails'] = updated_trails
                updated_fading_trails.append(group_data)
                
        self.fading_trails = updated_fading_trails
        
        # Rest of update logic (spawn cooldown, new groups, etc.)
        if self.spawn_cooldown_current >= 0:
            self.spawn_cooldown_current -= dt
            
        if self.spawn_cooldown_current <= 0 and params.auto_generate:
            need_new_group = True
            self.spawn_cooldown_current = self.spawn_cooldown_start
                
        # Update max_groups when checking for new group creation
        if need_new_group and active_groups < self.max_groups:  # Use instance variable instead of constant
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
                # Include creation time with trail point
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

    def draw(self, screen, max_alpha):
        """Draw all groups and their trails with proper creation time ordering."""
        # Dictionary to collect all drawable elements, keyed by creation time
        group_elements = {}
        
        # Add fading group trails
        for group_data in self.fading_trails:
            creation_time = group_data['creation_time']
            
            if creation_time not in group_elements:
                group_elements[creation_time] = []
                
            # Add all trails for this fading group
            for circle_idx, x, y, color, size, age in group_data['trails']:
                fade_progress = age / self.fade_duration
                eased_fade = 1 - (fade_progress * fade_progress * fade_progress)
                alpha = int(max(0, max_alpha * eased_fade))
                
                if alpha > 0:
                    group_elements[creation_time].append({
                        'type': 'trail',
                        'x': x,
                        'y': y,
                        'color': color,
                        'size': size,
                        'alpha': alpha,
                        'circle_idx': circle_idx  # Keep circle index for potential use
                    })
        
        # Add active groups' elements
        for group in self.groups:
            if not group.active:
                continue
                
            if group.creation_time not in group_elements:
                group_elements[group.creation_time] = []
            
            # Add trails for active circles
            for circle_idx, circle in enumerate(group.circles):
                # Add trails
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
                            'alpha': alpha,
                            'circle_idx': circle_idx
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
                        'alpha': 255,
                        'circle_idx': circle_idx
                    })
        
        # Draw all elements in order of creation time
        for creation_time in sorted(group_elements.keys()):
            for element in group_elements[creation_time]:
                gradient_surface = self._get_cached_gradient(
                    element['size'],
                    element['color'],
                    element['alpha']
                )
                screen.blit(gradient_surface, (
                    element['x'] - element['size'],
                    element['y'] - element['size']
                ))