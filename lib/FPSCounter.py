import pygame

class FPSCounter:
    def __init__(self, font_size=24):
        self.font = pygame.font.Font(None, font_size)
        self.clock = pygame.time.Clock()
        self.fps_text = "0 FPS"
        self.update_time = 0
        self.frames = 0
        self.update_interval = 0.5  # Update FPS display every 0.5 seconds

    def update(self, dt):
        self.frames += 1
        self.update_time += dt
        
        if self.update_time >= self.update_interval:
            self.fps_text = f"{int(self.frames / self.update_time)} FPS"
            self.frames = 0
            self.update_time = 0

    def draw(self, screen):
        text_surface = self.font.render(self.fps_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topright = (screen.get_width() - 10, 10)
        screen.blit(text_surface, text_rect)