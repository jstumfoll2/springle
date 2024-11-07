import pygame
import math

# Local imports
from OrbitGroup import OrbitGroup
from SpingleColors import SpingleColors
from MouseControlSystem import MouseControlSystem
from springle_params import SpringleParams

MAX_GROUPS = 7
class SpringleCircle:
    def __init__(self, min_circles, max_circles, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration,  
                 base_size, WIDTH, HEIGHT):
        
        # Initialize with default parameters
        self.params = SpringleParams.from_defaults()
        
        self.groups = [OrbitGroup(min_circles, max_circles, 0, base_size,
                                  radial_velocity, angular_velocity,
                                  radial_acceleration, angular_acceleration, False)]
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

        # Initialize gradient cache
        self.gradient_cache = {}
        self.max_cached_size = 100  # Maximum circle size to cache
        self.size_step = 2         # Round sizes to nearest multiple of 2
        self.alpha_step = 16       # Round alpha to nearest multiple of 16
        
        # Pre-generate common gradients
        self._init_gradient_cache()
        
    def _init_gradient_cache(self):
        """Pre-generate commonly used gradient surfaces."""
        base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),  # Primary colors
                      (255, 255, 0), (0, 255, 255), (255, 0, 255)]  # Secondary colors
        
        # Cache gradients for common sizes and colors
        for size in range(4, self.max_cached_size + 1, self.size_step):
            for color in base_colors:
                for alpha in range(64, 256, self.alpha_step):
                    self._get_cached_gradient(size, color, alpha)

    def _get_cache_key(self, size, color, alpha):
        """Generate a cache key for a given size, color, and alpha."""
        # Round size and alpha to reduce cache variations
        rounded_size = round(size / self.size_step) * self.size_step
        rounded_alpha = round(alpha / self.alpha_step) * self.alpha_step
        return (rounded_size, color, rounded_alpha)

    def _get_cached_gradient(self, size, color, alpha):
        """Get or create a cached gradient surface."""
        cache_key = self._get_cache_key(size, color, alpha)
        
        if cache_key not in self.gradient_cache:
            # Create new gradient surface if not in cache
            surface = self._create_gradient_circle(size, color, alpha)
            
            # Only cache if size is within reasonable limits
            if size <= self.max_cached_size:
                self.gradient_cache[cache_key] = surface
            return surface
        
        return self.gradient_cache[cache_key]

    def _create_gradient_circle(self, size, color, alpha):
        """Create a circle with a radial gradient effect."""
        surface = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        center = (size, size)
        
        # Optimize number of steps based on size
        num_steps = 15 # min(15, max(5, int(size / 4)))
        
        # Draw base gradient circles
        for i in range(num_steps):
            current_radius = size * (1 - (i / num_steps))
            gradient_factor = i / num_steps
            gradient_color = (
                int(color[0] * (1 - gradient_factor * 0.5)),
                int(color[1] * (1 - gradient_factor * 0.5)),
                int(color[2] * (1 - gradient_factor * 0.5)),
                int(alpha * (1 - gradient_factor * 0.3))
            )
            pygame.draw.circle(surface, gradient_color, center, current_radius)
        
        return surface
    
    def create_gradient_circle(self, size, color, alpha):
        """Create a circle with a radial gradient effect."""
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        center = (size, size)
        
        # Calculate gradient steps
        num_steps = 15
        for i in range(num_steps):
            current_radius = size * (1 - (i / num_steps))
            
            # Calculate gradient color
            gradient_factor = i / num_steps
            gradient_color = (
                int(color[0] * (1 - gradient_factor * 0.5)),  # Reduce RGB values for depth
                int(color[1] * (1 - gradient_factor * 0.5)),
                int(color[2] * (1 - gradient_factor * 0.5)),
                int(alpha * (1 - gradient_factor * 0.3))      # Slightly reduce alpha for depth
            )
            
            pygame.draw.circle(surface, gradient_color, center, current_radius)
        
        return surface
    
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
        
    def update(self, dt: float, params: SpringleParams) -> None:
        """Update all groups and handle mouse interaction."""
        # Update fade duration from parameters
        self.fade_duration = params.fade_duration
        need_new_group = False
        
        # Handle mouse input
        if params.mouse_button_pressed and params.mouse_pos:
            if not self.mouse_control.is_dragging:
                # Start new drag
                self.mouse_control.start_drag(params.mouse_pos)
                
                # Create new group at click position
                new_group = OrbitGroup(
                    params.min_circles, params.max_circles, 0, params.base_size, 
                    0, 0, 0, 0, True
                )
                new_group.set_group_position(params.mouse_pos, self.center)
                self.groups.append(new_group)
            else:
                # Update existing drag
                self.mouse_control.update_drag(params.mouse_pos, dt)
                
                # Update most recent group's position
                if self.groups:
                    latest_group = self.groups[-1]
                    latest_group.set_group_position(params.mouse_pos, self.center)
        
        elif self.mouse_control.is_dragging:
            # Handle mouse release
            velocity = self.mouse_control.end_drag()
            if self.groups:
                latest_group = self.groups[-1]
                latest_group.handle_mouse_release(params.mouse_pos, velocity, self.center)

        # Update spawn cooldown
        if self.spawn_cooldown_current > 0:
            self.spawn_cooldown_current -= dt
        
        active_groups = 0
        for group in self.groups:
            if not group.active:
                continue

            active_groups += 1
                
            # Update parameters from current settings
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
                                           current_size, params.space_factor):
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
        
        # Check if we should create a new group
        if self.spawn_cooldown_current <= 0 and params.auto_generate:
            need_new_group = True
            self.spawn_cooldown_current = self.spawn_cooldown_start
                
        # Spawn new group if needed
        if need_new_group and active_groups < MAX_GROUPS:
            new_group = OrbitGroup(
                    params.min_circles, params.max_circles, 0, params.base_size, 
                    params.radial_velocity, params.angular_velocity,
                    params.radial_acceleration, params.angular_acceleration, False
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
                        if alpha > 10:
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
        # drawable_elements.sort(key=lambda x: x.get('age', -1), reverse=True)
        
        # Draw all elements with gradient effect
        for element in drawable_elements:
            gradient_surface = self._get_cached_gradient(
            # gradient_surface = self.create_gradient_circle(
                element['size'], 
                element['color'], 
                element['alpha']
            )
            screen.blit(gradient_surface, (
                element['x'] - element['size'],
                element['y'] - element['size']
            ))