
from kivymd.uix.widget import MDWidget
from kivymd.uix.label import MDLabel

from kivy.clock import Clock
from kivy.core.window import Window

from kivy.animation import Animation

class TextOverlay(MDWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Overlay Positions
        self.xpos = 80
        self.ypos = 20
        
        # Initial help label
        self.initial_help = MDLabel(
            text='Press \'q\' to enable text overlay',
            font_size=14,  # Smaller font
            halign="left",
            valign="bottom",
            adaptive_size=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.initial_help)
        
        # Command list with consistent positioning
        self.commands = MDLabel(
            text=('\n'.join([
                'Press "s" to save screenshot',
                'Press "o" to toggle options',
                'Press "c" to clear all groups',
                'Press "space" to pause',
                'Press "q" to toggle this overlay'
            ])),
            font_size=14,  # Smaller font
            halign="left",
            valign="bottom",
            adaptive_size=True,
            color=(1, 1, 1, 1),
            opacity=0
        )
        self.add_widget(self.commands)
        
        # Add screenshot feedback label
        self.screenshot_feedback = MDLabel(
            text="",  # Start empty
            font_size=16,
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            adaptive_size=True,
            opacity=0  # Start hidden
        )
        self.add_widget(self.screenshot_feedback)
        
        # Add FPS counter
        self.fps_label = MDLabel(
            text="0 FPS",
            font_size=14,
            color=(1, 1, 1, 1),
            halign="right",
            valign="top",
            adaptive_size=True,
            opacity=0  # Start hidden
        )
        
        self.add_widget(self.fps_label)
        
        # Initialize FPS tracking
        self.fps_counter = 0
        self.fps_time = 0
        self.fps_update_interval = 0.5  # Update every half second
        
        # Start FPS update
        Clock.schedule_interval(self.update_fps, 0)  # Update every frame
        
        # Update positions when window resizes
        # Window.bind(on_resize=self._on_resize)
        Clock.schedule_once(self.fade_initial_help, 1.5)
    
    # def _on_resize(self, instance, width, height):
    #     """Handle window resize events"""
    #     self.initial_help.pos = (self.margin, self.margin)
    #     self.commands.pos = (self.margin, self.margin)
        
    def _update_positions(self, *args):
        """Update positions of all labels"""
        # Update FPS counter position (top right)
        self.fps_label.pos = (Window.width - self.fps_label.width - 10, 
                             Window.height - self.fps_label.height - 10)
        
    def fade_initial_help(self, dt):
        anim = Animation(opacity=0, duration=1)
        anim.start(self.initial_help)
    
    def toggle_overlay(self):
        # If showing commands, ensure initial help is hidden
        if self.commands.opacity == 0:
            self.initial_help.opacity = 0
        
        target_opacity = 0 if self.commands.opacity > 0 else 1
        anim = Animation(opacity=target_opacity, duration=0.3)
        anim.start(self.commands)
        anim.start(self.fps_label)

    def show_screenshot_message(self, success=True):
        """Show screenshot feedback message"""
        self.screenshot_feedback.text = "Screenshot saved!" if success else "Screenshot failed!"
        self.screenshot_feedback.opacity = 1
        
        # Center screenshot feedback at top
        self.screenshot_feedback.pos = (
            (Window.width - self.screenshot_feedback.width) / 2,
            Window.height
        )
        
        # Schedule fadeout
        def fadeout(dt):
            self.screenshot_feedback.opacity = 0
        Clock.schedule_once(fadeout, 2)
        
    def update_fps(self, dt):
        """Update FPS counter"""
        self.fps_counter += 1
        self.fps_time += dt
        
        if self.fps_time >= self.fps_update_interval:
            fps = int(self.fps_counter / self.fps_time)
            self.fps_label.text = f"{fps} FPS"
            self._update_positions()  # Update position in case text width changed
            
            # Reset counters
            self.fps_counter = 0
            self.fps_time = 0
