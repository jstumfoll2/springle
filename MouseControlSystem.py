class MouseControlSystem:
    def __init__(self, velocity_samples=25):
        self.is_dragging = False
        self.start_pos = None
        self.current_pos = None
        self.velocity = (0, 0)
        self.history = []  # List of (pos, time) tuples
        self.history_duration = 0.1  # Duration in seconds to track history
        self.velocity_samples = velocity_samples  # Number of samples to use for velocity calculation
        
    def start_drag(self, pos):
        self.is_dragging = True
        self.start_pos = pos
        self.current_pos = pos
        self.history = []
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
        """Calculate final velocity from averaged mouse movement history."""
        if len(self.history) >= 2:
            # Get the last N positions based on velocity_samples
            samples = min(self.velocity_samples, len(self.history))
            positions = self.history[-samples:]
            
            # Calculate total displacement and time
            total_dx = 0
            total_dy = 0
            total_dt = 0
            
            # Calculate displacements between consecutive points
            for i in range(len(positions)-1):
                start_pos, start_time = positions[i]
                end_pos, end_time = positions[i+1]
                
                dx = start_pos[0] - end_pos[0]
                dy = -start_pos[1] + end_pos[1]
                dt = end_time
                
                total_dx += dx
                total_dy += dy
                total_dt += dt
            
            # Calculate average velocity
            if total_dt > 0:
                avg_vx = total_dx / total_dt
                avg_vy = total_dy / total_dt
                self.velocity = (avg_vx, avg_vy)
            else:
                self.velocity = (0, 0)
        else:
            self.velocity = (0, 0)
        
        # print("velocity: ", self.velocity)
        self.is_dragging = False
        return self.velocity