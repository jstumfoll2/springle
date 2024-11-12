from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.pickers import MDColorPicker

from kivy.clock import Clock
from functools import partial
from typing import Union

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
            adaptive_height=True
        )
        
        # Title
        self.content.add_widget(MDLabel(
            text="Options Menu (Press O to toggle)",
            theme_text_color="Primary",
            font_style="H6",
            adaptive_height=True
        ))
        
        # Define all slider configurations
        self.slider_configs = [
            ('min_circles', 'Min Circles per Group', 1, 20, True),  # Integer
            ('max_circles', 'Max Circles per Group', 1, 20, True),  # Integer
            ('angular_acceleration', 'Angular Acceleration', -200, 200, False),
            ('radial_acceleration', 'Radial Acceleration', -200, 200, False),
            ('angular_velocity', 'Starting Rotation Speed', -1000, 1000, False),
            ('radial_velocity', 'Starting Radial Speed', -1000, 1000, False),
            ('base_size', 'Base Circle Size', 2, 100, False),
            ('fade_duration', 'Fade Duration (seconds)', 1.0, 30.0, False),
            ('max_alpha', 'Max Trail Alpha', 0, 255, True),  # Integer
            ('space_factor', 'Trail Point Spacing', 0.1, 10.0, False),
            ('color_transition_speed', 'Color Transition Speed', 0.0, 1.0, False),
            ('max_groups', 'Maximum Groups', 1, 20, True),  # Integer
            ('spawn_cooldown', 'Spawn Cooldown (seconds)', 0.5, 10.0, False)
        ]
        
        # Create sliders
        self.sliders = {}
        self.value_labels = {}
        self.create_sliders()
        
        # Create buttons
        self.create_buttons()
        
        # Initialize color picker dialog
        self.color_dialog = None
        self.current_color = [185/255, 150/255, 234/255, 1]  # Default purple
        
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
        """Create all sliders with proper formatting and labels"""
        for name, text, min_val, max_val, is_integer in self.slider_configs:
            container = MDBoxLayout(
                orientation='vertical',
                adaptive_height=True,
                spacing=dp(4),
                size_hint_y=None,
                height=dp(50)
            )
            
            # Label box with value display
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
            
            # Format initial value based on type
            initial_value = getattr(self.springle_widget.params, name)
            if is_integer:
                value_text = str(int(initial_value))
            else:
                value_text = f"{initial_value:.2f}"
                
            value_label = MDLabel(
                text=value_text,
                theme_text_color="Secondary",
                adaptive_height=True,
                size_hint_x=0.3,
                halign='right'
            )
            
            self.value_labels[name] = value_label
            
            label_box.add_widget(label)
            label_box.add_widget(value_label)
            container.add_widget(label_box)
            
            # Create slider with proper step value
            step = 1.0 if is_integer else (0.05 if max_val <= 1 else 0.5)
            slider = MDSlider(
                min=min_val,
                max=max_val,
                value=initial_value,
                step=step,
                size_hint_y=None,
                height=dp(20)
            )
            
            # Create value updater function
            def make_value_updater(name, value_label, is_integer):
                def update_value(instance, value):
                    if is_integer:
                        value = int(value)
                        value_label.text = str(value)
                    else:
                        value_label.text = f"{value:.2f}"
                    self.on_slider_change(name, value)
                return update_value
            
            slider.bind(value=make_value_updater(name, value_label, is_integer))
            self.sliders[name] = slider
            container.add_widget(slider)
            self.content.add_widget(container)

    def on_slider_change(self, name, value):
        """Handle slider value changes"""
        if name in ['min_circles', 'max_circles', 'max_groups', 'max_alpha']:
            value = int(value)
        setattr(self.springle_widget.params, name, value)
        
        # Handle special cases
        if name == 'min_circles' or name == 'max_circles':
            # Ensure min <= max
            min_val = self.sliders['min_circles'].value
            max_val = self.sliders['max_circles'].value
            if name == 'min_circles' and min_val > max_val:
                self.sliders['max_circles'].value = min_val
            elif name == 'max_circles' and max_val < min_val:
                self.sliders['min_circles'].value = max_val
                
    def create_buttons(self):
        """Create control buttons"""
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
            ('color_picker', 'Change Background Color', self.show_color_picker),  # Added color picker button
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

    def clear_trails(self, *args):
        if self.springle_widget.circle_system:
            self.springle_widget.circle_system.trail_store.clear_all()

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
        self.springle_widget.circle_system.clear_trails()

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

    def show_color_picker(self, *args):
        """Show the color picker dialog"""
        color_picker = MDColorPicker(
            size_hint=(0.85, 0.85)
        )
        color_picker.bind(
            on_select_color=self.on_select_color,
            on_release=self.close_color_picker
        )
        self.color_dialog = color_picker
        self.color_dialog.open()

    def on_select_color(self, instance, color):
        """Handle color selection"""
        self.current_color = color
        if hasattr(self.springle_widget, 'set_background_color'):
            self.springle_widget.set_background_color(color)


    def close_color_picker(self,
                            instance_color_picker: MDColorPicker,
                            type_color: str,
                            selected_color: Union[list, str]):
        self.current_color = selected_color
        if hasattr(self.springle_widget, 'set_background_color'):
            self.springle_widget.set_background_color(selected_color)

        # Close the dialog
        if self.color_dialog:
            self.color_dialog.dismiss()
            self.color_dialog = None
        
    def update_status(self, dt):
        if self.springle_widget.circle_system:
            active_groups = sum(1 for g in self.springle_widget.circle_system.groups if g.active)
            max_groups = self.springle_widget.circle_system.max_groups
            self.status_label.text = f'Active Groups: {active_groups} / {max_groups}'
            