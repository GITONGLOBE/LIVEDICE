import pygame

class GameBoard:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        self.dice_font = pygame.font.Font(None, 36)

    def draw(self, screen):
        self.surface.fill((0, 100, 0))  # Green background
        screen.blit(self.surface, (0, 0))

    def handle_event(self, event):
        # Handle any game board specific events
        pass

    def update(self, game_state):
        # Draw dice based on game state
        for i, value in enumerate(game_state.dice_values):
            dice_surface = pygame.Surface((50, 50))
            dice_surface.fill((255, 255, 255))  # White background
            pygame.draw.rect(dice_surface, (0, 0, 0), dice_surface.get_rect(), 2)  # Black border
            text = self.dice_font.render(str(value), True, (0, 0, 0))
            text_rect = text.get_rect(center=dice_surface.get_rect().center)
            dice_surface.blit(text, text_rect)
            self.surface.blit(dice_surface, (50 + i * 60, 50))
    
class PlayerInfo:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)

    def handle_event(self, event):
        # Handle any player info specific events
        pass

    def update(self, game_state):
        # Update player info based on game state
        pass

    def render_player_info(self, screen, player):
        text = f"Player: {player.name} | Chips: {player.chips}"
        text_surface = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))


class ChatBox:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.messages = []
        self.font = pygame.font.Font(None, 18)

    def draw(self, screen):
        pygame.draw.rect(screen, (240, 240, 240), self.rect)
        for i, message in enumerate(self.messages[-5:]):
            text_surface = self.font.render(message, True, (0, 0, 0))
            screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5 + i * 20))

    def handle_event(self, event):
        # Handle chat input events
        pass

    def update(self, game_state):
        self.messages = game_state.chat_messages


class ControlPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.buttons = [
            pygame.Rect(x + 10, y + 10, 80, 30),
            pygame.Rect(x + 100, y + 10, 80, 30)
        ]
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        for button in self.buttons:
            pygame.draw.rect(screen, (150, 150, 150), button)
        
        bet_text = self.font.render("Bet", True, (0, 0, 0))
        screen.blit(bet_text, (self.buttons[0].x + 25, self.buttons[0].y + 5))
        
        challenge_text = self.font.render("Challenge", True, (0, 0, 0))
        screen.blit(challenge_text, (self.buttons[1].x + 5, self.buttons[1].y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons[0].collidepoint(event.pos):
                print("Bet button clicked")
            elif self.buttons[1].collidepoint(event.pos):
                print("Challenge button clicked")

    def update(self, game_state):
        # Update control panel based on game state
        pass


    