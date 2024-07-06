import pygame
import os

class GameRoomUI:
    def __init__(self, screen):
        self.screen = screen
        self.table_image = pygame.image.load(os.path.join('assets', 'table.png'))
        self.chair_image = pygame.image.load(os.path.join('assets', 'chair.png'))
        self.player_avatar = pygame.image.load(os.path.join('assets', 'player_avatar.png'))
        
    def draw(self):
        # Draw background
        self.screen.fill((200, 200, 200))  # Light gray background
        
        # Draw table
        table_rect = self.table_image.get_rect(center=(400, 300))
        self.screen.blit(self.table_image, table_rect)
        
        # Draw chairs
        chair_positions = [
            (300, 200), (500, 200),  # Top chairs
            (300, 400), (500, 400),  # Bottom chairs
            (200, 300), (600, 300)   # Side chairs
        ]
        for pos in chair_positions:
            chair_rect = self.chair_image.get_rect(center=pos)
            self.screen.blit(self.chair_image, chair_rect)
        
        # Draw player avatars (example for 4 players)
        avatar_positions = [
            (300, 200), (500, 200),  # Top players
            (300, 400), (500, 400)   # Bottom players
        ]
        for pos in avatar_positions:
            avatar_rect = self.player_avatar.get_rect(center=pos)
            self.screen.blit(self.player_avatar, avatar_rect)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle click events if needed
                pass

    def update(self):
        # Update game room state if needed
        pass