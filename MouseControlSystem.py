class MouseControlSystem:
    def __init__(self):
        self.is_dragging = False
        self.start_pos = None
        self.current_pos = None
        self.velocity = (0, 0)
        self.history = []  # List of (pos, time) tuples
        self.history_duration = 0.1  # Duration in seconds to track history
        
    def start_drag(self, pos):
        self.is_dragging = True
        self.start_pos = pos
        self.current_pos = pos
        self.history = [(pos, 0)]
        
    def update_drag(self, pos, dt):
        if self.is_dragging:
            self.current_pos = pos
            self.history.append((pos, dt))
            
            # Keep only recent history for velocity calculation
            total_time = 0
            i = len(self.history) - 1
            while i >= 0 and total_time < self.history_duration:
                total_time += self.history[i][1]
                i -= 1
            self.history = self.history[max(0, i):]
            
    def end_drag(self):
        """Calculate final velocity from mouse movement history."""
        if len(self.history) >= 2:
            # Use the last few positions to calculate velocity
            start_pos, _ = self.history[0]
            end_pos, dt = self.history[-1]
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            
            if dt > 0:
                self.velocity = (dx / dt, dy / dt)
            else:
                self.velocity = (0, 0)
        else:
            self.velocity = (0, 0)
        
        self.is_dragging = False
        self.history = []
        return self.velocity