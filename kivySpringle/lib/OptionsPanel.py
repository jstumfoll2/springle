
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.button import MDRaisedButton

from kivy.clock import Clock

from lib.ScrollableOptionsPanel import ScrollableOptionsPanel

class OptionsPanel(MDBoxLayout):
    def __init__(self, springle_widget, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        self.springle_widget = springle_widget
        
        # Create content layout
        self.content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True  # Important for scrolling
        )
        
        # Title
        self.content.add_widget(MDLabel(
            text="Options Menu (Press O to toggle)",
            theme_text_color="Primary",
            font_style="H6",
            adaptive_height=True
        ))
        
        # Create sliders
        self.create_sliders()
        
        # Create buttons
        self.create_buttons()
        
        # Create status label
        self.status_label = MDLabel(
            text="Active Groups: 0 / 0",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        self.content.add_widget(self.status_label)
        
        # Create scroll view and add content
        self.scroll = ScrollableOptionsPanel()
        self.scroll.add_widget(self.content)
        self.add_widget(self.scroll)
        
        # Start update timer for status
        Clock.schedule_interval(self.update_status, 1.0)

    def create_sliders(self):
        sliders_config = [
            ('min_circles', 'Min Circles per Group', 1, 20),
            ('max_circles', 'Max Circles per Group', 1, 20),
            ('angular_acceleration', 'Angular Acceleration', -200, 200),
            ('radial_acceleration', 'Radial Acceleration', -200, 200),
            ('angular_velocity', 'Rotation Speed', -1000, 1000),
            ('radial_velocity', 'Radial Speed', -1000, 1000),
            ('base_size', 'Base Circle Size', 2, 200),
            ('fade_duration', 'Fade Duration', 1.0, 30.0),
            ('max_alpha', 'Max Trail Alpha', 0, 255),
            ('space_factor', 'Trail Point Spacing', 0.0, 1.0),
            ('gradient_sharpness', 'Circle Edge Sharpness', 0.5, 12.0),
        ]
        
        for name, text, min_val, max_val in sliders_config:
            container = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                spacing=dp(4),
                size_hint_y=None,
                height=dp(50)  # Fixed height for container
            )
            
            # Label with value display
            label_box = MDBoxLayout(
                adaptive_height=True,
                spacing=dp(10)
            )
            
            label = MDLabel(
                text=text,
                theme_text_color="Secondary",
                adaptive_height=True,
                size_hint_x=0.7
            )
            value_label = MDLabel(
                text=str(getattr(self.springle_widget.params, name)),
                theme_text_color="Secondary",
                adaptive_height=True,
                size_hint_x=0.3,
                halign='right'
            )
            
            label_box.add_widget(label)
            label_box.add_widget(value_label)
            container.add_widget(label_box)
            
            # Slider
            slider = MDSlider(
                min=min_val,
                max=max_val,
                value=getattr(self.springle_widget.params, name),
                size_hint_y=None,
                height=dp(20)
            )
            
            # Update value label when slider changes
            def make_value_updater(value_label, name):
                def update_value(instance, value):
                    self.on_slider_change(name, value)
                    value_label.text = f"{value:.1f}"
                return update_value
            
            slider.bind(value=make_value_updater(value_label, name))
            container.add_widget(slider)
            self.content.add_widget(container)

    def create_buttons(self):
        buttons_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            adaptive_height=True,
            padding=[0, dp(10), 0, dp(10)]
        )
        
        buttons_config = [
            ('clear_trails', 'Clear Trails', self.clear_trails),
            ('new_group', 'Create New Group', self.create_new_group),
            ('clear_groups', 'Clear All Groups', self.clear_groups),
            ('pause', 'Pause', self.toggle_pause),
            ('auto_generate', 'Toggle Auto Generation', self.toggle_auto_generate),
        ]
        
        for name, text, callback in buttons_config:
            button = MDRaisedButton(
                text=text,
                on_release=callback,
                size_hint_x=1,
            )
            setattr(self, f'{name}_button', button)
            buttons_container.add_widget(button)
            
        self.content.add_widget(buttons_container)

    def on_slider_touch(self, instance, touch):
        """Handle slider touch events"""
        if instance.collide_point(*touch.pos):
            # If touch is on slider, stop event propagation
            return True
        return False
    
    def on_slider_change(self, name, value):
        setattr(self.springle_widget.params, name, value)

    def clear_trails(self, *args):
        if self.springle_widget.circle_system:
            self.springle_widget.circle_system.fading_trails = []
            for group in self.springle_widget.circle_system.groups:
                for circle in group.circles:
                    circle['trail'] = []
                    circle['last_trail_pos'] = None

    def create_new_group(self, *args):
        if self.springle_widget.circle_system:
            params = self.springle_widget.params
            new_group = self.springle_widget.circle_system.create_new_group(
                params.min_circles,
                params.max_circles,
                params.radial_velocity,
                params.angular_velocity,
                params.base_size
            )

    def clear_groups(self, *args):
        self.springle_widget.clear_groups()

    def toggle_pause(self, *args):
        self.springle_widget.toggle_pause()
        self.update_pause_button(self.springle_widget.paused)

    def toggle_auto_generate(self, *args):
        self.springle_widget.auto_generate = not self.springle_widget.auto_generate
        self.auto_generate_button.text = (
            'Enable Auto Generation' if not self.springle_widget.auto_generate 
            else 'Disable Auto Generation'
        )

    def update_pause_button(self, paused):
        self.pause_button.text = 'Resume' if paused else 'Pause'

    def update_status(self, dt):
        if self.springle_widget.circle_system:
            active_groups = sum(1 for g in self.springle_widget.circle_system.groups if g.active)
            max_groups = self.springle_widget.circle_system.max_groups
            self.status_label.text = f'Active Groups: {active_groups} / {max_groups}'
