import pygame
import pygame_gui
from pygame_gui.windows import UIColourPickerDialog

class BackgroundColorManager:
    def __init__(self, manager, options_panel, left_margin, control_width):
        self.manager = manager
        self.color_picker = None
        self.current_color = pygame.Color(185,150,234)
        
        # Calculate button dimensions
        display_width = control_width - 100
        button_width = 90
        button_height = 30
        
        # Create color display button using themed style
        self.color_display = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(left_margin, 0, display_width, button_height),
            text='#b996ea',
            manager=manager,
            container=options_panel,
            object_id='@color_display',
            allow_double_clicks=False
        )
        
        # Create color picker button
        self.color_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(left_margin + display_width + 10, 0, button_width, button_height),
            text='Pick Color',
            manager=manager,
            container=options_panel,
            allow_double_clicks=False
        )
        
        # Set initial colors
        self.update_color_display()
    
    def update_color_display(self):
        """Update the color display button with current color."""
        hex_color = f'#{self.current_color.r:02x}{self.current_color.g:02x}{self.current_color.b:02x}'
        self.color_display.set_text(hex_color)
        
        # Calculate text color based on background brightness
        brightness = (self.current_color.r + self.current_color.g + self.current_color.b) / 3
        text_color = pygame.Color(255, 255, 255) if brightness < 128 else pygame.Color(0, 0, 0)
        
        # Create a theme dictionary with proper Color objects
        colours = {
            'normal_bg': pygame.Color(self.current_color),
            'hovered_bg': pygame.Color(self.current_color),
            'active_bg': pygame.Color(self.current_color),
            'selected_bg': pygame.Color(self.current_color),
            'normal_text': text_color,
            'hovered_text': text_color,
            'active_text': text_color,
            'selected_text': text_color
        }
        
        # Update only the dynamic colors
        self.color_display.colours.update(colours)
        self.color_display.rebuild()
    
    def handle_event(self, event):
        """Handle UI events for the color picker."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.color_button and not self.color_picker:
                self.color_picker = UIColourPickerDialog(
                    rect=pygame.Rect((self.manager.get_root_container().get_rect().width - 390) // 2,
                                   (self.manager.get_root_container().get_rect().height - 390) // 2,
                                   390, 390),
                    manager=self.manager,
                    initial_colour=self.current_color,
                    window_title='Choose Background Color'
                )
        
        elif event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            self.current_color = event.colour
            self.update_color_display()
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.color_picker:
                self.color_picker = None
    
    def get_color(self):
        """Get the current background color as a tuple."""
        return (self.current_color.r, self.current_color.g, self.current_color.b)