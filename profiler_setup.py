# profiler_setup.py

import cProfile
import pstats
import line_profiler
import os
import pygame
import time
import random
from SpringleCircle import SpringleCircle

def setup_game():
    """Setup basic pygame environment for testing"""
    pygame.init()
    WIDTH = 1080
    HEIGHT = 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Initial parameters
    MIN_CIRCLES = 6
    MAX_CIRCLES = 12
    ANGULAR_ACCELERATION = 40
    RADIAL_ACCELERATION = 3
    START_ANGULAR_VELOCITY = 25
    START_RADIAL_VELOCITY = 200
    BASE_SIZE = 25
    
    circle_system = SpringleCircle(MIN_CIRCLES, MAX_CIRCLES,
                                 START_RADIAL_VELOCITY, START_ANGULAR_VELOCITY,
                                 ANGULAR_ACCELERATION, RADIAL_ACCELERATION, 
                                 BASE_SIZE, WIDTH, HEIGHT)
    
    return screen, circle_system, (WIDTH, HEIGHT)

def simulate_mouse_interaction(circle_system, screen_size, frame_num):
    """Simulate mouse interactions periodically"""
    WIDTH, HEIGHT = screen_size
    center = (WIDTH // 2, HEIGHT // 2)
    
    # Create new groups with mouse interaction every 30 frames
    if frame_num % 30 == 0:
        # Simulate mouse press at random position
        mouse_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        circle_system.update(1/60, 6, 12, 200, 25, 40, 3, 25, 
                           True, mouse_pos, 10.0, 0.5)
        
        # Simulate mouse drag
        for _ in range(10):  # Simulate 10 frames of dragging
            new_pos = (
                mouse_pos[0] + random.randint(-100, 100),
                mouse_pos[1] + random.randint(-100, 100)
            )
            circle_system.update(1/60, 6, 12, 200, 25, 40, 3, 25, 
                               True, new_pos, 10.0, 0.5)
        
        # Simulate mouse release with velocity
        final_pos = (
            new_pos[0] + random.randint(-50, 50),
            new_pos[1] + random.randint(-50, 50)
        )
        circle_system.update(1/60, 6, 12, 200, 25, 40, 3, 25, 
                           False, final_pos, 10.0, 0.5)

def simulate_complex_scene(duration_seconds=5):
    """Simulate a complex scene with multiple groups and interactions"""
    screen, circle_system, screen_size = setup_game()
    frame_count = int(duration_seconds * 60)  # 60 FPS for specified duration
    
    # Pre-create several groups to ensure a busy scene
    for _ in range(3):
        simulate_mouse_interaction(circle_system, screen_size, 0)
    
    # Main simulation loop
    for frame in range(frame_count):
        screen.fill((0, 0, 0))
        
        # Simulate periodic mouse interactions
        simulate_mouse_interaction(circle_system, screen_size, frame)
        
        # Regular update and draw
        circle_system.update(1/60, 6, 12, 200, 25, 40, 3, 25, 
                           False, (500, 500), 10.0, 0.5)
        circle_system.draw(screen, 128)
        
        pygame.display.flip()
        
        # Print progress
        if frame % 60 == 0:
            print(f"Profiling progress: {frame/frame_count*100:.1f}%")

def run_cprofile():
    """Run cProfile analysis"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    simulate_complex_scene()
    
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(50)  # Print top 50 time-consuming functions
    
    # Save detailed stats to file
    stats.dump_stats('profile_results.prof')
    print("\nDetailed results saved to 'profile_results.prof'")
    print("You can view them with: python -m snakeviz profile_results.prof")

def run_line_profiler():
    """Run line-by-line profiling on specific functions"""
    profile = line_profiler.LineProfiler()
    
    # Profile specific methods
    profile.add_function(SpringleCircle._create_gradient_circle)
    profile.add_function(SpringleCircle._get_cached_gradient)
    profile.add_function(SpringleCircle.draw)
    profile.add_function(SpringleCircle.update)
    profile.add_function(SpringleCircle.calculate_circle_size)
    profile.add_function(SpringleCircle.should_add_trail_point)
    
    profile.runcall(simulate_complex_scene)
    
    # Save and print results
    profile.print_stats()
    with open('line_profile_results.txt', 'w') as f:
        profile.print_stats(stream=f)

if __name__ == '__main__':
    # First run cProfile
    print("Running cProfile analysis...")
    run_cprofile()
    
    print("\nRunning line-by-line profiling...")
    run_line_profiler()