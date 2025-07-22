import pygame
from math import sin, cos, pi
from assets import (
    load_frame,
    load_config
)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, frame_data, sprite_sheet, soundtrack, sounds):
        super().__init__()
        config = load_config()
        self.SCREEN_WIDTH = config["window"]["SCREEN_WIDTH"]
        self.SCREEN_HEIGHT = config["window"]["SCREEN_HEIGHT"]
        self.sounds = sounds
        self.soundtrack = soundtrack
        self.frame_data = frame_data
        self.sprite_sheet = sprite_sheet
        self.reset(x, y, frame_data, sprite_sheet)
 

    def reset(self, x, y, frame_data, sprite_sheet):
        self.images_right = [load_frame(f'walkingR{n}', frame_data, sprite_sheet) for n in range(1, 7)]
        self.images_left = [load_frame(f'walkingL{n}', frame_data, sprite_sheet) for n in range(7, 13)]
        self.dead_img = pygame.transform.scale(pygame.image.load('img/goAgain.png'), (128, 256))
        self.image = self.images_right[0]
        self.rect = self.image.get_rect(x=x, y=y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True
        self.index = 0
        self.counter = 0
        self.invincible = True
        self.invincible_timer = 1000
        self.last_hit_time = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, screen, game_state, scroll, world, enemies, rainbows, delta_time):

        dx, dy = 0, 0
        walk_cooldown = 5
        limit_y = 525

        if self.invincible:
            if pygame.time.get_ticks() - self.last_hit_time > self.invincible_timer:
                self.invincible = False
        self.image.set_alpha(255)

        if game_state == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP] and not self.jumped and not self.in_air:
                if self.rect.top > limit_y:
                    self.vel_y = -15
                    self.jumped = True
                    self.sounds['jump'].play()
            if not key[pygame.K_UP]:
                self.jumped = False

            if key[pygame.K_LEFT]:
                dx -= 200 * delta_time 
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 200 * delta_time
                self.counter += 1
                self.direction = 1

            if not (key[pygame.K_LEFT] or key[pygame.K_RIGHT]):
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]
                self.mask = pygame.mask.from_surface(self.image)

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images_right)
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]
                self.mask = pygame.mask.from_surface(self.image)

            self.vel_y = min(self.vel_y + 1, 10)
            dy += self.vel_y
            was_in_air = self.in_air
            prev_y = self.rect.y

            # Colisiones en X
            prev_rect = self.rect.copy()
            self.rect.x += dx
            for tile_img, tile_rect in world.tile_list:
                if tile_rect.colliderect(self.rect):
                    if dx > 0 and prev_rect.right <= tile_rect.left:
                        self.rect.right = tile_rect.left
                    elif dx < 0 and prev_rect.left >= tile_rect.right:
                        self.rect.left = tile_rect.right

            # Colisiones en Y
            self.rect.y += dy
            if self.rect.top < limit_y:
                self.rect.top = limit_y
                self.vel_y = 0

            self.in_air = True
            if dy > 0:
                for tile_img, tile_rect in world.tile_list:
                    if self.rect.bottom > tile_rect.top and self.rect.bottom - dy <= tile_rect.top and self.rect.right > tile_rect.left and self.rect.left < tile_rect.right:
                        self.rect.bottom = tile_rect.top
                        self.vel_y = 0
                        self.in_air = False
                        break

            # Colisiones del arcoiris/arco
            player_bottom = self.rect.bottom
            for arc in rainbows:
                if arc.falling:
                    continue
                if self.rect.colliderect(arc.rect):
                    offset_x = arc.rect.x - self.rect.x
                    offset_y = arc.rect.y - self.rect.y
                    overlap = self.mask.overlap(arc.mask, (offset_x, offset_y))
                    if overlap:
                        found_landing_y = None
                        for x_off in range(0, self.width):
                            for y_off in range(self.height - 5, self.height):
                                px = self.rect.x + x_off
                                py = self.rect.y + y_off
                                arc_x = px - arc.rect.x
                                arc_y = py - arc.rect.y
                                if 0 <= arc_x < arc.mask.get_size()[0] and 0 <= arc_y < arc.mask.get_size()[1]:
                                    if arc.mask.get_at((int(arc_x), int(arc_y))):
                                        landing_y = arc.rect.y + arc_y
                                        if found_landing_y is None or landing_y < found_landing_y:
                                            found_landing_y = landing_y

                        if found_landing_y is not None and player_bottom >= found_landing_y:
                            self.rect.bottom = found_landing_y + 1
                            self.vel_y = 0
                            self.in_air = False
                            dy = 0
                            if was_in_air and prev_y < self.rect.y:
                                arc.falling = True
                                self.vel_y = -8
                                self.jumped = True
                            break

            # Colisiones/muertes con enemigos
            for enemy in enemies:
                if not enemy.dying and not self.invincible and self.rect.colliderect(enemy.rect):
                    self.sounds['playerkilled'].play()
                    return -1  # Muerto

        elif game_state == -1:
            self.image = self.dead_img
            t = pygame.time.get_ticks() % 10000
            angle = (t / 10000) * 2 * pi
            radius = 100
            cx = self.SCREEN_WIDTH // 2
            cy = self.SCREEN_HEIGHT // 2
            self.rect.x = int(cx + radius * cos(angle)) - self.rect.width // 2
            self.rect.y = int(cy + radius * sin(angle)) - self.rect.height // 2

        # Nivel completado
        if self.rect.top <= limit_y and game_state == 0:
            return 1
        
        # Dibujar jugador
        screen.blit(self.image, (self.rect.x, self.rect.y + scroll))
        
        return game_state
    
