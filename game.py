import pygame
from world import World
from rainbow import RainbowArc
from player import Player
from ui import RestartButtonText
from assets import (
    load_image,
    load_sound,
    load_font,
    load_frame_data,
    load_config
)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.scroll = 0
        self.last_fire_time = 0
        self.game_over = 0
        config = load_config()
        self.FIRE_COOLDOWN = config["gameplay"]["fire_cooldown_ms"]
        self.SCREEN_WIDTH = config["window"]["SCREEN_WIDTH"]
        self.SCREEN_HEIGHT = config["window"]["SCREEN_HEIGHT"]
        self.CAPTION = config["window"]["caption"]
        self.LEVEL1_DATA = config.get("LEVEL1DATA")
        self.TILE_SIZE = config["gameplay"]["tile_size"]
        self.FPS = config["gameplay"]["fps"]
        self.SCROLL_LIMIT_TOP = config["gameplay"]["scroll_limit_top"]
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.CAPTION)
        self.bg_img = load_image("img/sky.png")
        self.sun_img = load_image("img/sun.png")
        self.brick_img = load_image("img/brick.png")
        self.grass_img = load_image("img/grass.png")
        self.frame_data, self.sprite_sheet = load_frame_data("assets/config/entities.json", "img/entities.png")
        self.soundtrack = load_sound("sound/soundtrack.mp3")
        self.game_over_sound = load_sound("sound/gameover.mp3")
        self.sounds = {
            'jump': load_sound("sound/jump.mp3"),
            'rainbow': load_sound("sound/rainbow.mp3"),
            'enemykill': load_sound("sound/enemykill.mp3"),
            'playerkilled': load_sound("sound/playerkilled.mp3"),
        }
        self.howdy_font = load_font("fonts/Howdyfont.otf", 48)
        self.enemies = pygame.sprite.Group()
        self.rainbows = pygame.sprite.Group()
        self.player = Player(100, (len(self.LEVEL1_DATA) - 3) * self.TILE_SIZE, self.frame_data, self.sprite_sheet, self.soundtrack, self.sounds)
        self.world = World(self.LEVEL1_DATA, self.brick_img, self.grass_img, self.enemies, self.frame_data, self.sprite_sheet)
        self.restart_button = RestartButtonText(self.howdy_font, scale=6)


    def run(self):
        run = True
        self.soundtrack.stop()
        self.soundtrack.play(-1)
        print("Starting game loop...")
        while run:
            delta_time = self.clock.tick(self.FPS) / 1000.0
            self.screen.blit(self.bg_img, (0, 0))
            self.screen.blit(self.sun_img, (100, 100 + self.scroll))
            self.world.draw(self.screen, self.scroll)


            self.enemies.update(self.world, self.rainbows)
            for enemy in self.enemies:
                self.screen.blit(enemy.image, (enemy.rect.x, enemy.rect.y + self.scroll))

            self.rainbows.update(self.enemies)
            for arc in self.rainbows:
                self.screen.blit(arc.image, (arc.rect.x, arc.rect.y + self.scroll))

            prev_game_over = self.game_over
            self.game_over = self.player.update(
                self.screen, self.game_over, self.scroll, self.world,
                self.enemies, self.rainbows, delta_time
            )

            if self.game_over != 0 and prev_game_over == 0:
                self.soundtrack.stop()
                self.game_over_sound.play()

            if self.game_over != 0:
                msg = "Wanna try again?" if self.game_over == -1 else "Go again?"
                y_offset = 100 if self.game_over == 1 else 0
                self.restart_button.update_text(msg, self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + y_offset)
                self.restart_button.draw(self.screen)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and pygame.time.get_ticks() - self.last_fire_time > self.FIRE_COOLDOWN and self.game_over == 0:
                self.sounds['rainbow'].play()
                self.last_fire_time = pygame.time.get_ticks()
                arc_x = self.player.rect.right if self.player.direction == 1 else self.player.rect.left - 100
                arc = RainbowArc(arc_x, self.player.rect.top + 18, {
                    'enemykill': self.sounds['enemykill']
                })
                self.rainbows.add(arc)
                arc.update(self.enemies)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if self.game_over != 0 and self.restart_button.is_clicked(event):
                    self.player.reset(100, (len(self.LEVEL1_DATA) - 3) * self.TILE_SIZE, self.frame_data, self.sprite_sheet)
                    self.enemies.empty()
                    self.rainbows.empty()
                    self.world = World(self.LEVEL1_DATA, self.brick_img, self.grass_img, self.enemies, self.frame_data, self.sprite_sheet)
                    self.game_over = 0
                    self.game_over_sound.stop() 
                    self.soundtrack.stop()
                    self.soundtrack.play(-1)

            self.scroll = max(
                min(-(self.player.rect.centery - self.SCREEN_HEIGHT // 2), self.SCROLL_LIMIT_TOP),
                self.SCREEN_HEIGHT - len(self.LEVEL1_DATA) * self.TILE_SIZE
            )
            
            pygame.display.update()

    def __del__(self):
        print("Closing game.")
        pygame.quit()

    pygame.quit()
