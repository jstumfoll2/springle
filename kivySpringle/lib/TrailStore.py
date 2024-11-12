import numpy as np
from typing import List, Dict, Tuple
import gc

from typing import Tuple

class TrailPoint:
    """Efficient storage for trail points using slots with property-based access control."""
    __slots__ = ['_x', '_y', '_color', '_size', '_group_id', '_creation_time', '_age', '_texture', '_alpha']
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 size: float, group_id: int, creation_time: float, texture, alpha: int):
        self._x = float(x)
        self._y = float(y)
        self._color = tuple(color)
        self._size = float(size)
        self._group_id = int(group_id)
        self._creation_time = float(creation_time)
        self._age = 0.0
        self._texture = texture
        self._alpha = int(alpha)
    
    @property
    def x(self) -> float:
        """Get x coordinate."""
        return self._x
    
    @x.setter
    def x(self, value: float):
        """Set x coordinate."""
        self._x = float(value)
    
    @property
    def y(self) -> float:
        """Get y coordinate."""
        return self._y
    
    @y.setter
    def y(self, value: float):
        """Set y coordinate."""
        self._y = float(value)
    
    @property
    def color(self) -> Tuple[int, int, int]:
        """Get RGB color tuple."""
        return self._color
    
    @color.setter
    def color(self, value: Tuple[int, int, int]):
        """Set RGB color tuple."""
        if not isinstance(value, (tuple, list)) or len(value) != 3:
            raise ValueError("Color must be a tuple of 3 integers")
        self._color = tuple(map(int, value))
    
    @property
    def size(self) -> float:
        """Get point size."""
        return self._size
    
    @size.setter
    def size(self, value: float):
        """Set point size."""
        self._size = float(value)
    
    @property
    def group_id(self) -> int:
        """Get group ID."""
        return self._group_id
    
    @group_id.setter
    def group_id(self, value: int):
        """Set group ID."""
        self._group_id = int(value)
    
    @property
    def creation_time(self) -> float:
        """Get creation timestamp."""
        return self._creation_time
    
    @creation_time.setter
    def creation_time(self, value: float):
        """Set creation timestamp."""
        self._creation_time = float(value)
    
    @property
    def age(self) -> float:
        """Get point age."""
        return self._age
    
    @age.setter
    def age(self, value: float):
        """Set point age."""
        self._age = float(value)
    
    @property
    def texture(self):
        """Get point texture."""
        return self._texture
    
    @texture.setter
    def texture(self, value):
        """Set point texture."""
        self._texture = value
    
    @property
    def alpha(self) -> int:
        """Get alpha transparency value."""
        return self._alpha
    
    @alpha.setter
    def alpha(self, value: int):
        """Set alpha transparency value."""
        self._alpha = int(value)

    
