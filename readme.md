# Springle

Springle is an interactive particle animation system that creates mesmerizing visual effects through orbital motion and color transitions. Users can create and manipulate groups of particles that leave colorful trails as they move across the screen.

![Springle Animation Demo] (Screenshot to be added)

## Features

- Interactive particle creation and manipulation using mouse input
- Real-time parameter adjustment through an intuitive UI
- Smooth color transitions and trail effects
- Physics-based orbital motion system
- FPS counter for performance monitoring
- Multiple color palettes with automatic transitions
- Gradient-based particle rendering
- Trail system with customizable fade effects

## Requirements

- Python 3.x
- Pygame
- Pygame_gui

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jstumfoll2/springle.git
cd springle
```

2. Install required packages:
```bash
pip install pygame pygame_gui
```

3. Run the application:
```bash
python Springle.py
```

## Controls

### Mouse Controls
- Click and drag to create new particle groups
- Release to set the group's velocity
- Groups will continue to move based on physics calculations

### UI Controls
- **Min/Max Circles per Group**: Adjust the number of particles in new groups
- **Angular Acceleration**: Control the rotational acceleration of particles
- **Radial Acceleration**: Adjust the inward/outward acceleration
- **Starting Rotation Speed**: Set initial angular velocity
- **Starting Radial Speed**: Set initial radial velocity
- **Base Circle Size**: Adjust particle size
- **Fade Duration**: Control how long trails persist
- **Max Trail Alpha**: Adjust trail transparency
- **Trail Point Spacing**: Control density of trail points

### Buttons
- **Clear Trails**: Remove all existing trails
- **Create New Group**: Spawn a new particle group
- **Clear All Groups**: Remove all groups except one
- **Reset All Settings**: Return all parameters to default values

## Architecture

The project is organized into several key components:

- `Springle.py`: Main application entry point
- `SpringleCircle.py`: Core particle system manager
- `OrbitGroup.py`: Manages groups of particles
- `PolarMotion.py`: Handles particle movement calculations
- `MouseControlSystem.py`: Processes mouse input
- `SpingleColors.py`: Color management system
- `FPSCounter.py`: Performance monitoring

## Performance Optimization

The system includes several optimizations:
- Gradient caching system for improved rendering performance
- Efficient trail point calculation
- Optimized color transition handling
- Smart particle culling when off-screen

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Future Enhancements

- [ ] Color control slider
- [ ] Maximum groups slider
- [ ] Time-based trail system
- [ ] Different particle shapes
- [ ] Background color options
- [ ] Options menu
- [ ] Screenshot functionality
- [ ] Pause button
- [ ] Android port

## License

This project is licensed under the MIT License -- see LICENSE file for more detail.

## Acknowledgments

- Inspired by particle systems and orbital mechanics
- Built with Pygame and Pygame_gui
- Special thanks to contributors and testers

## Author

Jason Stumfoll

---
For bugs, feature requests, or questions, please open an issue on the GitHub repository.