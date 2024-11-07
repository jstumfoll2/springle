"""
Springle - Interactive Particle Animation System
Developed with assistance from Claude AI (Anthropic)
Copyright (c) 2024 Jason Stumfoll
"""

import pygame
import pygame_gui
from datetime import datetime
import os

from OrbitGroup import OrbitGroup
from SpringleCircle import SpringleCircle
from FPSCounter import FPSCounter
from springle_params import SpringleParams

class Springle:
    # Default parameter values
    DEFAULT_VALUES = {
        'min_circles': 4,
        'max_circles': 12,
        'angular_acceleration': 0.5,
        'radial_acceleration': 3,
        'starting_angular_velocity': 1.0,
        'starting_radial_velocity': 25,
        'base_size': 20,
        'fade_duration': 5.0,
        'max_alpha': 200,
        'trail_spacing': 0.5,
        'color_transition_speed': 0.2,
        'max_groups': 10,
        'spawn_cooldown': 2.5
    }

    def __init__(self, width=1080, height=1080):
        """Initialize the Springle application."""
        self.width = width
        self.height = height
        self.running = True
        self.paused = False
        self.auto_generate_groups = True
        self.show_options = False  # Track options menu visibility
        
        # Initialize Pygame
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Springle")
        
        # Initialize UI
        self.manager = pygame_gui.UIManager((width, height), 'data/themes/theme.json')
        
        # Create options panel (hidden initially)
        self.create_options_panel()
        
        # Initialize game components
        self.fps_counter = FPSCounter()
        self.circle_system = SpringleCircle(
            self.DEFAULT_VALUES['min_circles'],
            self.DEFAULT_VALUES['max_circles'],
            self.DEFAULT_VALUES['starting_radial_velocity'],
            self.DEFAULT_VALUES['starting_angular_velocity'],
            self.DEFAULT_VALUES['angular_acceleration'],
            self.DEFAULT_VALUES['radial_acceleration'],
            self.DEFAULT_VALUES['base_size'],
            width, height
        )
        
        # Update circle system's color transition speed from default values
        self.circle_system.color_transition_speed = self.DEFAULT_VALUES['color_transition_speed']
        
        # Game state
        self.mouse_button_pressed = False
        self.clock = pygame.time.Clock()
        
        # Create fonts
        if not hasattr(pygame, 'mouse_pos_font'):
            pygame.mouse_pos_font = pygame.font.Font(None, 24)
        self.screenshot_font = pygame.font.Font(None, 20)
            
    def create_options_panel(self):
        """Create the collapsible options panel."""
        panel_width = 300
        panel_height = self.height
        
        # Calculate centered position within panel
        control_width = 260  # Width of controls
        left_margin = (panel_width - control_width) // 2
        
        # Create main options panel
        self.options_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(-panel_width, 0, panel_width, panel_height),
            manager=self.manager
        )
        
        # Add title to panel
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, panel_width-20, 20),
            text='Options Menu (Press O to toggle)',
            manager=self.manager,
            container=self.options_panel
        )
        
        # Create all controls directly in the panel
        self.create_controls(left_margin, control_width)
        
        # Create status bar at bottom
        self.group_counter = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, panel_height-40, panel_width-20, 30),
            text='Active Groups: 0 / 0',
            manager=self.manager,
            container=self.options_panel
        )
        
        # Hide panel initially
        self.options_panel.hide()

    def create_controls(self, left_margin, control_width):
        """Create all sliders and buttons within the options container."""
        self.sliders = {}
        self.buttons = {}
        
        # Y position tracker for positioning elements
        y_pos = 35  # Start after title
        
        # Create sliders with more compact spacing
        slider_configs = [
            ('min_circles', 'Min Circles per Group', (1, 20)),
            ('max_circles', 'Max Circles per Group', (1, 20)),
            ('angular_acceleration', 'Angular Acceleration', (-200, 200)),
            ('radial_acceleration', 'Radial Acceleration', (-200, 200)),
            ('starting_angular_velocity', 'Starting Rotation Speed', (-1000, 1000)),
            ('starting_radial_velocity', 'Starting Radial Speed', (-1000, 1000)),
            ('base_size', 'Base Circle Size', (2, 100)),
            ('fade_duration', 'Fade Duration (seconds)', (1.0, 30.0)),
            ('max_alpha', 'Max Trail Alpha', (0, 255)),
            ('trail_spacing', 'Trail Point Spacing', (0.0, 1.0), 0.05),
            ('color_transition_speed', 'Color Transition Speed', (0.0, 1.0), 0.05),
            ('max_groups', 'Maximum Groups', (1, 20)),
            ('spawn_cooldown', 'Spawn Cooldown (seconds)', (0.5, 10.0), 0.5)
        ]
        
        # Create sliders with adjusted spacing
        for config in slider_configs:
            name, label, value_range = config[:3]
            click_increment = config[3] if len(config) > 3 else 1
            
            # Add label with increased height
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(left_margin, y_pos, control_width, 20),  # Increased from 15 to 20
                text=label,
                manager=self.manager,
                container=self.options_panel
            )
            y_pos += 22  # Increased from 18 to 22 to accommodate larger label height
            
            # Add slider
            self.sliders[name] = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(left_margin, y_pos, control_width, 20),
                start_value=self.DEFAULT_VALUES[name],
                value_range=value_range,
                click_increment=click_increment,
                manager=self.manager,
                container=self.options_panel
            )
            y_pos += 28  # Increased from 25 to 28 for better spacing
        
        # Add spacing before buttons
        y_pos += 10  # Increased from 5 to 10
        
        # Create buttons with adjusted spacing
        button_configs = [
            ('clear_trails', 'Clear Trails'),
            ('new_group', 'Create New Group'),
            ('clear_groups', 'Clear All Groups'),
            ('reset', 'Reset All Settings'),
            ('pause', 'Pause'),
            ('toggle_auto_generate', 'Toggle Auto Generation')
        ]
        
        # Create buttons with adjusted height
        for name, text in button_configs:
            self.buttons[name] = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(left_margin, y_pos, control_width, 30),  # Increased from 25 to 30
                text=text,
                manager=self.manager,
                container=self.options_panel
            )
            y_pos += 35  # Increased from 28 to 35 for better button spacing
        
    def toggle_options_menu(self):
        """Toggle the visibility of the options menu."""
        self.show_options = not self.show_options
        
        if self.show_options:
            # Show panel with animation
            self.options_panel.show()
            target_x = 0
        else:
            # Hide panel with animation
            target_x = -self.options_panel.rect.width
        
        # Animate panel position
        current_x = self.options_panel.rect.x
        distance = target_x - current_x
        steps = 10
        
        for i in range(steps + 1):
            progress = i / steps
            new_x = current_x + (distance * progress)
            self.options_panel.set_position(pygame.Vector2(new_x, 0))
            self.manager.update(0.016)  # ~60fps
            self.draw()
        
        if not self.show_options:
            self.options_panel.hide()

    def handle_events(self):
        """Process all game events."""
        events = pygame.event.get()
        
        # Check for UI element interactions first
        ui_hover = False
        for event in events:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                # Check if mouse is over any UI element
                ui_hover = self.manager.get_hovering_any_element()
                break
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.take_screenshot()
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif event.key == pygame.K_o:
                    self.toggle_options_menu()
            
            # Handle mouse events if not over UI
            if not ui_hover:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.mouse_button_pressed = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.mouse_button_pressed = False
            
            # Always process UI events
            self.handle_ui_event(event)
            self.manager.process_events(event)
        
    def handle_ui_event(self, event):
        """Handle UI-specific events."""
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            for name, slider in self.sliders.items():
                if event.ui_element == slider:
                    self.DEFAULT_VALUES[name] = event.value
                    if name == 'color_transition_speed':
                        self.circle_system.color_transition_speed = event.value
                    break
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.buttons['clear_trails']:
                self.clear_trails()
            elif event.ui_element == self.buttons['new_group']:
                self.create_new_group()
            elif event.ui_element == self.buttons['clear_groups']:
                self.clear_groups()
            elif event.ui_element == self.buttons['reset']:
                self.reset_settings()
            elif event.ui_element == self.buttons['pause']:
                self.toggle_pause()
            elif event.ui_element == self.buttons['toggle_auto_generate']:
                self.toggle_auto_generate()

    def toggle_pause(self):
        """Toggle the pause state."""
        self.paused = not self.paused
        # Update pause button text
        self.buttons['pause'].set_text('Resume' if self.paused else 'Pause')

    def toggle_auto_generate(self):
        """Toggle automatic group generation."""
        self.auto_generate_groups = not self.auto_generate_groups
        # Update button text
        self.buttons['toggle_auto_generate'].set_text(
            'Enable Auto Generation' if not self.auto_generate_groups else 'Disable Auto Generation'
        )

    def clear_trails(self):
        """Clear all trail points."""
        for group in self.circle_system.groups:
            for circle in group.circles:
                circle['trail'] = []
                circle['last_trail_pos'] = None

    def create_new_group(self):
        """Create a new orbit group."""
        active_groups = sum(1 for group in self.circle_system.groups if group.active)
        if active_groups < self.DEFAULT_VALUES['max_groups']:
            new_group = OrbitGroup(
                self.DEFAULT_VALUES['min_circles'],
                self.DEFAULT_VALUES['max_circles'],
                0,
                self.DEFAULT_VALUES['base_size'],
                self.DEFAULT_VALUES['starting_radial_velocity'],
                self.DEFAULT_VALUES['starting_angular_velocity'],
                self.DEFAULT_VALUES['radial_acceleration'],
                self.DEFAULT_VALUES['angular_acceleration'],
                False
            )
            self.circle_system.groups.append(new_group)

    def clear_groups(self):
        """Clear all groups and create a new one."""
        # Replace all groups with new one
        self.circle_system.groups = []
        self.create_new_group()

    def reset_settings(self):
        """Reset all settings to their default values."""
        # Store original default values
        original_defaults = {
            'min_circles': 4,
            'max_circles': 12,
            'angular_acceleration': 0.5,
            'radial_acceleration': 3,
            'starting_angular_velocity': 1.5,
            'starting_radial_velocity': 100,
            'base_size': 20,
            'fade_duration': 2.0,
            'max_alpha': 200,
            'trail_spacing': 0.5,
            'color_transition_speed': 0.2,
            'max_groups': 7
        }
        
        # Reset all values and update sliders
        for name, value in original_defaults.items():
            self.DEFAULT_VALUES[name] = value
            if name in self.sliders:
                self.sliders[name].set_current_value(value)
        
        # Update circle system properties that depend on these values
        self.circle_system.color_transition_speed = original_defaults['color_transition_speed']
        
        # Update button states
        self.buttons['pause'].set_text('Pause')
        self.buttons['toggle_auto_generate'].set_text('Disable Auto Generation')
        
        # Reset states
        self.paused = False
        self.auto_generate_groups = True

    def update(self, time_delta):
        """Update game state."""
        self.manager.update(time_delta)
        
        if not self.paused:
            current_mouse_pos = pygame.mouse.get_pos()
            
            # Manage group limits
            if len(self.circle_system.groups) > self.DEFAULT_VALUES['max_groups']:
                # Remove oldest non-mouse groups first
                for group in self.circle_system.groups[:]:
                    if not group.is_mouse_group:
                        self.circle_system.groups.remove(group)
                        if len(self.circle_system.groups) <= self.DEFAULT_VALUES['max_groups']:
                            break
            
            # Update spawn cooldown in circle system
            self.circle_system.spawn_cooldown_start = self.DEFAULT_VALUES['spawn_cooldown']
            
            # Create parameters object with current values
            params = SpringleParams(
                min_circles=self.DEFAULT_VALUES['min_circles'],
                max_circles=self.DEFAULT_VALUES['max_circles'],
                radial_velocity=self.DEFAULT_VALUES['starting_radial_velocity'],
                angular_velocity=self.DEFAULT_VALUES['starting_angular_velocity'],
                radial_acceleration=self.DEFAULT_VALUES['radial_acceleration'],
                angular_acceleration=self.DEFAULT_VALUES['angular_acceleration'],
                base_size=self.DEFAULT_VALUES['base_size'],
                mouse_button_pressed=self.mouse_button_pressed,
                mouse_pos=current_mouse_pos,
                fade_duration=self.DEFAULT_VALUES['fade_duration'],
                space_factor=self.DEFAULT_VALUES['trail_spacing'],
                auto_generate=self.auto_generate_groups
            )
        
            # Update circle system with parameter object
            self.circle_system.update(time_delta, params)
            
            # Update group counter
            active_groups = sum(1 for group in self.circle_system.groups if group.active)
            self.group_counter.set_text(
                f'Active Groups: {active_groups} / {self.DEFAULT_VALUES["max_groups"]}'
            )

    def draw(self):
        """Draw the game state."""
        self.screen.fill((0, 0, 0))
        
        # Draw circle system
        self.circle_system.draw(self.screen, self.DEFAULT_VALUES['max_alpha'])
        
        # Draw mouse position
        self.draw_mouse_position()
        
        # Draw FPS counter
        self.fps_counter.draw(self.screen)
        
        # Draw instruction texts
        self.draw_instruction_texts()
        
        # Draw pause indicator if paused
        if self.paused:
            self.draw_pause_indicator()
        
        # Draw UI
        self.manager.draw_ui(self.screen)
        
        pygame.display.flip()

    def draw_instruction_texts(self):
        """Draw all instruction texts."""
        texts = [
            ('Press "s" to save screenshot', 'bottomleft', (10, self.height - 10)),
            ('Press "o" to toggle options', 'bottomleft', (10, self.height - 30)),
            ('Press "space" to pause', 'bottomleft', (10, self.height - 50))
        ]
        
        for text, anchor, pos in texts:
            text_surface = self.screenshot_font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            setattr(text_rect, anchor, pos)
            self.screen.blit(text_surface, text_rect)

    def draw_mouse_position(self):
        """Draw the current mouse position."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        centered_x = mouse_x - (self.width // 2)
        centered_y = (self.height // 2) - mouse_y
        
        mouse_pos_text = f"Mouse: ({centered_x}, {centered_y})"
        text_surface = pygame.mouse_pos_font.render(mouse_pos_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (self.width - 10, self.height - 10)
        self.screen.blit(text_surface, text_rect)

    def draw_pause_indicator(self):
        """Draw the pause indicator when game is paused."""
        pause_text = self.screenshot_font.render('PAUSED', True, (255, 255, 255))
        text_rect = pause_text.get_rect()
        text_rect.center = (self.width // 2, 30)
        self.screen.blit(pause_text, text_rect)
        
    def take_screenshot(self):
        """Take a screenshot of the current screen."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"springle_{timestamp}.png"
        filepath = os.path.join(".", filename)
        pygame.image.save(self.screen, filepath)
        print(f"Screenshot saved: {filepath}")
    
    def run(self):
        """Main game loop."""
        while self.running:
            time_delta = self.clock.tick(60)/1000.0
            
            self.handle_events()
            self.update(time_delta)
            self.draw()
            
            # Update FPS counter
            self.fps_counter.update(time_delta)

def main():
    """Entry point for the application."""
    springle = Springle()
    springle.run()
    pygame.quit()

if __name__ == '__main__':
    main()