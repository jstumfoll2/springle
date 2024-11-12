import cProfile
import pstats
import io
import time
import psutil
import gc
from functools import wraps
from collections import deque
from typing import Dict, List, Optional, Tuple, Callable
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import NumericProperty, ListProperty

class PerformanceMetrics:
    """Stores and calculates performance metrics"""
    def __init__(self, max_samples: int = 120):
        self.max_samples = max_samples
        self.frame_times = deque(maxlen=max_samples)
        self.method_times: Dict[str, deque] = {}
        self.memory_usage = deque(maxlen=max_samples)
        
    def add_frame_time(self, frame_time: float):
        """Add a new frame time measurement"""
        self.frame_times.append(frame_time)
        
    def add_method_time(self, method_name: str, execution_time: float):
        """Add a new method execution time measurement"""
        if method_name not in self.method_times:
            self.method_times[method_name] = deque(maxlen=self.max_samples)
        self.method_times[method_name].append(execution_time)
        
    def add_memory_usage(self, usage: float):
        """Add a new memory usage measurement"""
        self.memory_usage.append(usage)
        
    def get_fps(self) -> float:
        """Calculate current FPS based on recent frame times"""
        if not self.frame_times:
            return 0.0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
        
    def get_method_stats(self, method_name: str) -> Tuple[float, float, float]:
        """Get min, max, and average execution time for a method"""
        if method_name not in self.method_times or not self.method_times[method_name]:
            return (0.0, 0.0, 0.0)
        times = self.method_times[method_name]
        return (min(times), max(times), sum(times) / len(times))
        
    def get_memory_stats(self) -> Tuple[float, float, float]:
        """Get min, max, and average memory usage"""
        if not self.memory_usage:
            return (0.0, 0.0, 0.0)
        return (min(self.memory_usage), max(self.memory_usage), 
                sum(self.memory_usage) / len(self.memory_usage))

class PerformanceGraph(BoxLayout):
    """Real-time performance graph widget"""
    data = ListProperty([])
    max_value = NumericProperty(0)
    line_color = ListProperty([0, 1, 0, 1])
    
    def __init__(self, max_samples=120, **kwargs):
        super().__init__(**kwargs)
        self.max_samples = max_samples
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        
    def _update_canvas(self, *args):
        """Update the graph canvas"""
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw background
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            if not self.data:
                return
                
            # Draw grid lines
            Color(0.3, 0.3, 0.3, 1)
            for i in range(4):
                y = self.pos[1] + (self.height * (i + 1) / 4)
                Line(points=[self.pos[0], y, self.pos[0] + self.width, y])
            
            # Draw graph line
            Color(*self.line_color)
            points = []
            max_val = self.max_value or max(self.data)
            if max_val == 0:
                return
                
            for i, value in enumerate(self.data):
                x = self.pos[0] + (i * self.width / (self.max_samples - 1))
                y = self.pos[1] + (value * self.height / max_val)
                points.extend([x, y])
                
            if len(points) >= 4:
                Line(points=points)
    
    def update_data(self, new_data):
        """Update graph data"""
        self.data = new_data
        self._update_canvas()

