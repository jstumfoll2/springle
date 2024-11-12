from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

from lib.KivySpingleCircle import KivySpingleCircle
from lib.SpringleParams import SpringleParams
from lib.TextOverlay import TextOverlay

from datetime import datetime
import os

class SpringleWidget(MDWidget):
    """Main widget that handles the particle animation system"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize system parameters
        self.params = SpringleParams.from_defaults()
        
        # Window handling
        Window.bind(on_resize=self._on_resize)
        Window.bind(mouse_pos=self._on_mouse_move)  # Add mouse position tracking
        
        # Store background color
        self.background_color = [185/255, 150/255, 234/255, 1]  # Default purple
        
         # Bind to size and position changes
        self.bind(size=self._update_background, pos=self._update_background)
        
        # Initialize circle system with current window size
        self.WIDTH = 800
        self.HEIGHT = 600
        self._init_circle_system(self.WIDTH, self.HEIGHT) # initial size, resized soon after
        
        # Restore parameters
        self.params.validate()
        
        # Update circle system with restored parameters
        self._sync_parameters()
        
        # Force update of mouse position relative to new center
        if hasattr(self, 'mouse_pos'):
            self._on_mouse_move(None, self.mouse_pos)
                
        # Add text overlay
        self.text_overlay = TextOverlay()
        self.add_widget(self.text_overlay)

        # Ensure screenshots directory exists
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         'data', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Track touch and mouse state
        self.touch_pressed = False
        self.current_touch = None
        self.mouse_pos = (0, 0)
        
        # Bind keyboard
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        
        # State flags
        self.paused = False
        self.auto_generate = True
        
        # Start update loop
        Clock.schedule_interval(self.widget_update, 1.0/120.0)
    
    def _init_circle_system(self, width, height):
        """Initialize or reinitialize the circle system"""
        self.circle_system = KivySpingleCircle(
            self.params.min_circles,
            self.params.max_circles,
            self.params.radial_velocity,
            self.params.angular_velocity,
            self.params.radial_acceleration,
            self.params.angular_acceleration,
            self.params.base_size,
            width, height
        )
        
        # Set additional system parameters
        self.circle_system.color_transition_speed = self.params.color_transition_speed
        self.circle_system.spawn_cooldown_start = self.params.spawn_cooldown
        self.circle_system.spawn_cooldown_current = self.params.spawn_cooldown
        self.circle_system.set_max_groups(self.params.max_groups)
        self.circle_system.fade_duration = self.params.fade_duration
    
    def _on_resize(self, instance, width, height):
        """Handle window resize events"""
        if width > 0 and height > 0:  # Prevent invalid dimensions
            self.WIDTH = width
            self.HEIGHT = height
            
            # Store current parameters
            current_params = self.params.copy()
            
            # Reinitialize circle system with new dimensions
            self._init_circle_system(width, height)
            
            # Restore parameters
            self.params = current_params
            self.params.validate()
            
            # Update circle system with restored parameters
            self._sync_parameters()
            
            # Force update of mouse position relative to new center
            if hasattr(self, 'mouse_pos'):
                self._on_mouse_move(None, self.mouse_pos)
    
    def _on_mouse_move(self, window, pos):
        """Track mouse position and update display"""
        self.mouse_pos = pos
        
        # Convert to centered coordinates
        center_x = self.WIDTH / 2 if hasattr(self, 'WIDTH') else Window.width / 2
        center_y = self.HEIGHT / 2 if hasattr(self, 'HEIGHT') else Window.height / 2
        rel_x = pos[0] - center_x
        rel_y = center_y - pos[1]  # Invert Y for mathematical coordinates
        
        # Update text overlay directly
        if hasattr(self, 'text_overlay'):
            self.text_overlay.update_mouse_pos(rel_x, rel_y)
            
    def _sync_parameters(self):
        """Synchronize all parameters with circle system"""
        if self.circle_system:
            # Update system parameters
            self.circle_system.color_transition_speed = self.params.color_transition_speed
            self.circle_system.spawn_cooldown_start = self.params.spawn_cooldown
            self.circle_system.set_max_groups(self.params.max_groups)
            self.circle_system.fade_duration = self.params.fade_duration
            self.circle_system.center = (self.WIDTH/2, self.HEIGHT/2)
            
            # Update group parameters
            for group in self.circle_system.groups:
                group.update_circle_size(self.params.base_size)
                group.update_circle_acceleration(
                    self.params.radial_acceleration,
                    self.params.angular_acceleration
                )
                group.center = (self.WIDTH/2, self.HEIGHT/2)
    
    def on_touch_down(self, touch):
        """Handle touch press events"""
        if self.collide_point(*touch.pos):
            self.touch_pressed = True
            self.current_touch = touch
            self.params.mouse_button_pressed = True
            self.params.mouse_pos = touch.pos
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch drag events"""
        if touch == self.current_touch:
            self.params.mouse_pos = touch.pos
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch release events"""
        if touch == self.current_touch:
            self.touch_pressed = False
            self.current_touch = None
            self.params.mouse_button_pressed = False
            return True
        return super().on_touch_up(touch)
    
    def _on_keyboard_closed(self):
        """Handle keyboard cleanup"""
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle keyboard input"""
        if keycode[1] == 'spacebar':
            self.toggle_pause()
            return True
        elif keycode[1] == 'c':
            self.clear_groups()
            self.circle_system.clear_trails()
            return True
        elif keycode[1] == 'o':
            self.toggle_options()
            return True
        elif keycode[1] == 'q':
            if hasattr(MDApp.get_running_app(), 'text_overlay'):
                MDApp.get_running_app().text_overlay.toggle_overlay()
            return True
        elif keycode[1] == 's':
            self.take_screenshot()
            return True
        return False

    def toggle_pause(self):
        """Toggle animation pause state"""
        self.paused = not self.paused
        if hasattr(MDApp.get_running_app(), 'options_panel'):
            MDApp.get_running_app().options_panel.update_pause_button(self.paused)

    def clear_groups(self):
        """Clear all particle groups"""
        if self.circle_system:
            self.circle_system.groups = []
            self.circle_system.spawn_cooldown_current = self.circle_system.spawn_cooldown_start

    def toggle_options(self):
        """Toggle options panel visibility"""
        if hasattr(MDApp.get_running_app(), 'nav_drawer'):
            MDApp.get_running_app().nav_drawer.set_state("open" 
                if MDApp.get_running_app().nav_drawer.state == "close" else "close")

    def take_screenshot(self):
        """Capture and save a screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"springle_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            Window.screenshot(name=filepath)
            
            if hasattr(MDApp.get_running_app(), 'text_overlay'):
                MDApp.get_running_app().text_overlay.show_screenshot_message(True)
            
            print(f"Screenshot saved: {filepath}")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            if hasattr(MDApp.get_running_app(), 'text_overlay'):
                MDApp.get_running_app().text_overlay.show_screenshot_message(False)
                
    def set_background_color(self, color):
        """Set the background color"""
        self.background_color = color
        
    def _update_background(self, *args):
        """Update background rectangle"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)
            
    def widget_update(self, dt):
        """Update animation state"""
        # Skip updates if paused
        if self.paused:
            return
            
        # # Update parameters from current touch state
        # self.params.mouse_button_pressed = self.touch_pressed
        # if self.current_touch:
        #     self.params.mouse_pos = self.current_touch.pos
        
        # Update circle system
        self.circle_system.kivy_circle_update(1/60, self.params)
        
        # Trigger a redraw
        self.canvas.clear()
        with self.canvas:
            self._update_background()
            # Draw circles and trails
            self.circle_system.draw(
                self.canvas,
                self.params.gradient_sharpness
            )