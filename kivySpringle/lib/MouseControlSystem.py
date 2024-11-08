import math
from typing import Tuple, List, Optional, Dict

class MouseControlSystem:
    """
    Handles mouse input tracking and velocity calculations in polar coordinates 
    with improved stability and error checking.
    """
    
    # Class-level constants for configuration
    MAX_RADIAL_VELOCITY = 1000.0     # Maximum radial velocity (pixels/sec)
    MAX_ANGULAR_VELOCITY = math.pi*2  # Maximum angular velocity (radians/sec)
    MIN_RADIUS = 1.0                 # Minimum radius to prevent div by 0
    MIN_POSITION_DELTA = 1.0         # Minimum movement to register (pixels)
    MAX_HISTORY_SIZE = 25            # Maximum number of history points
    MAX_HISTORY_DURATION = 0.1       # Maximum duration to keep history (seconds)
    VELOCITY_SMOOTHING = 0.85        # Smoothing factor for velocity (0-1)
    
    def __init__(self, velocity_samples: int = 25):
        """Initialize the mouse control system with polar coordinate tracking."""
        self.reset()
        self.velocity_samples = min(max(5, velocity_samples), self.MAX_HISTORY_SIZE)
        self.screen_center = (0, 0)  # Will be set later
        
    def set_screen_center(self, center: Tuple[float, float]):
        """Set the center point for polar coordinate calculations."""
        self.screen_center = center
    
    def reset(self):
        """Reset all tracking variables to initial state."""
        self.is_dragging = False
        self.start_pos_cart = None     # Cartesian coordinates
        self.start_pos_polar = None    # Polar coordinates (r, θ)
        self.current_pos_cart = None
        self.current_pos_polar = None
        self.last_pos_cart = None
        self.last_pos_polar = None
        self.velocity_cart = (0, 0)    # (vx, vy)
        self.velocity_polar = (0, 0)   # (vr, vθ)
        self.history_cart = []         # [(pos, time), ...]
        self.history_polar = []        # [(r, θ, time), ...]
        self.total_distance = 0
        self.last_velocity_polar = (0, 0)
    
    def cart_to_polar(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Convert cartesian to polar coordinates relative to screen center."""
        x = pos[0] - self.screen_center[0]
        y = self.screen_center[1] - pos[1]  # Flip y for mathematical coordinates
        
        radius = math.sqrt(x*x + y*y)
        theta = math.atan2(y, x)
        
        # Ensure radius is not too small to prevent instability
        radius = max(self.MIN_RADIUS, radius)
        
        # print('radius: ', radius, ', theta: ', theta)
        return (radius, theta)
    
    def polar_to_cart(self, polar: Tuple[float, float]) -> Tuple[float, float]:
        """Convert polar to cartesian coordinates."""
        r, theta = polar
        x = self.screen_center[0] + r * math.cos(theta)
        y = self.screen_center[1] - r * math.sin(theta)  # Flip y back for screen coordinates
        return (x, y)
    
    def validate_position(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Validate cartesian position format and values."""
        if not pos or not isinstance(pos, (tuple, list)) or len(pos) != 2:
            raise ValueError("Invalid position format")
        
        try:
            x, y = float(pos[0]), float(pos[1])
            return (x, y)
        except (TypeError, ValueError):
            raise ValueError("Position coordinates must be numeric")
    
    def start_drag(self, pos: Tuple[float, float]) -> bool:
        """Start a new drag operation with position validation."""
        try:
            pos_cart = self.validate_position(pos)
            pos_polar = self.cart_to_polar(pos_cart)
            
            self.is_dragging = True
            self.start_pos_cart = pos_cart
            self.start_pos_polar = pos_polar
            self.current_pos_cart = pos_cart
            self.current_pos_polar = pos_polar
            self.last_pos_cart = pos_cart
            self.last_pos_polar = pos_polar
            
            self.history_cart = [(pos_cart, 0.0)]
            self.history_polar = [(pos_polar[0], pos_polar[1], 0.0)]
            
            self.total_distance = 0
            self.velocity_cart = (0, 0)
            self.velocity_polar = (0, 0)
            self.last_velocity_polar = (0, 0)
            
            return True
            
        except ValueError as e:
            print(f"Error starting drag: {e}")
            self.reset()
            return False
    
    def update_drag(self, pos: Tuple[float, float], dt: float) -> bool:
        """Update drag state with new position and time delta."""
        if not self.is_dragging:
            return False
            
        try:
            new_pos_cart = self.validate_position(pos)
            new_pos_polar = self.cart_to_polar(new_pos_cart)
            
            # Calculate distances in both coordinate systems
            dx = new_pos_cart[0] - self.current_pos_cart[0]
            dy = new_pos_cart[1] - self.current_pos_cart[1]
            cart_distance = math.sqrt(dx * dx + dy * dy)
            
            # dr = new_pos_polar[0] - self.current_pos_polar[0]
            # dtheta = (new_pos_polar[1] - self.current_pos_polar[1] + math.pi) % (2*math.pi) - math.pi
            # polar_distance = math.sqrt(dr*dr + (new_pos_polar[0]*dtheta)**2)
            
            # Only update if movement is significant
            if cart_distance >= self.MIN_POSITION_DELTA:
                self.total_distance += cart_distance
                
                self.last_pos_cart = self.current_pos_cart
                self.last_pos_polar = self.current_pos_polar
                
                self.current_pos_cart = new_pos_cart
                self.current_pos_polar = new_pos_polar
                
                self.history_cart.append((new_pos_cart, dt))
                self.history_polar.append((new_pos_polar[0], new_pos_polar[1], dt))
                
                # Maintain history size and duration limits
                self._cleanup_history()
            
            return True
            
        except ValueError as e:
            print(f"Error updating drag: {e}")
            return False
    
    def _cleanup_history(self):
        """Clean up history based on size and duration limits."""
        # Remove excess entries if history is too long
        if len(self.history_cart) > self.MAX_HISTORY_SIZE:
            self.history_cart = self.history_cart[-self.MAX_HISTORY_SIZE:]
            self.history_polar = self.history_polar[-self.MAX_HISTORY_SIZE:]
        
        # Remove old entries based on duration
        total_time = 0
        for i in range(len(self.history_cart) - 1, -1, -1):
            total_time += self.history_cart[i][1]
            if total_time > self.MAX_HISTORY_DURATION:
                self.history_cart = self.history_cart[i:]
                self.history_polar = self.history_polar[i:]
                break
    
    def _calculate_velocities(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Calculate both cartesian and polar velocities with smoothing and capping."""
        if len(self.history_cart) < 2:
            return (0, 0), (0, 0)
        
        # Calculate velocities between consecutive points
        cart_velocities = []
        polar_velocities = []
        
        for i in range(len(self.history_cart) - 1):
            start_cart, start_time = self.history_cart[i]
            end_cart, end_time = self.history_cart[i + 1]
            
            start_polar = self.history_polar[i]
            end_polar = self.history_polar[i + 1]
            
            dt = end_time
            
            if dt > 0:
                # Cartesian velocities
                vx = (end_cart[0] - start_cart[0]) / dt
                vy = -(end_cart[1] - start_cart[1]) / dt
                cart_velocities.append((vx, vy))
                
                # Polar velocities
                dr = (end_polar[0] - start_polar[0]) / dt
                dtheta = ((end_polar[1] - start_polar[1] + math.pi) % (2*math.pi) - math.pi) / dt
                polar_velocities.append((dr, dtheta))
        
        if not cart_velocities:
            return (0, 0), (0, 0)
        
        # Calculate weighted average velocities
        samples = min(len(cart_velocities), self.velocity_samples)
        recent_cart = cart_velocities[-samples:]
        recent_polar = polar_velocities[-samples:]
        
        # Average cartesian velocities
        avg_vx = sum(v[0] for v in recent_cart) / len(recent_cart)
        avg_vy = sum(v[1] for v in recent_cart) / len(recent_cart)
        
        # Average polar velocities
        avg_vr = sum(v[0] for v in recent_polar) / len(recent_polar)
        avg_vtheta = sum(v[1] for v in recent_polar) / len(recent_polar)
        
        # Apply smoothing to polar velocities
        smooth_vr = (avg_vr * (1 - self.VELOCITY_SMOOTHING) + 
                    self.last_velocity_polar[0] * self.VELOCITY_SMOOTHING)
        smooth_vtheta = (avg_vtheta * (1 - self.VELOCITY_SMOOTHING) + 
                        self.last_velocity_polar[1] * self.VELOCITY_SMOOTHING)
        
        # Cap velocities
        smooth_vr = max(-self.MAX_RADIAL_VELOCITY, min(self.MAX_RADIAL_VELOCITY, smooth_vr))
        smooth_vtheta = max(-self.MAX_ANGULAR_VELOCITY, min(self.MAX_ANGULAR_VELOCITY, smooth_vtheta))
        
        return (avg_vx, avg_vy), (smooth_vr, smooth_vtheta)
    
    def end_drag(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """
        End drag operation and calculate final velocities.
        
        Returns:
            Tuple of (cartesian_velocity, polar_velocity)
            where cartesian_velocity is (vx, vy) and polar_velocity is (vr, vθ)
        """
        if not self.is_dragging:
            return (0, 0), (0, 0)
        
        # Calculate final velocities
        self.velocity_cart, self.velocity_polar = self._calculate_velocities()
        self.last_velocity_polar = self.velocity_polar
        
        # Reset drag state
        self.is_dragging = False
        self.start_pos_cart = None
        self.start_pos_polar = None
        self.current_pos_cart = None
        self.current_pos_polar = None
        
        # Keep velocities for return but clear history
        final_velocities = (self.velocity_cart, self.velocity_polar)
        self.history_cart = []
        self.history_polar = []
        
        
        # print('xy vel: ', self.velocity_cart, ', Polar vel (vr, vθ): ', self.velocity_polar)
        return final_velocities
    
    def get_drag_info(self) -> Dict:
        """Get current drag information for debugging."""
        return {
            'is_dragging': self.is_dragging,
            'start_pos_cart': self.start_pos_cart,
            'start_pos_polar': self.start_pos_polar,
            'current_pos_cart': self.current_pos_cart,
            'current_pos_polar': self.current_pos_polar,
            'velocity_cart': self.velocity_cart,
            'velocity_polar': self.velocity_polar,
            'history_size': len(self.history_cart),
            'total_distance': self.total_distance,
        }
    
    def get_smoothed_path(self, samples: int = 10) -> List[Tuple[float, float]]:
        """Get smoothed path points for visualization."""
        if len(self.history_cart) < 2:
            return []
        
        # Return evenly spaced points from history
        step = max(1, len(self.history_cart) // samples)
        return [pos for pos, _ in self.history_cart[::step]]