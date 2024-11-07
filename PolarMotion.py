import math
import random

class PolarMotion:
    """
    Handles motion in polar coordinates with proper bounds and limits.
    Includes safety checks and normalization for physical parameters.
    """
    
    # Class-level constants for limits
    MIN_RADIUS = -2000
    MAX_RADIUS = 2000  # Adjust based on screen size
    
    # Velocity limits (in units per second)
    MAX_RADIAL_VELOCITY = 1000
    MIN_RADIAL_VELOCITY = -1000
    MAX_ANGULAR_VELOCITY = math.pi * 4  # 2 full rotations per second
    MIN_ANGULAR_VELOCITY = -math.pi * 4
    
    # Acceleration limits (in units per second squared)
    MAX_RADIAL_ACCELERATION = 2000
    MIN_RADIAL_ACCELERATION = -2000
    MAX_ANGULAR_ACCELERATION = math.pi * 8  # 4 rotations/sec²
    MIN_ANGULAR_ACCELERATION = -math.pi * 8

    def __init__(self, radius=0, theta=0, radial_velocity=0, angular_velocity=0,
                 radial_acceleration=0, angular_acceleration=0):
        """
        Initialize polar motion with bounds checking.
        
        Args:
            radius (float): Initial distance from origin
            theta (float): Initial angle in radians
            radial_velocity (float): Initial velocity along radius
            angular_velocity (float): Initial angular velocity (radians/sec)
            radial_acceleration (float): Radial acceleration (units/sec²)
            angular_acceleration (float): Angular acceleration (radians/sec²)
        """
        # Initialize with bounds checking
        self._radius = self._clamp_radius(radius)
        self._theta = self._normalize_angle(theta)
        
        # Initialize velocities with limits
        self._radial_velocity = self._clamp_radial_velocity(radial_velocity)
        self._angular_velocity = self._clamp_angular_velocity(angular_velocity)
        
        # Initialize accelerations with limits
        self._radial_acceleration = self._clamp_radial_acceleration(radial_acceleration)
        self._angular_acceleration = self._clamp_angular_acceleration(angular_acceleration)
        
        # Track total time for potential debug/analysis
        self._total_time = 0.0
    
    # Property getters and setters with bounds checking
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        self._radius = self._clamp_radius(value)
    
    @property
    def theta(self):
        return self._theta
    
    @theta.setter
    def theta(self, value):
        self._theta = self._normalize_angle(value)
        
    @property
    def radial_velocity(self):
        return self._radial_velocity
    
    @radial_velocity.setter
    def radial_velocity(self, value):
        self._radial_velocity = self._clamp_radial_velocity(value)
        
    @property
    def angular_velocity(self):
        return self._angular_velocity
    
    @angular_velocity.setter
    def angular_velocity(self, value):
        self._angular_velocity = self._clamp_angular_velocity(value)
        
    @property
    def radial_acceleration(self):
        return self._radial_acceleration
    
    @radial_acceleration.setter
    def radial_acceleration(self, value):
        self._radial_acceleration = self._clamp_radial_acceleration(value)
        
    @property
    def angular_acceleration(self):
        return self._angular_acceleration
    
    @angular_acceleration.setter
    def angular_acceleration(self, value):
        self._angular_acceleration = self._clamp_angular_acceleration(value)
    
    # Clamping and normalization methods
    def _clamp_radius(self, value):
        """Ensure radius stays within valid bounds."""
        return max(self.MIN_RADIUS, min(self.MAX_RADIUS, value))
    
    def _normalize_angle(self, angle):
        """Normalize angle to [0, 2π] range."""
        return angle % (2 * math.pi)
    
    def _clamp_radial_velocity(self, value):
        """Limit radial velocity to prevent excessive speeds."""
        if -1 < value < 1:
            return 1
        else:
            return max(self.MIN_RADIAL_VELOCITY, min(self.MAX_RADIAL_VELOCITY, value))
    
    def _clamp_angular_velocity(self, value):
        """Limit angular velocity to prevent excessive rotation."""
        if -0.05 < value < 0.05:
            return 0.05
        else:
            return max(self.MIN_ANGULAR_VELOCITY, min(self.MAX_ANGULAR_VELOCITY, value))
    
    def _clamp_radial_acceleration(self, value):
        """Limit radial acceleration to prevent unstable motion."""
        return max(self.MIN_RADIAL_ACCELERATION, min(self.MAX_RADIAL_ACCELERATION, value))
    
    def _clamp_angular_acceleration(self, value):
        """Limit angular acceleration to prevent unstable rotation."""
        return max(self.MIN_ANGULAR_ACCELERATION, min(self.MAX_ANGULAR_ACCELERATION, value))
    
    def update(self, dt):
        """
        Update position based on velocities and accelerations.
        Uses improved numerical integration and ensures stable motion.
        
        Args:
            dt (float): Time step in seconds
        """
        self._total_time += dt
        
        # Update velocities using acceleration (with mid-point integration)
        mid_radial_velocity = self._radial_velocity + self._radial_acceleration * dt / 2
        mid_angular_velocity = self._angular_velocity + self._angular_acceleration * dt / 2
        
        # Clamp mid-point velocities
        mid_radial_velocity = self._clamp_radial_velocity(mid_radial_velocity)
        mid_angular_velocity = self._clamp_angular_velocity(mid_angular_velocity)
        
        # Update final velocities
        self._radial_velocity = self._clamp_radial_velocity(
            self._radial_velocity + self._radial_acceleration * dt
        )
        self._angular_velocity = self._clamp_angular_velocity(
            self._angular_velocity + self._angular_acceleration * dt
        )
        
        # Update position using mid-point velocities for better accuracy
        self._radius = self._clamp_radius(
            self._radius + mid_radial_velocity * dt
        )
        self._theta = self._normalize_angle(
            self._theta + mid_angular_velocity * dt
        )
    
    def to_cartesian(self, origin_x=0, origin_y=0):
        """
        Convert polar coordinates to Cartesian coordinates.
        
        Args:
            origin_x (float): x coordinate of the origin
            origin_y (float): y coordinate of the origin
            
        Returns:
            tuple: (x, y) coordinates
        """
        x = origin_x + self._radius * math.cos(self._theta)
        y = origin_y + self._radius * math.sin(self._theta)
        return (x, y)
    
    def set_velocity_from_release(self, velocity_data, center_pos, current_pos):
        """
        Set velocities based on release velocity with improved stability.
        
        Args:
            velocity_data: Either (vx, vy) or ((vx, vy), (vr, vtheta))
            center_pos: (x, y) position of center/origin
            current_pos: (x, y) current position
        """
        # Handle both old and new velocity formats
        if isinstance(velocity_data, tuple) and len(velocity_data) == 2:
            if isinstance(velocity_data[0], (tuple, list)):
                # New format: ((vx, vy), (vr, vtheta))
                cart_velocity, polar_velocity = velocity_data
                v_radial, v_angular = polar_velocity
                
                # correct sign and apply scale for better feel
                v_radial = v_radial * 2.0
                v_angular = v_angular * -2.0
            else:
                # Old format: (vx, vy)
                cart_velocity = velocity_data
                v_radial, v_angular = self.decompose_velocity(cart_velocity, center_pos, current_pos)
        else:
            print(f"Warning: Unexpected velocity format: {velocity_data}")
            return

        # Scale and clamp velocities for better behavior
        self._radial_velocity = self._clamp_radial_velocity(v_radial * 1)
        
        # Calculate angular velocity based on current radius to prevent instability
        if self._radius > 0:
            angular = self._clamp_angular_velocity(v_angular * 1)
        else:
            # If at center, use a safe random value
            angular = random.uniform(-math.pi/2, math.pi/2)
        
        self._angular_velocity = angular
        
        # Reset accelerations on release
        self._radial_acceleration = 0
        self._angular_acceleration = 0

    def decompose_velocity(self, velocity, center_pos, current_pos):
        """
        Decompose cartesian velocity into polar components with improved accuracy.
        
        Args:
            velocity: (vx, vy) velocity components
            center_pos: (x, y) position of origin/center
            current_pos: (x, y) current position
            
        Returns:
            tuple: (radial_velocity, angular_velocity)
        """
        try:
            # Get relative position from center
            x = current_pos[0] - center_pos[0]
            y = -(current_pos[1] - center_pos[1])  # Flip y for mathematical coordinates
            
            # Get velocity components (flip vy to match mathematical coordinates)
            vx, vy = velocity[0], -velocity[1]
            
            # Calculate radius with safety check
            r = math.sqrt(x*x + y*y)
            if r < 0.1:  # Prevent division by zero with small threshold
                return 0, 0
                
            # Calculate velocity components with improved accuracy
            v_r = -(-x * vy + y * vx) / r  # Radial velocity
            v_t = -(x * vx + y * vy) / r   # Tangential velocity
            
            return self._clamp_radial_velocity(v_r), v_t
            
        except (TypeError, AttributeError) as e:
            print(f"Error decomposing velocity: {e}")
            return 0, 0