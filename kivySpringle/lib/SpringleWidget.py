from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color

from lib.KivySpingleCircle import KivySpingleCircle
from lib.SpringleParams import SpringleParams
from lib.TextOverlay import TextOverlay

from datetime import datetime
import os

# TODO List:
# 2. Remaining features to implement:
#    - Mouse position in bottom right corner
#    - Background color selector in options menu
# 3. Convert all Kivy widgets to KivyMD counterparts
        
class SpringleWidget(MDWidget):
    """Main widget that handles the particle animation system"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize system parameters
        self.params = SpringleParams.from_defaults()
        Window.bind(on_resize=self._on_resize)
        
        # Manually trigger resize to handle initial window size change
        # self._on_resize(None, *Window.size)  # Trigger resize handler with current size
        
        # Initialize circle system
        self._init_circle_system(800,600) # initial size, resized soon after
        
        # Add text overlay
        self.text_overlay = TextOverlay()
        self.add_widget(self.text_overlay)

        # Ensure screenshots directory exists
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         'data', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Track touch state
        self.touch_pressed = False
        self.current_touch = None
        
        # Bind keyboard
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        
        # State flags
        self.paused = False
        self.auto_generate = True
        
        # Start update loop
        Clock.schedule_interval(self.update, 1.0/60.0)
    
    def _init_circle_system(self, width, height):
        """Initialize or reinitialize the circle system"""
        
        # print(f"Initializing circle system with size: {width}x{height}")  # Debug print
        self.circle_system = KivySpingleCircle(
            self.params.min_circles,
            self.params.max_circles,
            self.params.radial_velocity,      # Changed from starting_radial_velocity
            self.params.angular_velocity,      # Changed from starting_angular_velocity
            self.params.radial_acceleration,
            self.params.angular_acceleration,
            self.params.base_size,
            width, height
        )
        
        # Set additional parameters
        self.circle_system.color_transition_speed = 0.2
        self.circle_system.spawn_cooldown_start = 4.0
        self.circle_system.spawn_cooldown_current = 4.0
        self.circle_system.set_max_groups(7)
        
    def _on_resize(self, instance, width, height):
        """Handle window resize events"""
        # print(f"Widget Window resized to: {width}x{height}")  # Debug print

        self._init_circle_system(width, height)
    
    def on_touch_down(self, touch):
        """Handle touch press events"""
        if self.collide_point(*touch.pos):
            self.touch_pressed = True
            self.current_touch = touch
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch drag events"""
        if touch == self.current_touch:
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch release events"""
        if touch == self.current_touch:
            self.touch_pressed = False
            self.current_touch = None
            return True
        return super().on_touch_up(touch)
    
    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar':
            self.toggle_pause()
            return True
        elif keycode[1] == 'c':
            self.clear_groups()
            return True
        elif keycode[1] == 'o':
            self.toggle_options()
            return True
        elif keycode[1] == 'q':
            # Access text overlay through app instance
            if hasattr(MDApp.get_running_app(), 'text_overlay'):
                MDApp.get_running_app().text_overlay.toggle_overlay()
            return True
        elif keycode[1] == 's':
            self.take_screenshot()
            return True
        return False

    def toggle_pause(self):
        self.paused = not self.paused
        if hasattr(MDApp.get_running_app(), 'options_panel'):
            MDApp.get_running_app().options_panel.update_pause_button(self.paused)

    def clear_groups(self):
        if self.circle_system:
            self.circle_system.groups = []
            self.circle_system.fading_trails = []
            self.circle_system.spawn_cooldown_current = self.circle_system.spawn_cooldown_start

    def toggle_options(self):
        if hasattr(MDApp.get_running_app(), 'nav_drawer'):
            MDApp.get_running_app().nav_drawer.set_state("open" 
                if MDApp.get_running_app().nav_drawer.state == "close" else "close")

    def take_screenshot(self):
        """Capture and save a screenshot of the current window"""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"springle_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Take screenshot
            Window.screenshot(name=filepath)
            
            # Show success feedback using existing text overlay
            if hasattr(MDApp.get_running_app(), 'text_overlay'):
                MDApp.get_running_app().text_overlay.show_screenshot_message(True)
            
            print(f"Screenshot saved: {filepath}")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            
            # Show error feedback
            if hasattr(MDApp.get_running_app(), 'text_overlay'):
                MDApp.get_running_app().text_overlay.show_screenshot_message(False)
                
    def update(self, dt):
        """Update the animation state"""
        # Update parameters from current touch state
        self.params.mouse_button_pressed = self.touch_pressed
        if self.current_touch:
            self.params.mouse_pos = self.current_touch.pos
        
        # Skip updates if paused
        if self.paused:
            return
        
        # Update circle system
        self.circle_system.update(dt, self.params)
        
        # Trigger a redraw
        self.canvas.clear()
        with self.canvas:
            # Draw background (we'll integrate with background color manager later)
            Color(185/255, 150/255, 234/255)  # Default purple background
            
            # Draw circles and trails
            self.circle_system.draw(
                self.canvas, 
                self.params.max_alpha,
                self.params.gradient_sharpness
            )