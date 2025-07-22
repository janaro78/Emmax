import pygame
from assets import load_frame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, frame_data, sprite_sheet):
        super().__init__()
        self.images_right = [
            pygame.transform.rotate(load_frame(f'pinkBugWalkRight{n}', frame_data, sprite_sheet), 90)
            for n in range(1, 4)
        ]
        self.images_left = [
            pygame.transform.rotate(load_frame(f'pinkBugWalkLeft{n}', frame_data, sprite_sheet), 90)
            for n in range(1, 4)
        ]
        self.image = self.images_right[0]
        self.rect = self.image.get_rect(x=x, y=y)
        self.mask = pygame.mask.from_surface(self.image)

        self.move_direction = 1
        self.move_counter = 0
        self.vel_y = 0
        self.in_air = True
        self.dying = False
        self.alpha = 255
        self.fade_speed = 5
        self.animation_index = 0
        self.animation_cooldown = 100  # ms
        self.last_animation_update = pygame.time.get_ticks()

    def update(self, world, rainbows):
        current_time = pygame.time.get_ticks()

        if self.dying:
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.kill()
                return

            base_img = self.images_right[self.animation_index] if self.move_direction == 1 else self.images_left[self.animation_index]
            temp_image = base_img.copy()
            temp_image.set_alpha(self.alpha)
            self.image = temp_image

        else:
            # Animación
            if current_time - self.last_animation_update > self.animation_cooldown:
                self.animation_index = (self.animation_index + 1) % len(self.images_right)
                self.last_animation_update = current_time
                self.image = self.images_right[self.animation_index] if self.move_direction == 1 else self.images_left[self.animation_index]
                self.mask = pygame.mask.from_surface(self.image)

            # movimiento
            dx = self.move_direction
            dy = 0
            self.vel_y = min(self.vel_y + 1, 10)
            dy += self.vel_y
            self.in_air = True

            # All platforms (tiles + rainbows)
            all_platforms = [rect for _, rect in world.tile_list]
            all_platforms.extend([arc.rect for arc in rainbows if not arc.falling])

            # X + colisiones
            self.rect.x += dx
            for platform in all_platforms:
                if platform.colliderect(self.rect):
                    for arc in rainbows:
                        if arc.rect == platform and arc.mask:
                            offset_x = self.rect.x - arc.rect.x
                            offset_y = self.rect.y - arc.rect.y
                            if self.mask.overlap(arc.mask, (offset_x, offset_y)):
                                self.dying = True
                                return
                    # Wall hit
                    self.move_direction *= -1
                    if dx > 0:
                        self.rect.right = platform.left
                    else:
                        self.rect.left = platform.right
                    break

            # Y + colisiones
            self.rect.y += dy
            for platform in all_platforms:
                if platform.colliderect(self.rect):
                    if self.vel_y < 0:
                        self.rect.top = platform.bottom
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        self.rect.bottom = platform.top
                        self.vel_y = 0
                        self.in_air = False
                    break

            # Girar
            self.move_counter += 1
            if abs(self.move_counter) > 50:
                self.move_direction *= -1
                self.move_counter *= -1
