
import pygame

# Reinicar el juego con un botón de texto, accioanado por un evento de clic del ratón.
class RestartButtonText:
    def __init__(self, font, text="", position=(0, 0), scale=4,
                 color=(255, 255, 255), shadow_offset=(2, 2), shadow_color=(0, 0, 0)):

        self.font = font
        self.text = text
        self.color = color
        self.shadow_offset = shadow_offset
        self.shadow_color = shadow_color
        self.position = position
        self.scale = scale
        self.update_text(text)

    def update_text(self, new_text, center_x=None, center_y=None):
        self.text = new_text
        self.shadow_text = self.font.render(self.text, True, self.shadow_color)
        self.main_text = self.font.render(self.text, True, self.color)
        self.rect = self.main_text.get_rect(topleft=self.position)

        if center_x is not None and center_y is not None:
            self.rect.center = (center_x, center_y)
            self.position = self.rect.topleft

    def draw(self, surface):
        shadow_pos = (self.position[0] + self.shadow_offset[0],
                      self.position[1] + self.shadow_offset[1])
        surface.blit(self.shadow_text, shadow_pos)
        surface.blit(self.main_text, self.position)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
