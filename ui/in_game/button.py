import os
import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, prefix_color, player_name_color, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.prefix_color = prefix_color
        self.player_name_color = player_name_color
        self.prefix_length = 0
        self.player_name_length = 0
        self.font_size = font_size

    def set_text(self, text):
        self.text = text

    def set_prefix_length(self, length):
        self.prefix_length = length

    def set_player_name_length(self, length):
        self.player_name_length = length

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.text_color, self.rect, 2)  # Add a border
        
        font = pygame.font.Font(os.path.join("assets", "open-sauce-two", "OpenSauceTwo-Regular.ttf"), self.font_size)
        
        if len(self.text) == 1:  # For single character buttons (like "?")
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        else:
            lines = self.text.split('\n')
            y_offset = 10
            for i, line in enumerate(lines):
                if i == 0:
                    # Draw prefix
                    prefix = line[:self.prefix_length]
                    prefix_surface = font.render(prefix, True, self.prefix_color)
                    prefix_rect = prefix_surface.get_rect(topleft=(self.rect.left + 10, self.rect.top + y_offset))
                    pygame.draw.rect(screen, (0, 0, 255), prefix_rect)  # Blue background
                    screen.blit(prefix_surface, prefix_rect)
                    
                    # Draw player name
                    player_name = line[self.prefix_length + 1:self.prefix_length + 1 + self.player_name_length]
                    player_surface = font.render(player_name, True, self.player_name_color)
                    screen.blit(player_surface, (self.rect.left + 10 + prefix_rect.width + 5, self.rect.top + y_offset))
                    
                    # Draw rest of the first line
                    rest_of_line = line[self.prefix_length + 1 + self.player_name_length:]
                    rest_surface = font.render(rest_of_line, True, self.text_color)
                    screen.blit(rest_surface, (self.rect.left + 10 + prefix_rect.width + 5 + player_surface.get_width() + 5, self.rect.top + y_offset))
                    
                    y_offset += font.get_linesize()
                else:
                    text_surface = font.render(line, True, self.text_color)
                    text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.top + y_offset + font.get_linesize() // 2))
                    screen.blit(text_surface, text_rect)
                    y_offset += font.get_linesize()

        if self.is_mouse_over():
            pygame.draw.rect(screen, self.text_color, self.rect, 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())