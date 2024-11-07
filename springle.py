"""
Springle - Interactive Particle Animation System
Developed with assistance from Claude AI (Anthropic)
Copyright (c) 2024 Jason Stumfoll

This file was created with the help of Claude AI, providing guidance on
implementation, optimization, and best practices. All code has been reviewed
and tested by human developers.
"""

import pygame
import pygame_gui
from datetime import datetime
import os

from OrbitGroup import OrbitGroup
from SpringleCircle import SpringleCircle  # Update import to use the class
from FPSCounter import FPSCounter

# Add screenshot function
def take_screenshot(screen):
    """Take a screenshot of the current screen."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"springle_{timestamp}.png"
    filepath = os.path.join(".\\", filename)
    pygame.image.save(screen, filepath)
    print(f"Screenshot saved: {filepath}")
    
# Initialize Pygame
pygame.init()

# Create font
if not hasattr(pygame, 'mouse_pos_font'):
    pygame.mouse_pos_font = pygame.font.Font(None, 24)
screenshot_font = pygame.font.Font(None, 20)

# Set up the display
WIDTH = 1080
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Springle")

# Initialize UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Initialize fps counter
fps_counter = FPSCounter()

# Initial parameters
MIN_CIRCLES = 4
MAX_CIRCLES = 12
ANGULAR_ACCELERATION = 0.5
RADIAL_ACCELERATION = 3
START_ANGULAR_VELOCITY = 1.5
START_RADIAL_VELOCITY = 100
BASE_SIZE = 20
FADE_DURATION = 2.0
MAX_ALPHA = 200  # New parameter for max trail alpha
TRAIL_SPACING_FACTOR = 0.5

# First, define original/default values at the start of program, after the WIDTH/HEIGHT definitions
DEFAULT_VALUES = {
    'min_circles': MIN_CIRCLES, 
    'max_circles': MAX_CIRCLES,  
    'angular_acceleration': ANGULAR_ACCELERATION,
    'radial_acceleration': RADIAL_ACCELERATION, 
    'starting_angular_velocity': START_ANGULAR_VELOCITY,  
    'starting_radial_velocity': START_RADIAL_VELOCITY,  
    'base_size': BASE_SIZE, 
    'fade_duration': FADE_DURATION, 
    'max_alpha': MAX_ALPHA,
    'trail_spacing': TRAIL_SPACING_FACTOR
}

# Create UI elements
min_circles_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 20), (200, 20)),
    start_value=MIN_CIRCLES,
    value_range=(1, 20),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 5), (200, 20)),
    text='Min Circles per Group',
    manager=manager
)

max_circles_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 70), (200, 20)),
    start_value=MAX_CIRCLES,
    value_range=(1, 20),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 55), (200, 20)),
    text='Max Circles per Group',
    manager=manager
)

expansion_rate_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 120), (200, 20)),
    start_value=ANGULAR_ACCELERATION,
    value_range=(-200, 200),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 105), (200, 20)),
    text='Angular Acceleration',
    manager=manager
)

radial_acceleration_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 170), (200, 20)),
    start_value=RADIAL_ACCELERATION,
    value_range=(-200.0, 200.0),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 155), (200, 20)),
    text='Radial Acceleration',
    manager=manager
)

angular_velocity_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 220), (200, 20)),
    start_value=START_ANGULAR_VELOCITY,
    value_range=(-1000, 1000),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 205), (200, 20)),
    text='Starting Rotation Speed',
    manager=manager
)


radial_velocity_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 270), (200, 20)),
    start_value=START_RADIAL_VELOCITY,
    value_range=(-1000, 1000),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 255), (200, 20)),
    text='Starting Radial Speed',
    manager=manager
)

# Add radial velocity slider

base_size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 320), (200, 20)),
    start_value=BASE_SIZE,
    value_range=(2, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 305), (200, 20)),
    text='Base Circle Size',
    manager=manager
)

# Add new slider after the base_size_slider:
fade_duration_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 370), (200, 20)),
    start_value=FADE_DURATION,
    value_range=(1.0, 30.0),  # 1 to 30 seconds
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 355), (200, 20)),
    text='Fade Duration (seconds)',
    manager=manager
)

# New slider for max trail alpha
max_alpha_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 420), (200, 20)),
    start_value=MAX_ALPHA,
    value_range=(0, 255),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 405), (200, 20)),
    text='Max Trail Alpha',
    manager=manager
)

# Add the new slider (before the buttons)
trail_spacing_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 470), (200, 20)),
    start_value=TRAIL_SPACING_FACTOR,
    value_range=(0.0, 1.0),
    click_increment=0.05,  # adjusts by 0.05 per arrow click
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 455), (200, 20)),
    text='Trail Point Spacing',
    manager=manager
)

# Move buttons down to make room
clear_trails_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 520), (200, 30)),
    text='Clear Trails',
    manager=manager
)

new_group_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 560), (200, 30)),
    text='Create New Group',
    manager=manager
)

clear_groups_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 600), (200, 30)),
    text='Clear All Groups',
    manager=manager
)

# Add reset button
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 640), (200, 30)),
    text='Reset All Settings',
    manager=manager
)

# Create circle system
circle_system = SpringleCircle(MIN_CIRCLES, MAX_CIRCLES,
                               START_RADIAL_VELOCITY, START_ANGULAR_VELOCITY,
                               ANGULAR_ACCELERATION, RADIAL_ACCELERATION, 
                               BASE_SIZE, WIDTH, HEIGHT)

# Modify main game loop to handle mouse input
running = True
clock = pygame.time.Clock()
mouse_button_pressed = False
mouse_pos = None

while running:
    time_delta = clock.tick(60)/1000.0
    
    # Get the current event queue
    events = pygame.event.get()
    
    # Check for UI element interactions first
    ui_event_occurred = False
    for event in events:
        if event.type in (pygame_gui.UI_BUTTON_PRESSED, pygame_gui.UI_HORIZONTAL_SLIDER_MOVED):
            ui_event_occurred = True
            break
        # Also check for mouse events over UI elements
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            mouse_pos = pygame.mouse.get_pos()
            if manager.get_hovering_any_element():  # Check if mouse is over any UI element
                ui_event_occurred = True
                break
            
    # Process all events
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            
        # Handle UI events
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == min_circles_slider:
                MIN_CIRCLES = int(event.value)
            elif event.ui_element == max_circles_slider:
                MAX_CIRCLES = max(MIN_CIRCLES, int(event.value))
            elif event.ui_element == expansion_rate_slider:
                ANGULAR_ACCELERATION = event.value
            elif event.ui_element == radial_acceleration_slider:
                RADIAL_ACCELERATION = event.value
            elif event.ui_element == angular_velocity_slider:
                START_ANGULAR_VELOCITY = event.value
            elif event.ui_element == radial_velocity_slider:
                START_RADIAL_VELOCITY = event.value
            elif event.ui_element == base_size_slider:
                BASE_SIZE = event.value
            elif event.ui_element == fade_duration_slider:
                FADE_DURATION = event.value
            elif event.ui_element == max_alpha_slider:
                MAX_ALPHA = event.value
            elif event.ui_element == trail_spacing_slider:
                TRAIL_SPACING_FACTOR = event.value
                
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == clear_trails_button:
                for group in circle_system.groups:
                    for circle in group.circles:
                        circle['trail'] = []
                        circle['last_trail_pos'] = None
            elif event.ui_element == new_group_button:
                # Create a new group with current settings
                new_group = OrbitGroup(MIN_CIRCLES, MAX_CIRCLES, 0, BASE_SIZE,
                                       START_RADIAL_VELOCITY, START_ANGULAR_VELOCITY, 
                                       RADIAL_ACCELERATION, ANGULAR_ACCELERATION, False)
                circle_system.groups.append(new_group)
            elif event.ui_element == clear_groups_button:
                # Create a single new group to ensure the system isn't empty
                new_group = OrbitGroup(MIN_CIRCLES, MAX_CIRCLES, 0, BASE_SIZE,
                                       START_RADIAL_VELOCITY, START_ANGULAR_VELOCITY, 
                                       RADIAL_ACCELERATION, ANGULAR_ACCELERATION, False)
                circle_system.groups = [new_group]
                # In main event loop, add this to the UI_BUTTON_PRESSED section:
            elif event.ui_element == reset_button:
                # Reset all sliders to their default values
                min_circles_slider.set_current_value(DEFAULT_VALUES['min_circles'])
                max_circles_slider.set_current_value(DEFAULT_VALUES['max_circles'])
                expansion_rate_slider.set_current_value(DEFAULT_VALUES['angular_acceleration'])
                radial_acceleration_slider.set_current_value(DEFAULT_VALUES['radial_acceleration'])
                angular_velocity_slider.set_current_value(DEFAULT_VALUES['starting_angular_velocity'])
                base_size_slider.set_current_value(DEFAULT_VALUES['base_size'])
                fade_duration_slider.set_current_value(DEFAULT_VALUES['fade_duration'])
                max_alpha_slider.set_current_value(DEFAULT_VALUES['max_alpha'])
                trail_spacing_slider.set_current_value(DEFAULT_VALUES['trail_spacing'])
                
                # Update the variables to match
                MIN_CIRCLES = DEFAULT_VALUES['min_circles']
                MAX_CIRCLES = DEFAULT_VALUES['max_circles']
                ANGULAR_ACCELERATION = DEFAULT_VALUES['angular_acceleration']
                RADIAL_ACCELERATION = DEFAULT_VALUES['radial_acceleration']
                START_ANGULAR_VELOCITY = DEFAULT_VALUES['starting_angular_velocity']
                START_RADIAL_VELOCITY = DEFAULT_VALUES['starting_radial_velocity']
                BASE_SIZE = DEFAULT_VALUES['base_size']
                FADE_DURATION = DEFAULT_VALUES['fade_duration']
                MAX_ALPHA = DEFAULT_VALUES['max_alpha']
                TRAIL_SPACING_FACTOR = DEFAULT_VALUES['trail_spacing']
                
        # To capture screenshots
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Press 'S' to save screenshot
                take_screenshot(screen)
        
        # Handle mouse events only if UI didn't handle them
        if not ui_event_occurred:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_button_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_button_pressed = False
        
        # Make sure pygame_gui processes all events
        manager.process_events(event)
    
    # Update game state
    manager.update(time_delta)
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update and draw circle system with mouse input
    current_mouse_pos = pygame.mouse.get_pos()
    circle_system.update(time_delta, MIN_CIRCLES, MAX_CIRCLES, 
                         START_RADIAL_VELOCITY, START_ANGULAR_VELOCITY,
                         ANGULAR_ACCELERATION, RADIAL_ACCELERATION, 
                         BASE_SIZE, mouse_button_pressed, current_mouse_pos, 
                         FADE_DURATION, TRAIL_SPACING_FACTOR)
    
    # Pass MAX_ALPHA to the draw method
    circle_system.draw(screen, MAX_ALPHA)
    
    # Get current mouse position and adjust to center coordinates
    mouse_x, mouse_y = pygame.mouse.get_pos()
    centered_x = mouse_x - (WIDTH // 2)
    centered_y = (HEIGHT // 2) - mouse_y  # Flip Y to make positive go up

    # Render mouse position text
    mouse_pos_text = f"Mouse: ({centered_x}, {centered_y})"
    text_surface = pygame.mouse_pos_font.render(mouse_pos_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.bottomright = (WIDTH - 10, HEIGHT - 10)

    # Draw mouse position text
    screen.blit(text_surface, text_rect)
    
    # Update and draw FPS counter
    fps_counter.update(time_delta)
    fps_counter.draw(screen)
    
    # Draw the screenshot instruction text
    screenshot_text = 'Press "s" to save screenshot'
    text_surface = screenshot_font.render(screenshot_text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.bottomleft = (10, screen.get_height() - 10)
    screen.blit(text_surface, text_rect)
        
    # Draw UI
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()

