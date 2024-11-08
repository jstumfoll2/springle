import pygame
import numpy as np
from pygame import Surface, SRCALPHA
from typing import Tuple, List, Dict
import moderngl
from lib.SpringleCircle import SpringleCircle
import math

class GPUCircleRenderer:
    def __init__(self, window_size: Tuple[int, int]):
        self.window_size = window_size
        self.width, self.height = window_size
        
        # Get actual display scaling factor
        display_info = pygame.display.Info()
        self.display_scale = pygame.display.get_window_size()[0] / window_size[0]
        
        # Create scaled dimensions
        self.scaled_size = (int(window_size[0] * self.display_scale), 
                          int(window_size[1] * self.display_scale))
        
        self.ctx = moderngl.create_standalone_context()
        
        vertex_shader = '''
            #version 330
            
            in vec2 in_vert;
            in vec2 in_center;
            in vec4 in_color;
            in float in_size;
            
            out vec2 v_uv;
            out vec4 v_color;
            
            void main() {
                // Scale the size and position based on display scale
                vec2 scaled_center = in_center * ${scale};
                float scaled_size = in_size * ${scale};
                
                vec2 screen_pos = scaled_center + (in_vert * scaled_size);
                vec2 clip_pos = (screen_pos / vec2(${width}, ${height})) * 2.0 - 1.0;
                clip_pos.y = -clip_pos.y;
                
                gl_Position = vec4(clip_pos, 0.0, 1.0);
                v_uv = in_vert;
                v_color = in_color;
            }
        '''.replace('${width}', str(float(self.scaled_size[0])))\
           .replace('${height}', str(float(self.scaled_size[1])))\
           .replace('${scale}', str(float(self.display_scale)))
        
        fragment_shader = '''
            #version 330
            
            in vec2 v_uv;
            in vec4 v_color;
            
            out vec4 f_color;
            
            void main() {
                float dist = length(v_uv);
                if (dist > 1.0) {
                    discard;
                }
                
                // Improved anti-aliasing
                float edge_smoothing = fwidth(dist);
                float alpha = 1.0 - smoothstep(1.0 - edge_smoothing, 1.0, dist);
                
                // Enhanced gradient
                float gradient = pow(1.0 - dist, 1.5);
                alpha *= gradient;
                
                f_color = vec4(v_color.rgb, v_color.a * alpha);
            }
        '''
        
        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        
        # Create unit circle vertices with more points for smoother circles
        angles = np.linspace(0, 2*np.pi, 32, endpoint=False)
        vertices = np.array([(np.cos(angle), np.sin(angle)) for angle in angles], dtype='f4')
        
        self.vbo = self.ctx.buffer(vertices.tobytes())
        
        self.max_instances = 10000
        self.instance_data = np.zeros(self.max_instances * 7, dtype='f4')
        self.instance_buffer = self.ctx.buffer(self.instance_data.tobytes())
        
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, '2f', 'in_vert'),
                (self.instance_buffer, '2f 4f 1f/i', 'in_center', 'in_color', 'in_size'),
            ]
        )
        
        # Create high-resolution texture and framebuffer
        self.texture = self.ctx.texture(self.scaled_size, 4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])
    
    def render(self, circles: List[Dict], background_color: Tuple[int, int, int, int]) -> Surface:
        """Render circles at high resolution and return scaled surface."""
        self.fbo.use()
        
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
        
        # Clear with background color
        self.ctx.clear(
            background_color[0]/255,
            background_color[1]/255,
            background_color[2]/255,
            background_color[3]/255
        )
        
        if circles:
            # Update instance data
            num_circles = min(len(circles), self.max_instances)
            for i, circle in enumerate(circles[:num_circles]):
                idx = i * 7
                self.instance_data[idx:idx+7] = [
                    circle['x'], circle['y'],
                    circle['color'][0]/255, circle['color'][1]/255,
                    circle['color'][2]/255, circle['alpha']/255,
                    circle['size']
                ]
            
            self.instance_buffer.write(self.instance_data.tobytes())
            self.vao.render(moderngl.TRIANGLE_FAN, instances=num_circles)
        
        # Read pixels at high resolution
        pixels = self.fbo.read(components=4)
        
        # Create high-res surface
        temp_surface = pygame.image.fromstring(pixels, self.scaled_size, 'RGBA')
        
        # Scale down to window size with smooth scaling
        final_surface = pygame.Surface(self.window_size, pygame.SRCALPHA)
        pygame.transform.smoothscale(temp_surface, self.window_size, final_surface)
        
        return final_surface
    
    def cleanup(self):
        self.vbo.release()
        self.instance_buffer.release()
        self.vao.release()
        self.prog.release()
        self.texture.release()
        self.fbo.release()
        self.ctx.release()

class GPUAcceleratedSpingleCircle(SpringleCircle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpu_renderer = GPUCircleRenderer((self.WIDTH, self.HEIGHT))
        
    def calculate_circle_size(self, radius, base_size, size_variation):
        """Adjusted size calculation for GPU rendering."""
        size_factor = math.log(radius + 1) / 5 if radius > 0 else 1
        # Adjust base size for GPU rendering
        adjusted_base_size = base_size * 1.0  # Adjust this factor if needed
        return adjusted_base_size * size_variation * size_factor
        
    def draw(self, screen, max_alpha):
        # Same as before, but with adjusted alpha handling
        drawable_elements = []
        
        # Collect fade trails with improved alpha calculation
        for creation_time, (x, y, color, size, age) in self.fading_trails:
            fade_progress = age / self.fade_duration
            # Improved easing function for smoother fade
            eased_fade = 1 - (fade_progress * fade_progress)
            alpha = int(max(0, max_alpha * eased_fade))
            
            if alpha > 0:
                drawable_elements.append({
                    'x': x,
                    'y': y,
                    'color': color,
                    'size': size,
                    'alpha': alpha
                })
        
        # Add active group trails and circles
        for group in sorted(self.groups, key=lambda g: g.creation_time):
            if not group.active:
                continue
            
            for circle in group.circles:
                # Add trails with improved alpha blending
                for x, y, color, size, age, _ in circle['trail']:
                    fade_progress = age / self.fade_duration
                    eased_fade = 1 - (fade_progress * fade_progress)
                    alpha = int(max(0, max_alpha * eased_fade))
                    
                    if alpha > 0:
                        drawable_elements.append({
                            'x': x,
                            'y': y,
                            'color': color,
                            'size': size,
                            'alpha': alpha
                        })
                
                # Add current circle
                x, y = group.get_circle_cartesian_pos(circle, self.center)
                if (0 <= x <= self.WIDTH * 1.2 and 0 <= y <= self.HEIGHT * 1.2):
                    color = self.colors.getColor(
                        group.palette_index,
                        circle['color_index'],
                        group.color_transition
                    )
                    size = self.calculate_circle_size(
                        circle['motion'].radius,
                        circle['base_size'],
                        circle['size_variation']
                    )
                    
                    drawable_elements.append({
                        'x': x,
                        'y': y,
                        'color': color,
                        'size': size,
                        'alpha': 255
                    })
        
        # Get background color
        bg_color = screen.get_at((0, 0))
        
        # Render high-resolution circles
        rendered_surface = self.gpu_renderer.render(drawable_elements, bg_color)
        
        # Blit to screen
        screen.blit(rendered_surface, (0, 0))
        
    def __del__(self):
        if hasattr(self, 'gpu_renderer'):
            self.gpu_renderer.cleanup()