class TrailStore:
    """
    Centralized store for particle trails with optimized memory and rendering.
    Uses numpy for efficient calculations and memory management.
    """
    
    def __init__(self, fade_duration: float = 5.0, max_points: int = 50000, cleanup_interval: float = 1.0):
        self.trails = [] #= TrailBuffer(max_points) #
        self.fade_duration = fade_duration
        self.max_points = max_points
        self.cleanup_interval = cleanup_interval
        self.last_cleanup_time = 0
        
        # Pre-allocate numpy arrays for calculations
        self._fade_factors = np.zeros(max_points, dtype=np.float32)
        self._alpha_values = np.zeros(max_points, dtype=np.uint8)
        
        # Track statistics
        self.total_points_added = 0
        self.total_points_removed = 0
    
    def add_point(self, x: float, y: float, color: Tuple[int, int, int], 
                 size: float, group_id: int, creation_time: float, texture) -> None:
        """Add trail point with overflow protection."""

        # Enforce maximum points limit
        if len(self.trails) >= self.max_points:
            # Remove oldest 20% of points when limit is reached
            remove_count = self.max_points // 5
            self.trails = self.trails[remove_count:]

        point = TrailPoint(x, y, color, size, group_id, creation_time, texture, 1)
        self.trails.append(point)
        
    def trail_store_update(self, dt: float, current_time: float, max_alpha: int) -> None:
        """Update trails with periodic cleanup."""
        if not self.trails:
            return
            
        # # Periodic cleanup of expired trails and inactive groups
        # if current_time - self.last_cleanup_time >= self.cleanup_interval:
        #     self._perform_cleanup(current_time)
        #     self.last_cleanup_time = current_time
            
        # Vectorized calculations
        creation_time = np.array([t._creation_time for t in self.trails])
        ages = current_time - creation_time
        progress = np.clip(ages / self.fade_duration, 0, 1)
        self._fade_factors = 1 - (progress * progress * progress)
        self._alpha_values = (max_alpha * self._fade_factors).astype(np.uint8)
        
        # update alpha values
        for i, trail in enumerate(self.trails):
            if self._alpha_values[i] < 5:
                self.trails.pop(i)
            trail.alpha = self._alpha_values[i]
    
    # def _perform_cleanup(self, current_time: float) -> None:
    #     """Thorough cleanup of trails and inactive groups."""
    #     # Remove expired trails
    #     # cutoff_time = current_time - self.fade_duration
    #     self.trails = [trail for trail in self.trails if trail.alpha < 10]
        
            
    # def _update_trail(self, trail: TrailPoint, age: float) -> bool:
    #     """Update a single trail point. Returns False if trail should be removed."""
    #     trail.age = age
    #     return age < self.fade_duration
    
    def get_drawable_elements(self):
        """
        Get all drawable elements with pre-calculated fade values.
        Uses vectorized operations for efficiency.
        """
        if not self.trails:
            return []

        return self.trails

    def clear_all(self) -> None:
        """Clear all trails and reset state."""
        self.trails.clear()
        # self.active_groups.clear()
        gc.collect()  # Force garbage collection
    
    def get_stats(self) -> Dict:
        """Get statistics about the trail store."""
        return {
            'active_points': len(self.trails),
            'total_added': self.total_points_added,
            'total_removed': self.total_points_removed,
            'max_points': self.max_points,
            'memory_usage': len(self.trails) * 64  # Approximate bytes per trail point
        }
        
        

class TrailBuffer:
    """Fixed-size circular buffer for trail points with pre-allocation."""
    
    def __init__(self, capacity: int):
        """
        Initialize pre-allocated trail buffer.
        
        Args:
            capacity: Maximum number of trail points to store
        """
        self.capacity = capacity
        self.size = 0  # Current number of valid points
        self.head = 0  # Index for next insertion
        
        # Pre-allocate array of trail points with None
        self.buffer: List[TrailPoint | None] = [None] * capacity
        
    def append(self, point: TrailPoint) -> None:
        """
        Add a point to the buffer, overwriting oldest point if full.
        
        Args:
            point: TrailPoint to add
        """
        # Store the point at current head position
        self.buffer[self.head] = point
        
        # Update head position
        self.head = (self.head + 1) % self.capacity
        
        # Update size until capacity is reached
        self.size = min(self.size + 1, self.capacity)
    
    def clear(self) -> None:
        """Clear all points from buffer."""
        self.size = 0
        self.head = 0
        self.buffer = [None] * self.capacity
    
    def __iter__(self):
        """Iterate over valid points in order from oldest to newest."""
        if self.size == 0:
            return
            
        # If buffer is not full, iterate from start up to size
        if self.size < self.capacity:
            for i in range(self.size):
                if self.buffer[i] is not None:
                    yield self.buffer[i]
            return
            
        # If buffer is full, iterate from head to end, then start to head
        for i in range(self.head, self.capacity):
            if self.buffer[i] is not None:
                yield self.buffer[i]
        for i in range(0, self.head):
            if self.buffer[i] is not None:
                yield self.buffer[i]
    
    def __len__(self) -> int:
        """Get number of valid points in buffer."""
        return self.size