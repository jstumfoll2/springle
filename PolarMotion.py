import math
import random

class PolarMotion:
    def __init__(self, radius=0, theta=0, radial_velocity=0, angular_velocity=0,
                 radial_acceleration=0,angular_acceleration=0):
        """
        Initialize polar motion with position and velocity components.
        
        Args:
            radius (float): Initial distance from origin
            theta (float): Initial angle in radians
            radial_velocity (float): Initial velocity along radius (outward positive)
            angular_velocity (float): Initial angular velocity (radians/sec, positive is counterclockwise)
        """
        self.radius = radius
        self.theta = theta
        self.radial_velocity = radial_velocity
        self.angular_velocity = angular_velocity
        self.radial_acceleration = radial_acceleration
        self.angular_acceleration = angular_acceleration
    
    def update(self, dt):
        """
        Update position based on velocities and additional motion parameters.
        
        Args:
            dt (float): Time step in seconds
        """
        # Update radius based on radial velocity and acceleration
        self.radial_velocity += (self.radial_acceleration) * dt * dt / 2.0
        self.radius += (self.radial_velocity) * dt
        
        # Update angle based on angular velocity and acceleration
        self.angular_velocity += (self.angular_acceleration) * dt * dt / 2.0
        self.theta += (self.angular_velocity) * dt
        
        # Normalize theta to stay within [0, 2π]
        self.theta = self.theta % (2 * math.pi)
    
    
    def to_cartesian(self, origin_x=0, origin_y=0):
        """
        Convert polar coordinates to Cartesian coordinates.
        
        Args:
            origin_x (float): x coordinate of the origin
            origin_y (float): y coordinate of the origin
            
        Returns:
            tuple: (x, y) coordinates
        """
        x = origin_x + self.radius * math.cos(self.theta)
        y = origin_y + self.radius * math.sin(self.theta)
        return (x, y)
    
    def decompose_velocity(self, velocity, center_pos, current_pos):
        """
        Decompose cartesian velocity (vx, vy) into polar velocity components (dr/dt, dθ/dt).
        
        Args:
            velocity (tuple): (vx, vy) velocity components in cartesian coordinates
            center_pos (tuple): (x, y) position of the origin/center
            current_pos (tuple): (x, y) current position
            
        Returns:
            tuple: (radial_velocity, angular_velocity)
                radial_velocity (dr/dt): positive means moving away from center
                angular_velocity (dθ/dt): positive means counterclockwise rotation
        """
        # Get relative position from center
        x = current_pos[0] - center_pos[0]
        y = -(current_pos[1] - center_pos[1])  # Flip y for mathematical coordinates
        
        # Get velocity components (flip vy to match mathematical coordinates)
        vx, vy = velocity[0], -velocity[1]
        
        # Calculate radius
        r = math.sqrt(x*x + y*y)
        if r == 0:
            return 0, 0
            
        # Radial velocity component (v_r)
        v_r = -(-x * vy + y * vx) / r
        
        # Tangential velocity component (v_theta)
        v_t = -(x * vx + y * vy) / r 
        
        # print("xy Postion: ", x, y)
        # print("Polar velocity: ", v_r, v_t)
        return  v_r, v_t
        
    def set_velocity_from_release(self, velocity, center_pos, current_pos):
        """
        Set velocities based on release velocity.
        
        Args:
            velocity (tuple): (vx, vy) velocity components
            center_pos (tuple): (x, y) position of center/origin
            current_pos (tuple): (x, y) current position
            
        Returns:
            tuple: (expansion_rate, rotation_speed)
        """
        # Get velocity components
        v_radial, v_tangential = self.decompose_velocity(velocity, center_pos, current_pos)
        
        # # Set the motion parameters
        # self.radial_velocity = v_radial
        # if self.radius > 0:
        #     self.angular_velocity = (v_tangential / self.radius)
        # else:
        #     self.angular_velocity = random.random() * 10
            
        # Set the motion parameters
        # Scale the velocities to make them more noticeable
        # These scaling factors can be adjusted based on your needs
        self.radial_velocity = v_radial * 1 # Increase radial effect
        self.angular_velocity = v_tangential * 0.01  # Increase angular effect
        
        # zero out the accelerations
        self.radial_acceleration = 0
        self.angular_acceleration = 0
        
    def update_acceleration(self, radial, angular):
        self.radial_acceleration=radial
        self.angular_acceleration=angular