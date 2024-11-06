import pygame
import math
import colorsys

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rainbow Bouncing Circle")

# Circle properties
circle_radius = 20
x = WIDTH // 2
y = HEIGHT // 2
speed_x = 5
speed_y = 4

# Trail properties
trail = []
trail_length = 50
hue = 0

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update circle position
    x += speed_x
    y += speed_y
    
    # Bounce off walls
    if x <= circle_radius or x >= WIDTH - circle_radius:
        speed_x = -speed_x
    if y <= circle_radius or y >= HEIGHT - circle_radius:
        speed_y = -speed_y
    
    # Update trail
    trail.append((x, y, hue))
    if len(trail) > trail_length:
        trail.pop(0)
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Draw trail
    for i, (trail_x, trail_y, trail_hue) in enumerate(trail):
        # Calculate alpha and size for trail effect
        alpha = int(255 * (i / trail_length))
        trail_radius = int(circle_radius * (i / trail_length))
        
        # Convert HSV to RGB (hue cycles from 0 to 1)
        rgb = colorsys.hsv_to_rgb(trail_hue % 1.0, 1.0, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        
        # Create surface for semi-transparent circle
        circle_surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (*color, alpha), (trail_radius, trail_radius), trail_radius)
        screen.blit(circle_surface, (trail_x - trail_radius, trail_y - trail_radius))
    
    # Draw current circle
    rgb = colorsys.hsv_to_rgb(hue % 1.0, 1.0, 1.0)
    color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    pygame.draw.circle(screen, color, (int(x), int(y)), circle_radius)
    
    # Update hue for rainbow effect
    hue += 0.005
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()