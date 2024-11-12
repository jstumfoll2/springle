import random
import math

from lib.SpingleColors import SpingleColors
from lib.PolarMotion import PolarMotion

class OrbitGroup:
    """
    Manages a group of orbiting circles with improved stability and randomization.
    """
    
    # Configuration constants
    MIN_SIZE_VARIATION = 0.8
    MAX_SIZE_VARIATION = 1.2
    MIN_VELOCITY_VARIATION = 0.5
    MAX_VELOCITY_VARIATION = 10.0
    MIN_ACCELERATION_VARIATION = -1.0
    MAX_ACCELERATION_VARIATION = 1.0
    VISIBILITY_MARGIN = 1.1  # How far off screen before marking as inactive
    
    def __init__(self, trail_store, group_id, min_circles, max_circles, radius, base_size, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration,  
                 is_mouse_group=False):
        """
        Initialize orbit group with parameter validation.
        
        Args:
            trail_store: Centralized trail storage system
            group_id: Unique identifier for this group
            min_circles (int): Minimum number of circles
            max_circles (int): Maximum number of circles
            radius (float): Initial radius from center
            base_size (float): Base circle size
            radial_velocity (float): Initial radial velocity
            angular_velocity (float): Initial angular velocity
            radial_acceleration (float): Initial radial acceleration
            angular_acceleration (float): Initial angular acceleration
            is_mouse_group (bool): Whether this group is controlled by mouse
        """
        # Store TrailStore reference and group ID
        self.trail_store = trail_store
        self.group_id = group_id
        
        # Validate parameters
        self.validate_parameters(min_circles, max_circles, radius, base_size)
        
        # Set time_offset to 0 for mouse groups to prevent initial variations
        self.is_mouse_group = is_mouse_group
        self.time_offset = 0 if is_mouse_group else random.uniform(0, 10)
        
        self.radius = radius
        self.active = True
        self.size = 1
        self.x = 1
        self.y = 1
        
        # Initialize colors
        self.colors = SpingleColors()
        self.palette_index = random.randint(0, self.colors.numPatterns() - 1)
        self.color_transition = 0
        
        self.creation_time = 0
        self._last_trail_time = 0
        
        # Generate variations with improved distribution
        self.generate_variations()
        
        self.radial_acceleration = radial_acceleration
        self.angular_acceleration = angular_acceleration
        self.base_size = base_size
        self.should_check_visibility = True
        
        # Create circles
        num_circles = self.get_validated_circle_count(min_circles, max_circles)
        self.create_circles(num_circles, radius, base_size,
                          radial_velocity, angular_velocity,
                          radial_acceleration, angular_acceleration)

    def validate_parameters(self, min_circles, max_circles, radius, base_size):
        """Validate input parameters."""
        if min_circles < 1:
            min_circles = 1
        if max_circles < min_circles:
            max_circles = min_circles
        if radius < 0:
            radius = 1
        if base_size <= 0:
            base_size = 1

    def get_validated_circle_count(self, min_circles, max_circles):
        """Get validated number of circles with bounds checking."""
        min_circles = max(1, min_circles)
        max_circles = max(min_circles, max_circles)
        return random.randint(min_circles, max_circles)

    def generate_variations(self):
        """Generate motion variations using improved distribution."""
        # Use triangular distribution for more natural variation
        def triangular_variation(min_val, max_val):
            mode = (min_val + max_val) / 2
            return random.triangular(min_val, max_val, mode)
        
        self.vr_variation = triangular_variation(
            self.MIN_VELOCITY_VARIATION, 
            self.MAX_VELOCITY_VARIATION
        )
        
        self.vt_variation = triangular_variation(
            self.MIN_VELOCITY_VARIATION, 
            self.MAX_VELOCITY_VARIATION
        )
        
        direction = random.randint(-1,1)
        if direction == 0: 
            direction = 1
        self.vt_variation = self.vt_variation if self.is_mouse_group else self.vt_variation*direction
        
        self.ar_variation = triangular_variation(
            self.MIN_ACCELERATION_VARIATION, 
            self.MAX_ACCELERATION_VARIATION
        )
        self.at_variation = triangular_variation(
            self.MIN_ACCELERATION_VARIATION, 
            self.MAX_ACCELERATION_VARIATION
        )
        
        if self.is_mouse_group:
            self.vr_variation = 1
            self.vt_variation = 1
            # self.ar_variation = 1
            # self.at_variation = 1
            
        # Use beta distribution for size variation (tends toward middle values)
        self.size_variation = (random.betavariate(2, 2) * 
                                (self.MAX_SIZE_VARIATION - self.MIN_SIZE_VARIATION) + 
                                self.MIN_SIZE_VARIATION)

    def create_circles(self, num_circles, radius, base_size, 
                      radial_velocity=0, angular_velocity=0,
                      radial_acceleration=0, angular_acceleration=0):
        """Create circles with improved parameter handling and variation."""
        self.circles = []
        angle_step = 2 * math.pi / num_circles
        
        for i in range(num_circles):
            # Create motion with validated parameters
            motion = PolarMotion(
                radius=radius,
                theta=angle_step * i,
                radial_velocity=0 if self.is_mouse_group else 
                                radial_velocity * self.vr_variation,
                angular_velocity=0 if self.is_mouse_group else 
                                 angular_velocity * self.vt_variation,
                radial_acceleration=0 if self.is_mouse_group else 
                                    radial_acceleration * self.ar_variation,
                angular_acceleration=0 if self.is_mouse_group else 
                                     angular_acceleration * self.at_variation
            )
            
            # Simplified circle state (removed trail array)
            circle = {
                'motion': motion,
                'color_index': i % self.colors.COLORS_PER_PALETTE,
                'time_offset': 0 if self.is_mouse_group else self.time_offset,
                'size_variation': self.size_variation,
                'base_size': base_size,
                'active': True
            }
            self.circles.append(circle)
    
    def calculate_circle_size(self, circle):
        """Calculate current circle size with all factors applied."""
        radius = circle['motion'].radius
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        self.size = circle['base_size'] * circle['size_variation'] * size_factor
        return self.size
    
    def update_circle_size(self, new_size):
        """Update circle sizes with validation."""
        if new_size <= 0:
            return
        
        for circle in self.circles:
            circle['base_size'] = new_size
            
    def update_circle_acceleration(self, radial, angular):
        """Update accelerations with proper scaling."""
        for circle in self.circles:
            if not self.is_mouse_group:
                circle['motion'].radial_acceleration = radial * self.ar_variation
                circle['motion'].angular_acceleration = angular * self.at_variation
    
    def update_circle_positions(self, dt):
        """Update positions with time-based variations."""
        for circle in self.circles:
            # Update motion
            circle['motion'].update(dt)
            
            # Update time offset for variation calculations
            if not self.is_mouse_group:
                circle['time_offset'] += dt
    
    def handle_mouse_release(self, mouse_pos, velocity, screen_center):
        """Handle mouse release with improved velocity calculations."""
        if not mouse_pos or not velocity:
            return
            
        for circle in self.circles:
            circle['motion'].set_velocity_from_release(
                velocity,
                screen_center,
                mouse_pos
            )

    def is_circle_visible(self, screen_size):
        """Check visibility with improved boundary handling."""
        screen_diagonal = max(screen_size[0], screen_size[1])
        visible_radius = screen_diagonal * self.VISIBILITY_MARGIN
        
        if len(self.circles) == 0:
            return False
            
        return math.fabs(self.circles[0]['motion'].radius) <= visible_radius
    
    def get_circle_cartesian_pos(self, circle, screen_center):
        """Get circle position with validation."""
        if not circle or not screen_center:
            return (0, 0)
        
        self.x, self.y = circle['motion'].to_cartesian(
            origin_x=screen_center[0],
            origin_y=screen_center[1]
        )
        return self.x, self.y 
        
    def set_group_position(self, pos, screen_center):
        """Set position for all circles in the group."""
        if not pos or not screen_center:
            return
            
        # Calculate base position
        rel_x = pos[0] - screen_center[0]
        rel_y = pos[1] - screen_center[1]
        base_radius = math.sqrt(rel_x**2 + rel_y**2)
        base_angle = math.atan2(rel_y, rel_x)
        
        # Update circle positions
        angle_step = 2 * math.pi / len(self.circles)
        for i, circle in enumerate(self.circles):
            circle['motion'].radius = base_radius
            circle['motion'].theta = base_angle + (angle_step * i)
            # Reset motion parameters
            circle['motion'].radial_velocity = 0
            circle['motion'].angular_velocity = 0
            circle['motion'].radial_acceleration = 0
            circle['motion'].angular_acceleration = 0
            
    def group_update(self, dt, current_time, space_factor, screen_center):
        """Optimized circle updating."""
        # Pre-calculate common values
        screen_center = self.center
        should_add_trail = current_time - self._last_trail_time >= 0.01 * space_factor # Limit trail frequency
        
        # Batch update circles
        current_size = self.calculate_circle_size(self.circles[0])
        color = self.colors.getColor(
            self.palette_index,
            self.circles[0]['color_index'],
            self.color_transition
        )
        texture = None # self.get_texture()
        for circle in self.circles:
            # Update motion
            circle['motion'].update(dt)
            
            # Update time offset for non-mouse groups
            if not self.is_mouse_group:
                circle['time_offset'] += dt
            
            # Only add trail points periodically
            if self.is_circle_visible and should_add_trail:
                x, y = self.get_circle_cartesian_pos(circle, screen_center)
                
                self.trail_store.add_point(
                    x=x,
                    y=y,
                    color=color,
                    size=current_size,
                    group_id=self.group_id,
                    creation_time=current_time,
                    texture=texture
                )
            self._last_trail_time  = current_time