import pygame
from math import pi

class RainbowArc(pygame.sprite.Sprite):
    def __init__(self, x, y, sounds):
        super().__init__()
        self.width = 100
        self.height = 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.sounds = sounds

        # Arcoiris
        pygame.draw.arc(self.image, (255, 0, 0), (0, 0, self.width, self.height * 2), 0, pi, 4)                 # Rojo
        pygame.draw.arc(self.image, (255, 165, 0), (5, 5, self.width - 10, self.height * 2 - 10), 0, pi, 4)     # Naranja
        pygame.draw.arc(self.image, (255, 255, 0), (10, 10, self.width - 20, self.height * 2 - 20), 0, pi, 4)   # Amarillo
        pygame.draw.arc(self.image, (0, 128, 0), (15, 15, self.width - 30, self.height * 2 - 30), 0, pi, 4)     # Verde
        pygame.draw.arc(self.image, (0, 0, 255), (20, 20, self.width - 40, self.height * 2 - 40), 0, pi, 4)     # Azul
        pygame.draw.arc(self.image, (75, 0, 130), (25, 25, self.width - 50, self.height * 2 - 50), 0, pi, 4)    # Índigo
        pygame.draw.arc(self.image, (238, 130, 238), (30, 30, self.width - 60, self.height * 2 - 60), 0, pi, 4) # Violeta

        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.start_time = pygame.time.get_ticks()
        self.vel_y = 0
        self.falling = False

    def update(self, enemies):
        if self.falling:
            self.vel_y = min(self.vel_y + 0.5, 10)
            self.rect.y += self.vel_y

        next_rect = self.rect.move(0, self.vel_y)

        # Colisiones
        for enemy in enemies:
            if next_rect.colliderect(enemy.rect) and not enemy.dying:
                offset_x = enemy.rect.x - self.rect.x
                offset_y = enemy.rect.y - self.rect.y
                if self.mask.overlap(enemy.mask, (offset_x, offset_y)):
                    enemy.dying = True
                self.sounds['enemykill'].play()

        # Duración del arcoiris
        if not self.falling and pygame.time.get_ticks() - self.start_time > 3000:
            self.kill()
