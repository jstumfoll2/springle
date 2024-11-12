from dataclasses import dataclass

@dataclass
class SpringleParams:
    """Parameters for SpringleCircle update with complete parameter set."""
    # Group creation parameters
    min_circles: int
    max_circles: int
    max_groups: int
    
    # Motion parameters
    radial_velocity: float
    angular_velocity: float
    radial_acceleration: float
    angular_acceleration: float
    
    # Visual parameters
    base_size: float
    fade_duration: float
    space_factor: float
    max_alpha: int
    color_transition_speed: float
    
    # System parameters
    spawn_cooldown: float
    auto_generate: bool = True
    gradient_sharpness: float = 5.0
    
    # Input state
    mouse_button_pressed: bool = False
    mouse_pos: tuple = (0, 0)

    @classmethod
    def from_defaults(cls):
        """Create instance with carefully tuned default values."""
        return cls(
            # Group parameters
            min_circles=4,
            max_circles=12,
            max_groups=7,
            
            # Motion parameters - calibrated for smooth movement
            radial_velocity=100.0,      # Initial outward speed
            angular_velocity=1.5,       # Initial rotation speed
            radial_acceleration=3.0,    # How quickly circles move in/out
            angular_acceleration=0.5,   # How quickly rotation changes
            
            # Visual parameters - tuned for optimal appearance
            base_size=25.0,            # Base circle diameter
            fade_duration=5.0,         # How long trails persist
            space_factor=0.5,          # Controls trail point density
            max_alpha=200,             # Maximum trail opacity (0-255)
            color_transition_speed=0.2, # How fast colors change
            
            # System parameters
            spawn_cooldown=4.0,        # Time between auto-spawns
            auto_generate=True,        # Whether to auto-spawn groups
            gradient_sharpness=0.2,    # Circle edge softness
            
            # Input state - initialized to neutral
            mouse_button_pressed=False,
            mouse_pos=(0, 0)
        )

    def validate(self):
        """Validate and correct parameter values."""
        # Ensure integer parameters are actually integers
        self.min_circles = int(self.min_circles)
        self.max_circles = int(self.max_circles)
        self.max_groups = int(self.max_groups)
        self.max_alpha = int(self.max_alpha)
        
        # Enforce value ranges
        self.min_circles = max(1, min(20, self.min_circles))
        self.max_circles = max(self.min_circles, min(20, self.max_circles))
        self.max_groups = max(1, min(20, self.max_groups))
        
        # Clamp float parameters to valid ranges
        self.radial_velocity = max(-1000, min(1000, self.radial_velocity))
        self.angular_velocity = max(-1000, min(1000, self.angular_velocity))
        self.radial_acceleration = max(-200, min(200, self.radial_acceleration))
        self.angular_acceleration = max(-200, min(200, self.angular_acceleration))
        
        self.base_size = max(2, min(100, self.base_size))
        self.fade_duration = max(1.0, min(30.0, self.fade_duration))
        self.space_factor = max(0.0, min(1.0, self.space_factor))
        self.max_alpha = max(0, min(255, self.max_alpha))
        self.color_transition_speed = max(0.0, min(1.0, self.color_transition_speed))
        self.spawn_cooldown = max(0.5, min(10.0, self.spawn_cooldown))
        
        return self

    def update_from_dict(self, params_dict):
        """Update parameters from a dictionary, with validation."""
        for key, value in params_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.validate()
        return self

    def copy(self):
        """Create a deep copy of parameters."""
        return SpringleParams(
            min_circles=self.min_circles,
            max_circles=self.max_circles,
            max_groups=self.max_groups,
            radial_velocity=self.radial_velocity,
            angular_velocity=self.angular_velocity,
            radial_acceleration=self.radial_acceleration,
            angular_acceleration=self.angular_acceleration,
            base_size=self.base_size,
            fade_duration=self.fade_duration,
            space_factor=self.space_factor,
            max_alpha=self.max_alpha,
            color_transition_speed=self.color_transition_speed,
            spawn_cooldown=self.spawn_cooldown,
            auto_generate=self.auto_generate,
            gradient_sharpness=self.gradient_sharpness,
            mouse_button_pressed=self.mouse_button_pressed,
            mouse_pos=self.mouse_pos
        )