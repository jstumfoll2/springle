from kivymd.uix.widget import MDWidget
from kivymd.uix.label import MDLabel

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.animation import Animation

class TextOverlay(MDWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create fonts and text styling properties
        self.font_size = '14sp'
        self.command_spacing = dp(4)
        
        # Initial help label
        self.initial_help = MDLabel(
            text='Press \'q\' to enable text overlay',
            font_size=self.font_size,
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
            font_size=self.font_size,
            halign="left",
            valign="bottom",
            adaptive_size=True,
            color=(1, 1, 1, 1),
            opacity=0
        )
        self.add_widget(self.commands)
        
        # Mouse position label (new)
        self.mouse_pos_label = MDLabel(
            text="Mouse: (0, 0)",
            font_size=self.font_size,
            halign="right",
            valign="bottom",
            adaptive_size=True,
            color=(1, 1, 1, 1),
            opacity=0
        )
        self.add_widget(self.mouse_pos_label)
        
        # Screenshot feedback label
        self.screenshot_feedback = MDLabel(
            text="",
            font_size='16sp',
            color=(1, 1, 1, 1),
            halign="center",
            valign="top",
            adaptive_size=True,
            opacity=0
        )
        self.add_widget(self.screenshot_feedback)
        
        # FPS counter
        self.fps_label = MDLabel(
            text="0 FPS",
            font_size=self.font_size,
            color=(1, 1, 1, 1),
            halign="right",
            valign="top",
            adaptive_size=True,
            opacity=0
        )
        self.add_widget(self.fps_label)
        
        # Initialize FPS tracking
        self.fps_counter = 0
        self.fps_time = 0
        self.fps_update_interval = 0.5  # Update every half second
        
        # Start FPS update and position update
        Clock.schedule_interval(self.update_fps, 0)
        # Clock.schedule_interval(self._update_positions, 1/30)  # 30fps for position updates
        
        # Initial fade out timer
        Clock.schedule_once(self.fade_initial_help, 1.5)
        
        # Bind to window resize
        Window.bind(on_resize=self._on_resize)
        self._update_positions(0)
    
    def _on_resize(self, instance, width, height):
        """Handle window resize events"""
        self._update_positions(0)
    
    def _update_positions(self, dt):
        """Update positions of all labels"""
        margin = dp(10)
        
        # Update initial help position (bottom left)
        self.initial_help.pos = (margin, margin)
        
        # Update command list position (bottom left)
        self.commands.pos = (margin, margin)
        
        # Update FPS counter position (top right)
        self.fps_label.pos = (Window.width - self.fps_label.width - margin, 
                             Window.height - self.fps_label.height - margin)
        
        # Update mouse position label (bottom right)
        self.mouse_pos_label.pos = (Window.width - self.mouse_pos_label.width - margin,
                                   margin)
        
        # Update screenshot feedback position (top center)
        if self.screenshot_feedback.opacity > 0:
            self.screenshot_feedback.pos = (
                (Window.width - self.screenshot_feedback.width) / 2,
                Window.height - self.screenshot_feedback.height - margin
            )
    
    def update_mouse_pos(self, x, y):
        """Update the mouse position display with relative coordinates"""
        self.mouse_pos_label.text = f"Mouse: ({int(x)}, {int(y)})"
        # Force position update on text change
        # self.mouse_pos_label.texture_update()  # Force texture update
        # self._update_positions(0)
    
    def fade_initial_help(self, dt):
        """Fade out the initial help text"""
        anim = Animation(opacity=0, duration=1)
        anim.start(self.initial_help)
        self._update_positions(0)
    
    def toggle_overlay(self):
        """Toggle visibility of the command list and related elements"""
        # If showing commands, ensure initial help is hidden
        if self.commands.opacity == 0:
            self.initial_help.opacity = 0
        
        # Target opacity for animation
        target_opacity = 0 if self.commands.opacity > 0 else 1
        
        # Create animations for all elements
        duration = 0.3
        for widget in [self.commands, self.fps_label, self.mouse_pos_label]:
            anim = Animation(opacity=target_opacity, duration=duration)
            anim.start(widget)

    def show_screenshot_message(self, success=True):
        """Show screenshot feedback message with animation"""
        self.screenshot_feedback.text = "Screenshot saved!" if success else "Screenshot failed!"
        
        # Reset position and show message
        # self._update_positions(0)
        
        # Create fade in and out animation
        fade_in = Animation(opacity=1, duration=0.3)
        fade_out = Animation(opacity=0, duration=0.3)
        
        # Chain animations with delay
        fade_in.bind(on_complete=lambda *args: Clock.schedule_once(
            lambda dt: fade_out.start(self.screenshot_feedback), 1.5
        ))
        
        # Start animation sequence
        fade_in.start(self.screenshot_feedback)
        
    def update_fps(self, dt):
        """Update FPS counter"""
        self.fps_counter += 1
        self.fps_time += dt
        
        if self.fps_time >= self.fps_update_interval:
            fps = int(self.fps_counter / self.fps_time)
            self.fps_label.text = f"{fps} FPS"
            
            # Reset counters
            self.fps_counter = 0
            self.fps_time = 0
            
            # Update positions after text change
            # self._update_positions(0)