class ProfilerOverlay(MDCard):
    """Overlay widget displaying performance metrics"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.size = (dp(300), dp(400))
        self.pos_hint = {'right': 0.99, 'top': 0.99}
        self.padding = dp(8)
        self.spacing = dp(4)
        
        # FPS Display
        self.fps_label = MDLabel(
            text="FPS: --",
            theme_text_color="Secondary",
            font_style="Caption"
        )
        self.add_widget(self.fps_label)
        
        # FPS Graph
        self.fps_graph = PerformanceGraph(
            size_hint_y=0.3,
            line_color=[0, 1, 0, 1]
        )
        self.add_widget(self.fps_graph)
        
        # Memory Usage Display
        self.memory_label = MDLabel(
            text="Memory: --",
            theme_text_color="Secondary",
            font_style="Caption"
        )
        self.add_widget(self.memory_label)
        
        # Memory Graph
        self.memory_graph = PerformanceGraph(
            size_hint_y=0.3,
            line_color=[1, 0.5, 0, 1]
        )
        self.add_widget(self.memory_graph)
        
        # Method Timings
        self.methods_label = MDLabel(
            text="Method Timings:",
            theme_text_color="Secondary",
            font_style="Caption"
        )
        self.add_widget(self.methods_label)
        
        # Toggle Button
        self.toggle_button = MDRaisedButton(
            text="Hide Profiler",
            size_hint=(1, None),
            height=dp(36),
            on_release=self.toggle_visibility
        )
        self.add_widget(self.toggle_button)
        
    def toggle_visibility(self, *args):
        """Toggle profiler visibility"""
        self.opacity = 1.0 if self.opacity == 0.0 else 0.0
        self.toggle_button.text = "Show Profiler" if self.opacity == 0.0 else "Hide Profiler"
        
    def update_display(self, metrics: PerformanceMetrics):
        """Update the display with new metrics"""
        # Update FPS
        fps = metrics.get_fps()
        self.fps_label.text = f"FPS: {fps:.1f}"
        self.fps_graph.update_data(list(metrics.frame_times))
        
        # Update Memory
        min_mem, max_mem, avg_mem = metrics.get_memory_stats()
        self.memory_label.text = f"Memory: {avg_mem:.1f}MB (Min: {min_mem:.1f}, Max: {max_mem:.1f})"
        self.memory_graph.update_data(list(metrics.memory_usage))
        
        # Update Method Timings
        method_text = "Method Timings:\n"
        for method_name, times in metrics.method_times.items():
            min_time, max_time, avg_time = metrics.get_method_stats(method_name)
            method_text += f"{method_name}: {avg_time*1000:.1f}ms\n"
        self.methods_label.text = method_text

class SpringleProfiler:
    """Main profiler class for the Springle application"""
    def __init__(self, app):
        self.app = app
        self.metrics = PerformanceMetrics()
        self.overlay = ProfilerOverlay()
        self.profiling_enabled = True
        self.last_frame_time = time.time()
        
        # Schedule the overlay addition for the next frame
        Clock.schedule_once(self._add_overlay)
        
        # Start update schedule
        Clock.schedule_interval(self.update, 1.0/120.0)  # 30 fps updates
        
    def _add_overlay(self, dt):
        """Add overlay to the root widget after it's created"""
        if self.app.root:
            self.app.root.add_widget(self.overlay)
        else:
            # If root is not ready, try again in the next frame
            Clock.schedule_once(self._add_overlay)
        
    def profile_method(self, method: Callable) -> Callable:
        """Decorator for profiling method execution time"""
        @wraps(method)
        def wrapper(*args, **kwargs):
            if not self.profiling_enabled:
                return method(*args, **kwargs)
                
            start_time = time.time()
            result = method(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self.metrics.add_method_time(method.__name__, execution_time)
            return result
        return wrapper
    
    def update(self, dt):
        """Update profiler metrics"""
        if not self.profiling_enabled:
            return
            
        # Update frame time
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        self.metrics.add_frame_time(frame_time)
        
        # Update memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.metrics.add_memory_usage(memory_mb)
        
        # Update display
        self.overlay.update_display(self.metrics)
        
    def start_profiling(self):
        """Start profiling"""
        self.profiling_enabled = True
        self.overlay.opacity = 1.0
        
    def stop_profiling(self):
        """Stop profiling"""
        self.profiling_enabled = False
        self.overlay.opacity = 0.0
        
    def toggle_profiling(self):
        """Toggle profiling on/off"""
        if self.profiling_enabled:
            self.stop_profiling()
        else:
            self.start_profiling()
            
    def profile_critical_methods(self):
        """Profile critical methods in the Springle app"""
        # Schedule the profiling setup for after the widgets are created
        Clock.schedule_once(self._setup_profiling)
            
    def _setup_profiling(self, dt):
        """Setup profiling after widgets are created"""
        if not hasattr(self.app, 'springle_widget') or not self.app.springle_widget:
            # If widgets aren't ready, try again in the next frame
            Clock.schedule_once(self._setup_profiling)
            return
            
        # Profile SpringleWidget methods
        self.app.springle_widget.widget_update = self.profile_method(self.app.springle_widget.widget_update)
        # self.app.springle_widget._update_background = self.profile_method(
        #     self.app.springle_widget._update_background)
            
        # Profile KivySpingleCircle methods
        circle_system = self.app.springle_widget.circle_system
        circle_system.kivy_circle_update = self.profile_method(circle_system.kivy_circle_update)
        # circle_system.group_update = self.profile_method(circle_system.group_update)
        # circle_system.update_mouse = self.profile_method(circle_system.update_mouse)
        # circle_system.update_group_spawn = self.profile_method(circle_system.update_group_spawn)
        # circle_system._create_new_group = self.profile_method(circle_system._create_new_group)
        # circle_system._get_cached_gradient = self.profile_method(circle_system._get_cached_gradient)
        
        circle_system.draw = self.profile_method(circle_system.draw)
        
        
        trail_store = circle_system.trail_store
        trail_store.trail_store_update = self.profile_method(trail_store.trail_store_update)
        # trail_store.get_drawable_elements = self.profile_method(trail_store.get_drawable_elements)
        


def initialize_profiler(app):
    """Initialize and setup the profiler"""
    profiler = SpringleProfiler(app)
    profiler.profile_critical_methods()
    return profiler