import pygame
from assets import load_config
from enemy import Enemy



class World:
    def __init__(self, data, brick_img, grass_img, enemies_group, frame_data=None, sprite_sheet=None):
        self.tile_list = []
        self.brick_img = brick_img
        self.grass_img = grass_img
        config = load_config()
        TILE_SIZE = config["gameplay"]["tile_size"]

        for row_idx, row in enumerate(data):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE

                if tile == 1:
                    img = pygame.transform.scale(self.brick_img, (TILE_SIZE, TILE_SIZE))
                    self.tile_list.append((img, img.get_rect(x=x, y=y)))

                elif tile == 2:
                    img = pygame.transform.scale(self.grass_img, (TILE_SIZE, TILE_SIZE))
                    self.tile_list.append((img, img.get_rect(x=x, y=y)))

                elif tile == 3:
                    if frame_data and sprite_sheet:
                        enemy = Enemy(x, y + 15, frame_data, sprite_sheet)
                        enemies_group.add(enemy)

    def draw(self, screen, scroll):
        for img, rect in self.tile_list:
            screen.blit(img, (rect.x, rect.y + scroll))
