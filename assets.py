import pygame
import json


# Módulo responsalbe de cargar los recursos del juego

def load_image(path):
    return pygame.image.load(path).convert_alpha()

def load_sound(path):
    return pygame.mixer.Sound(path)

def load_font(path, size):
    return pygame.font.Font(path, size)

def load_frame_data(json_path, sprite_sheet_path):
    with open(json_path) as f:
        frame_data = json.load(f)
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
    return frame_data, sprite_sheet

def load_frame(name, frame_data, sprite_sheet):
    x, y, w, h = frame_data[name]
    frame = pygame.Surface((w, h), pygame.SRCALPHA)
    frame.blit(sprite_sheet, (0, 0), pygame.Rect(x, y, w, h))
    return frame

def load_config(path="assets/config/config.json"):
    with open(path, "r") as f:
        return json.load(f)
