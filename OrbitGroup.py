import random
import math
from SpingleColors import SpingleColors
from PolarMotion import PolarMotion

class OrbitGroup:
    def __init__(self, min_circles, max_circles, radius, base_size, 
                 radial_velocity, angular_velocity,
                 radial_acceleration, angular_acceleration,  
                 is_mouse_group=False):
        
        # Set time_offset to 0 for mouse groups to prevent initial variations
        self.is_mouse_group = is_mouse_group
        self.time_offset = 0 if is_mouse_group else random.random() * 10
        
        self.radius = radius
        
        self.colors = SpingleColors()  # Create instance of SpingleColors
        self.palette_index = random.randint(0, self.colors.numPatterns() - 1)
        self.color_transition = 0
        self.active = True  # New flag to track if group is still moving
                
        num_circles = random.randint(min_circles, max_circles)
        
        self.vr_variation = random.random()*2-1
        self.vt_variation = random.random()*2-1
        self.ar_variation = random.random()*2-1
        self.at_variation = random.random()*2-1
        self.size_variation = random.random()*1+0.5
        if self.size_variation == 0:
            self.size_variation = 1
        
        self.create_circles(num_circles, radius, base_size,
                            radial_velocity, angular_velocity,
                            radial_acceleration, angular_acceleration)

    def create_circles(self, num_circles, radius, base_size, 
                       radial_velocity=0, angular_velocity=0,
                       radial_acceleration=0,angular_acceleration=0):
        """Create circles with PolarMotion for position and velocity tracking."""
        self.circles = []
        angle_step = 2 * math.pi / num_circles
        
        for i in range(num_circles):
            # Create circle with polar motion
            motion = PolarMotion(
                radius=radius,
                theta=angle_step * i,
                radial_velocity=0 if self.is_mouse_group else radial_velocity*(self.vr_variation),
                angular_velocity=0 if self.is_mouse_group else angular_velocity*(self.vt_variation),
                radial_acceleration=0 if self.is_mouse_group else radial_acceleration*(self.ar_variation),
                angular_acceleration=0 if self.is_mouse_group else angular_acceleration*(self.at_variation)
            )
            
            circle = {
                'motion': motion,
                'color_index': 0,
                'trail': [],
                'time_offset': 0 if self.is_mouse_group else self.time_offset,
                'last_trail_pos': None,
                'size_variation': self.size_variation,
                'base_size': base_size
            }
            self.circles.append(circle)
    
    def update_circle_size(self, new_size):
        for circle in self.circles:
            # Update motion
            circle['base_size'] = new_size
            
    def update_circle_acceleration(self, radial, angular):
        for circle in self.circles:
            # Update motion
            circle['motion'].radial_acceleration = radial
            circle['motion'].angular_acceleration = angular
    
    def update_circle_positions(self, dt):
        """Update positions of all circles in the group."""
        for circle in self.circles:
            # Update motion
            circle['motion'].update(dt)
            
            # Update time offset for variation calculations
            if not self.is_mouse_group:
                circle['time_offset'] += dt
    
    def handle_mouse_release(self, mouse_pos, velocity, screen_center):
        """Handle mouse release event for the group."""
        # Set the proper angular velocity for each circle
        for circle in self.circles:
            circle['motion'].set_velocity_from_release(
                velocity,
                screen_center,
                mouse_pos
            )

    def is_circle_visible(self, screen_size):
        """Check if any circle in group is visible on screen."""
        screen_diagonal = math.sqrt(screen_size[0]**2 + screen_size[1]**2)
        visible_radius = screen_diagonal / 1.3
        
        for circle in self.circles:
            if circle['motion'].radius <= visible_radius:
                return True
        return False
    
    def get_circle_cartesian_pos(self, circle, screen_center):
        """Get circle position in cartesian coordinates."""
        return circle['motion'].to_cartesian(
            origin_x=screen_center[0],
            origin_y=screen_center[1]
        )
        
    def set_group_position(self, pos, screen_center):
        """Set position of entire group based on mouse position."""
        # Calculate relative position from center
        rel_x = pos[0] - screen_center[0]
        rel_y = pos[1] - screen_center[1]
        
        # Calculate base radius and angle
        base_radius = math.sqrt(rel_x**2 + rel_y**2)
        base_angle = math.atan2(rel_y, rel_x)
        
        # Update each circle's position
        angle_step = 2 * math.pi / len(self.circles)
        for i, circle in enumerate(self.circles):
            circle['motion'].radius = base_radius
            circle['motion'].theta = base_angle + (angle_step * i)
            # Reset velocities when setting new position
            circle['motion'].radial_velocity = 0
            circle['motion'].angular_velocity = 0
            # Reset acccelerations when setting new position
            circle['motion'].radial_accceleration = 0
            circle['motion'].angular_accceleration = 0
            