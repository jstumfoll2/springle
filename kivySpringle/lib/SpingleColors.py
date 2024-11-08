from typing import Tuple, List

class SpingleColors:
    """
    Manages color palettes with improved validation, interpolation, and error handling.
    """
    
    # Type alias for RGB colors
    ColorType = Tuple[int, int, int]
    
    # Validation constants
    MAX_COLOR_VALUE = 255
    MIN_COLOR_VALUE = 0
    COLORS_PER_PALETTE = 12
    
    def __init__(self):
        """Initialize color palettes with validation."""
        # Color palettes (each with 12 colors)
        self.COLOR_PALETTES: List[List[ColorType]] = [
            # Sunset Gradient
            [(255, 171, 0), (255, 140, 0), (255, 99, 71), (255, 69, 0), (255, 45, 0), 
            (255, 20, 47), (255, 0, 80), (225, 0, 108), (195, 0, 126), (165, 0, 168),
            (135, 0, 189), (105, 0, 204)],
            
            # Ocean Depths
            [(64, 224, 208), (0, 216, 217), (0, 186, 217), (0, 156, 217), (0, 116, 217),
            (30, 144, 255), (0, 191, 255), (135, 206, 250), (0, 150, 255), (0, 120, 255),
            (0, 90, 255), (0, 60, 255)],
            
            # Forest Canopy
            [(34, 139, 34), (0, 128, 0), (0, 100, 0), (107, 142, 35), (85, 107, 47),
            (154, 205, 50), (124, 252, 0), (50, 205, 50), (46, 139, 87), (60, 179, 113),
            (32, 178, 170), (47, 79, 79)],
            
            # Neon Lights
            [(255, 0, 255), (255, 0, 204), (255, 0, 153), (255, 0, 102), (255, 0, 51),
            (255, 51, 0), (255, 102, 0), (255, 153, 0), (255, 204, 0), (255, 255, 0),
            (204, 255, 0), (153, 255, 0)],
            
            # Galaxy Nebula
            [(123, 31, 162), (84, 13, 110), (32, 0, 255), (103, 58, 183), (156, 39, 176),
            (170, 7, 107), (244, 143, 177), (199, 0, 57), (255, 87, 51), (255, 141, 0),
            (170, 0, 255), (138, 43, 226)],
            
            # Northern Lights
            [(16, 255, 133), (39, 255, 175), (80, 255, 201), (132, 255, 217), (175, 255, 228),
            (202, 255, 251), (216, 255, 204), (171, 228, 155), (128, 200, 107), (86, 172, 59),
            (43, 144, 11), (0, 116, 0)],
            
            # Desert Sands
            [(242, 209, 158), (235, 189, 118), (217, 164, 65), (191, 144, 0), (166, 123, 0),
            (140, 103, 0), (115, 82, 0), (89, 62, 0), (64, 41, 0), (38, 21, 0),
            (217, 179, 130), (230, 197, 158)],
            
            # Deep Sea
            [(0, 119, 190), (0, 147, 196), (0, 174, 203), (0, 202, 209), (0, 229, 216),
            (0, 255, 222), (0, 229, 216), (0, 202, 209), (0, 174, 203), (0, 147, 196),
            (0, 119, 190), (0, 92, 183)],
            
            # Volcanic
            [(153, 0, 0), (179, 0, 0), (204, 0, 0), (230, 0, 0), (255, 0, 0),
            (255, 26, 0), (255, 51, 0), (255, 77, 0), (255, 102, 0), (255, 128, 0),
            (255, 153, 0), (255, 179, 0)],
            
            # Cotton Candy
            [(255, 183, 213), (255, 154, 204), (255, 124, 196), (255, 95, 187), (255, 66, 179),
            (255, 36, 170), (255, 7, 162), (255, 0, 153), (255, 0, 144), (255, 0, 135),
            (255, 0, 127), (255, 0, 118)],
            
            # Emerald City
            [(0, 201, 87), (0, 178, 89), (0, 154, 91), (0, 131, 93), (0, 107, 95),
            (0, 84, 97), (0, 60, 99), (0, 37, 101), (0, 13, 103), (0, 0, 105),
            (0, 0, 107), (0, 0, 109)],
            
            # Twilight
            [(25, 25, 112), (48, 25, 112), (72, 25, 112), (95, 25, 112), (119, 25, 112),
            (142, 25, 112), (165, 25, 112), (189, 25, 112), (212, 25, 112), (236, 25, 112),
            (255, 25, 112), (255, 48, 112)],
            
            # Rainbow Sherbet
            [(255, 192, 203), (255, 182, 193), (255, 160, 122), (255, 127, 80), (255, 99, 71),
            (255, 69, 0), (255, 140, 0), (255, 165, 0), (255, 215, 0), (255, 255, 0),
            (255, 255, 224), (255, 228, 196)],
            
            # Deep Purple
            [(48, 25, 52), (72, 38, 78), (95, 50, 104), (119, 63, 130), (142, 75, 156),
            (165, 88, 182), (189, 100, 208), (212, 113, 234), (236, 125, 255), (255, 138, 255),
            (255, 150, 255), (255, 163, 255)],
            
            # Electric Blue
            [(0, 255, 255), (0, 238, 255), (0, 221, 255), (0, 204, 255), (0, 187, 255),
            (0, 170, 255), (0, 153, 255), (0, 136, 255), (0, 119, 255), (0, 102, 255),
            (0, 85, 255), (0, 68, 255)],
            
            # Autumn Leaves
            [(255, 69, 0), (255, 99, 71), (255, 127, 80), (255, 140, 0), (255, 165, 0),
            (255, 191, 0), (255, 215, 0), (255, 239, 0), (255, 255, 0), (238, 232, 170),
            (240, 230, 140), (189, 183, 107)],
            
            # Cyberpunk
            [(255, 0, 128), (255, 0, 255), (178, 0, 255), (102, 0, 255), (25, 0, 255),
            (0, 128, 255), (0, 255, 255), (0, 255, 128), (0, 255, 0), (128, 255, 0),
            (255, 255, 0), (255, 128, 0)],
            
            # Arctic Aurora
            [(127, 255, 212), (64, 224, 208), (0, 255, 255), (0, 255, 127), (60, 179, 113),
            (46, 139, 87), (34, 139, 34), (50, 205, 50), (144, 238, 144), (152, 251, 152),
            (143, 188, 143), (102, 205, 170)],
            
            # Cosmic Dust
            [(148, 0, 211), (138, 43, 226), (123, 104, 238), (106, 90, 205), (72, 61, 139),
            (147, 112, 219), (153, 50, 204), (186, 85, 211), (128, 0, 128), (216, 191, 216),
            (221, 160, 221), (238, 130, 238)],
            
            # Tropical Paradise
            [(0, 255, 127), (0, 250, 154), (0, 255, 127), (124, 252, 0), (127, 255, 0),
            (173, 255, 47), (50, 205, 50), (152, 251, 152), (144, 238, 144), (0, 255, 127),
            (60, 179, 113), (46, 139, 87)],
            
            # Candy Shop
            [(255, 105, 180), (255, 182, 193), (255, 192, 203), (255, 20, 147), (219, 112, 147),
            (255, 160, 122), (255, 127, 80), (255, 99, 71), (255, 69, 0), (255, 140, 0),
            (255, 160, 122), (255, 127, 80)],
            
            # Deep Ocean
            [(0, 0, 139), (0, 0, 205), (0, 0, 255), (30, 144, 255), (0, 191, 255),
            (135, 206, 235), (135, 206, 250), (176, 224, 230), (173, 216, 230), (0, 255, 255),
            (127, 255, 212), (64, 224, 208)],
            
            # Cherry Blossom
            [(255, 192, 203), (255, 182, 193), (255, 160, 122), (255, 127, 80), (255, 99, 71),
            (255, 69, 0), (255, 0, 0), (255, 20, 147), (255, 105, 180), (255, 182, 193),
            (255, 192, 203), (219, 112, 147)],
            
            # Golden Hour
            [(255, 215, 0), (255, 223, 0), (255, 231, 0), (255, 239, 0), (255, 247, 0),
            (255, 255, 0), (255, 247, 0), (255, 239, 0), (255, 231, 0), (255, 223, 0),
            (255, 215, 0), (255, 207, 0)],
            
            # Moonlight
            [(25, 25, 112), (0, 0, 128), (0, 0, 139), (0, 0, 205), (0, 0, 255),
            (65, 105, 225), (100, 149, 237), (135, 206, 235), (135, 206, 250), (176, 224, 230),
            (173, 216, 230), (240, 248, 255)]
        ]
        
        # Validate all palettes on initialization
        self._validate_palettes()
        
        # Cache for interpolated colors
        self._color_cache = {}
        self._max_cache_size = 1000
    
    def _validate_palettes(self) -> None:
        """Validate all color palettes for proper format and values."""
        if not self.COLOR_PALETTES:
            raise ValueError("No color palettes defined")
            
        for i, palette in enumerate(self.COLOR_PALETTES):
            if len(palette) != self.COLORS_PER_PALETTE:
                raise ValueError(f"Palette {i} must have exactly {self.COLORS_PER_PALETTE} colors")
                
            for j, color in enumerate(palette):
                self._validate_color(color, f"Palette {i}, Color {j}")
    
    def _validate_color(self, color: tuple, location: str = "") -> None:
        """
        Validate a single color tuple.
        
        Args:
            color: RGB color tuple to validate
            location: String describing where this color is used (for error messages)
        
        Raises:
            ValueError: If color format is invalid
        """
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            raise ValueError(f"Invalid color format at {location}: {color}")
            
        for i, component in enumerate(color):
            if not isinstance(component, int):
                raise ValueError(f"Color component must be integer at {location}: {component}")
            if not self.MIN_COLOR_VALUE <= component <= self.MAX_COLOR_VALUE:
                raise ValueError(
                    f"Color component must be between {self.MIN_COLOR_VALUE} and "
                    f"{self.MAX_COLOR_VALUE} at {location}: {component}"
                )
    
    def _validate_indices(self, pattern_index: int, color_index: int) -> None:
        """
        Validate pattern and color indices.
        
        Args:
            pattern_index: Index of the color pattern
            color_index: Index within the pattern
            
        Returns:
            Tuple of validated indices
        """
        pattern_index = pattern_index % len(self.COLOR_PALETTES)
        color_index = color_index % self.COLORS_PER_PALETTE
        return pattern_index, color_index
    
    def _validate_transition(self, transition_factor: float) -> float:
        """
        Validate and normalize transition factor.
        
        Args:
            transition_factor: Raw transition factor
            
        Returns:
            Normalized transition factor between 0 and 1
        """
        return max(0.0, min(1.0, float(transition_factor)))
    
    def _get_cache_key(self, pattern_index: int, color_index: int, 
                      transition_factor: float) -> tuple:
        """Generate cache key for color interpolation."""
        # Round transition factor to reduce cache size
        rounded_transition = round(transition_factor * 100) / 100
        return (pattern_index, color_index, rounded_transition)
    
    def _manage_cache(self) -> None:
        """Manage color cache size."""
        if len(self._color_cache) > self._max_cache_size:
            # Clear half of the cache when it gets too large
            cache_items = list(self._color_cache.items())
            self._color_cache = dict(cache_items[len(cache_items)//2:])
    
    def lerp_color(self, color1: ColorType, color2: ColorType, 
                   t: float, use_lab: bool = True) -> ColorType:
        """
        Interpolate between two colors with improved blending.
        
        Args:
            color1: First RGB color
            color2: Second RGB color
            t: Transition factor (0 to 1)
            use_lab: Whether to use LAB color space for interpolation
            
        Returns:
            Interpolated RGB color
        """
        t = self._validate_transition(t)
        
        if use_lab:
            # Convert to LAB color space for better interpolation
            lab1 = self._rgb_to_lab(color1)
            lab2 = self._rgb_to_lab(color2)
            
            # Interpolate in LAB space
            lab_result = tuple(
                a + (b - a) * t for a, b in zip(lab1, lab2)
            )
            
            # Convert back to RGB
            return self._lab_to_rgb(lab_result)
        else:
            # Simple RGB interpolation
            return tuple(
                int(a + (b - a) * t) for a, b in zip(color1, color2)
            )
    
    def _rgb_to_lab(self, rgb: ColorType) -> tuple:
        """Convert RGB to LAB color space."""
        # RGB to XYZ
        r, g, b = [x / 255.0 for x in rgb]
        
        def transform(c):
            if c > 0.04045:
                return ((c + 0.055) / 1.055) ** 2.4
            return c / 12.92
        
        r, g, b = transform(r), transform(g), transform(b)
        
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        
        # XYZ to LAB
        def f(t):
            if t > 0.008856:
                return t ** (1/3)
            return 7.787 * t + 16/116
        
        xn, yn, zn = 0.95047, 1.00000, 1.08883
        
        l = 116 * f(y/yn) - 16
        a = 500 * (f(x/xn) - f(y/yn))
        b = 200 * (f(y/yn) - f(z/zn))
        
        return (l, a, b)
    
    def _lab_to_rgb(self, lab: tuple) -> ColorType:
        """Convert LAB to RGB color space."""
        l, a, b = lab
        
        def f_inv(t):
            if t > 0.206893:
                return t ** 3
            return (t - 16/116) / 7.787
        
        # LAB to XYZ
        xn, yn, zn = 0.95047, 1.00000, 1.08883
        
        y = yn * f_inv((l + 16) / 116)
        x = xn * f_inv((l + 16) / 116 + a / 500)
        z = zn * f_inv((l + 16) / 116 - b / 200)
        
        # XYZ to RGB
        r = x *  3.2406 + y * -1.5372 + z * -0.4986
        g = x * -0.9689 + y *  1.8758 + z *  0.0415
        b = x *  0.0557 + y * -0.2040 + z *  1.0570
        
        def transform(c):
            if c > 0.0031308:
                return 1.055 * (c ** (1/2.4)) - 0.055
            return 12.92 * c
        
        r, g, b = transform(r), transform(g), transform(b)
        
        # Clamp and convert to 8-bit
        return tuple(
            int(max(0, min(255, round(c * 255)))) for c in (r, g, b)
        )
    
    def numPatterns(self) -> int:
        """Get number of available patterns."""
        return len(self.COLOR_PALETTES)
    
    def getPalette(self, index: int) -> List[ColorType]:
        """
        Get a specific color palette with validation.
        
        Args:
            index: Palette index
            
        Returns:
            List of RGB colors
        """
        index = index % len(self.COLOR_PALETTES)
        return self.COLOR_PALETTES[index]
    
    def getColor(self, pattern_index: int, color_index: int, 
                 transition_factor: float) -> ColorType:
        """
        Get interpolated color with caching and validation.
        
        Args:
            pattern_index: Index of the color pattern
            color_index: Index within the pattern
            transition_factor: Transition factor between patterns
            
        Returns:
            RGB color tuple
        """
        try:
            # Validate and normalize inputs
            pattern_index, color_index = self._validate_indices(pattern_index, color_index)
            transition_factor = self._validate_transition(transition_factor)
            
            # Check cache
            cache_key = self._get_cache_key(pattern_index, color_index, transition_factor)
            if cache_key in self._color_cache:
                return self._color_cache[cache_key]
            
            # Get colors from current and next pattern
            current_palette = self.COLOR_PALETTES[pattern_index]
            next_palette = self.COLOR_PALETTES[(pattern_index + 1) % len(self.COLOR_PALETTES)]
            
            current_color = current_palette[color_index]
            next_color = next_palette[color_index]
            
            # Interpolate colors in LAB space
            color = self.lerp_color(current_color, next_color, transition_factor)
            
            # Cache result
            self._color_cache[cache_key] = color
            self._manage_cache()
            
            return color
            
        except Exception as e:
            print(f"Error getting color: {e}")
            # Return safe fallback color (white)
            return (255, 255, 255)