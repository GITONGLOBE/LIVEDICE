import pygame
import os

class HexButton:
    def __init__(self, image_path, hover_image_path, bounds_image_path, position, selected_image=None):
        self.image = pygame.image.load(image_path)
        self.hover_image = pygame.image.load(hover_image_path)
        self.bounds_image = pygame.image.load(bounds_image_path)
        self.selected_image = pygame.image.load(selected_image) if selected_image else None
        self.rect = self.image.get_rect(topleft=position)
        self.mask = pygame.mask.from_surface(self.bounds_image)
        self.selected = False

    def draw(self, surface):
        if self.selected and self.selected_image:
            surface.blit(self.selected_image, self.rect)
        elif self.is_hovered():
            surface.blit(self.hover_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            rel_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            return self.mask.get_at(rel_pos)
        return False

    def is_clicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            rel_pos = (mouse_pos[0] - self.rect.x, mouse_pos[1] - self.rect.y)
            return self.mask.get_at(rel_pos)
        return False