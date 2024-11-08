from dataclasses import dataclass

@dataclass
class SpringleParams:
    """Parameters for SpringleCircle update."""
    min_circles: int
    max_circles: int
    radial_velocity: float
    angular_velocity: float
    radial_acceleration: float
    angular_acceleration: float
    base_size: float
    mouse_button_pressed: bool
    mouse_pos: tuple
    fade_duration: float
    space_factor: float
    max_alpha: int = 200
    auto_generate: bool = True
    gradient_sharpness: float = 5.0  # Added gradient sharpness parameter

    @classmethod
    def from_defaults(cls):
        """Create instance with default values."""
        return cls(
            min_circles=4,
            max_circles=12,
            radial_velocity=100,
            angular_velocity=1.5,
            radial_acceleration=3,
            angular_acceleration=0.5,
            base_size=50,
            mouse_button_pressed=False,
            mouse_pos=(0, 0),
            fade_duration=2.0,
            space_factor=0.05,
            max_alpha=200,
            auto_generate=True,
            gradient_sharpness=5.0  # Default value
        )