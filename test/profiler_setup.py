# test/profiler_setup.py

import cProfile
import pstats
import line_profiler
import os
import pygame
import time
import random
import sys
from pathlib import Path

# Add parent directory to path so we can import from lib
sys.path.append(str(Path(__file__).parent.parent))

from lib.SpringleCircle import SpringleCircle
from lib.SpringleParams import SpringleParams

class MockColorManager:
    """Simple color manager for testing without UI dependencies"""
    def __init__(self):
        self.current_color = (185, 150, 234)  # Default purple background
        
    def get_color(self):
        return self.current_color
        
    def handle_event(self, event):
        pass

def setup_game():
    """Setup basic pygame environment for testing"""
    pygame.init()
    WIDTH = 1080
    HEIGHT = 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # Initial parameters
    params = SpringleParams(
        min_circles=6,
        max_circles=12,
        radial_velocity=200,
        angular_velocity=25,
        radial_acceleration=3,
        angular_acceleration=40,
        base_size=25,
        mouse_button_pressed=False,
        mouse_pos=(0, 0),
        fade_duration=5.0,
        space_factor=0.5,
        auto_generate=True
    )
    
    circle_system = SpringleCircle(
        params.min_circles, params.max_circles,
        params.radial_velocity, params.angular_velocity,
        params.radial_acceleration, params.angular_acceleration,
        params.base_size, WIDTH, HEIGHT
    )
    
    return screen, circle_system, (WIDTH, HEIGHT), params

def simulate_mouse_interaction(circle_system, screen_size, frame_num, params):
    """Simulate mouse interactions periodically"""
    WIDTH, HEIGHT = screen_size
    center = (WIDTH // 2, HEIGHT // 2)
    
    # Create new groups with mouse interaction every 30 frames
    if frame_num % 30 == 0:
        # Simulate mouse press at random position
        mouse_pos = (random.randint(0, WIDTH), random.randint(0, HEIGHT))
        params.mouse_button_pressed = True
        params.mouse_pos = mouse_pos
        circle_system.update(1/60, params)
        
        # Simulate mouse drag
        for _ in range(10):  # Simulate 10 frames of dragging
            new_pos = (
                mouse_pos[0] + random.randint(-100, 100),
                mouse_pos[1] + random.randint(-100, 100)
            )
            params.mouse_pos = new_pos
            circle_system.update(1/60, params)
        
        # Simulate mouse release with velocity
        final_pos = (
            new_pos[0] + random.randint(-50, 50),
            new_pos[1] + random.randint(-50, 50)
        )
        params.mouse_button_pressed = False
        params.mouse_pos = final_pos
        circle_system.update(1/60, params)

def simulate_complex_scene(duration_seconds=5):
    """Simulate a complex scene with multiple groups and interactions"""
    screen, circle_system, screen_size, params = setup_game()
    frame_count = int(duration_seconds * 60)  # 60 FPS for specified duration
    
    # Create output directories if they don't exist
    output_dir = Path(__file__).parent / 'profiler_output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Pre-create several groups to ensure a busy scene
    for _ in range(3):
        simulate_mouse_interaction(circle_system, screen_size, 0, params)
    
    # Use mock color manager instead of the full UI version
    bg_color_manager = MockColorManager()
    
    # Main simulation loop
    for frame in range(frame_count):
        screen.fill(bg_color_manager.get_color())
        
        # Simulate periodic mouse interactions
        simulate_mouse_interaction(circle_system, screen_size, frame, params)
        
        # Regular update and draw
        circle_system.update(1/60, params)
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
    
    # Save results to the test directory
    output_dir = Path(__file__).parent / 'profiler_output'
    output_file = output_dir / 'profile_results.prof'
    
    stats.dump_stats(output_file)
    stats.print_stats(50)  # Print top 50 time-consuming functions
    
    print(f"\nDetailed results saved to: {output_file}")
    print(f"View with: python -m snakeviz {output_file}")

def run_line_profiler():
    """Run line-by-line profiling on specific functions"""
    profile = line_profiler.LineProfiler()
    
    # Profile specific methods from SpringleCircle
    profile.add_function(SpringleCircle._create_gradient_circle)
    profile.add_function(SpringleCircle._get_cached_gradient)
    profile.add_function(SpringleCircle.draw)
    profile.add_function(SpringleCircle.update)
    profile.add_function(SpringleCircle.calculate_circle_size)
    profile.add_function(SpringleCircle.should_add_trail_point)
    
    profile.runcall(simulate_complex_scene)
    
    # Save and print results to the test directory
    output_dir = Path(__file__).parent / 'profiler_output'
    output_file = output_dir / 'line_profile_results.txt'
    
    # Print to console
    profile.print_stats()
    
    # Save to file
    with open(output_file, 'w') as f:
        profile.print_stats(stream=f)
    
    print(f"\nLine profiler results saved to: {output_file}")

if __name__ == '__main__':
    # Ensure we're using the correct working directory
    os.chdir(Path(__file__).parent.parent)
    
    print("Running cProfile analysis...")
    run_cprofile()
    
    print("\nRunning line-by-line profiling...")
    run_line_profiler()