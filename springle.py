import pygame
import pygame_gui

from OrbitGroup import OrbitGroup
from SpringleCircle import SpringleCircle  # Update import to use the class

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 1080
HEIGHT = 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Springle")

# Initialize UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Initial parameters
MIN_CIRCLES = 6
MAX_CIRCLES = 12
BASE_EXPANSION_RATE = 40
RATE_VARIATION = 3
ROTATION_SPEED = 1.2
BASE_SIZE = 25
FADE_DURATION = 6.0
MAX_ALPHA = 128  # New parameter for max trail alpha
TRAIL_SPACING_FACTOR = 0.5

# First, define original/default values at the start of your program, after the WIDTH/HEIGHT definitions
DEFAULT_VALUES = {
    'min_circles': MIN_CIRCLES,  # 8
    'max_circles': MAX_CIRCLES,  # 10
    'base_expansion_rate': BASE_EXPANSION_RATE,  # 40
    'rate_variation': RATE_VARIATION,  # 3
    'rotation_speed': ROTATION_SPEED,  # 1.2
    'base_size': BASE_SIZE,  # 25
    'fade_duration': FADE_DURATION,  # 6.0
    'max_alpha': MAX_ALPHA,  # 128
    'trail_spacing': TRAIL_SPACING_FACTOR  # 0.5
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
    start_value=BASE_EXPANSION_RATE,
    value_range=(1, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 105), (200, 20)),
    text='Base Expansion Rate',
    manager=manager
)

rate_variation_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 170), (200, 20)),
    start_value=RATE_VARIATION,
    value_range=(0.01, 20.0),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 155), (200, 20)),
    text='Expansion Rate Variation',
    manager=manager
)

rotation_speed_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 220), (200, 20)),
    start_value=ROTATION_SPEED,
    value_range=(0.1, 10),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 205), (200, 20)),
    text='Rotation Speed',
    manager=manager
)

base_size_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 270), (200, 20)),
    start_value=BASE_SIZE,
    value_range=(2, 100),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 255), (200, 20)),
    text='Base Circle Size',
    manager=manager
)

# Add new slider after the base_size_slider:
fade_duration_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 320), (200, 20)),
    start_value=FADE_DURATION,
    value_range=(1.0, 30.0),  # 1 to 30 seconds
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 305), (200, 20)),
    text='Fade Duration (seconds)',
    manager=manager
)

# New slider for max trail alpha
max_alpha_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 370), (200, 20)),
    start_value=MAX_ALPHA,
    value_range=(0, 255),
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 355), (200, 20)),
    text='Max Trail Alpha',
    manager=manager
)

# Add the new slider (before the buttons)
trail_spacing_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((20, 420), (200, 20)),
    start_value=TRAIL_SPACING_FACTOR,
    value_range=(0.0, 1.0),
    click_increment=0.05,  # adjusts by 0.05 per arrow click
    manager=manager
)
pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((20, 405), (200, 20)),
    text='Trail Point Spacing',
    manager=manager
)

# Move buttons down to make room
clear_trails_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 470), (200, 30)),
    text='Clear Trails',
    manager=manager
)

new_group_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 510), (200, 30)),
    text='Create New Group',
    manager=manager
)

clear_groups_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 550), (200, 30)),
    text='Clear All Groups',
    manager=manager
)

# Add reset button (after your other buttons)
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((20, 590), (200, 30)),
    text='Reset All Settings',
    manager=manager
)

# Create circle system
circle_system = SpringleCircle(MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE, 
                               RATE_VARIATION, ROTATION_SPEED, BASE_SIZE, WIDTH, HEIGHT)

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
                BASE_EXPANSION_RATE = event.value
            elif event.ui_element == rate_variation_slider:
                RATE_VARIATION = event.value
            elif event.ui_element == rotation_speed_slider:
                ROTATION_SPEED = event.value
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
                new_group = OrbitGroup(MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE,
                                   RATE_VARIATION, ROTATION_SPEED, BASE_SIZE, 0)
                circle_system.groups.append(new_group)
            elif event.ui_element == clear_groups_button:
                # Create a single new group to ensure the system isn't empty
                new_group = OrbitGroup(MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE,
                                   RATE_VARIATION, ROTATION_SPEED, BASE_SIZE, 0)
                circle_system.groups = [new_group]
                # In your main event loop, add this to the UI_BUTTON_PRESSED section:
            elif event.ui_element == reset_button:
                # Reset all sliders to their default values
                min_circles_slider.set_current_value(DEFAULT_VALUES['min_circles'])
                max_circles_slider.set_current_value(DEFAULT_VALUES['max_circles'])
                expansion_rate_slider.set_current_value(DEFAULT_VALUES['base_expansion_rate'])
                rate_variation_slider.set_current_value(DEFAULT_VALUES['rate_variation'])
                rotation_speed_slider.set_current_value(DEFAULT_VALUES['rotation_speed'])
                base_size_slider.set_current_value(DEFAULT_VALUES['base_size'])
                fade_duration_slider.set_current_value(DEFAULT_VALUES['fade_duration'])
                max_alpha_slider.set_current_value(DEFAULT_VALUES['max_alpha'])
                trail_spacing_slider.set_current_value(DEFAULT_VALUES['trail_spacing'])
                
                # Update the variables to match
                MIN_CIRCLES = DEFAULT_VALUES['min_circles']
                MAX_CIRCLES = DEFAULT_VALUES['max_circles']
                BASE_EXPANSION_RATE = DEFAULT_VALUES['base_expansion_rate']
                RATE_VARIATION = DEFAULT_VALUES['rate_variation']
                ROTATION_SPEED = DEFAULT_VALUES['rotation_speed']
                BASE_SIZE = DEFAULT_VALUES['base_size']
                FADE_DURATION = DEFAULT_VALUES['fade_duration']
                MAX_ALPHA = DEFAULT_VALUES['max_alpha']
                TRAIL_SPACING_FACTOR = DEFAULT_VALUES['trail_spacing']
        
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
    current_mouse_pos = pygame.mouse.get_pos() if mouse_button_pressed else None
    circle_system.update(time_delta, MIN_CIRCLES, MAX_CIRCLES, BASE_EXPANSION_RATE, 
                        RATE_VARIATION, ROTATION_SPEED, BASE_SIZE, 
                        mouse_button_pressed, current_mouse_pos, FADE_DURATION,
                        TRAIL_SPACING_FACTOR)
    
    # Pass MAX_ALPHA to the draw method
    circle_system.draw(screen, MAX_ALPHA)
    
    # Draw UI
    manager.draw_ui(screen)
    
    # Update display
    pygame.display.flip()

pygame.quit()