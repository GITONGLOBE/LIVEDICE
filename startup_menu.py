import os
import pygame
import sys

class StartupMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(os.path.join("assets", "open-sauce-two", "OpenSauceTwo-Regular.ttf"), 36)
        self.human_players = 1
        self.ai_players = 1
        self.max_players = 4
        self.RED = (255, 0, 0)  # Define red color

    def draw(self):
        self.screen.fill(self.RED)  # Fill the screen with red
        
        title = self.font.render("•LIVEDICE [ F ]", True, (255, 255, 255))  # White text
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 50))

        human_text = self.font.render(f"Human Players: {self.human_players}", True, (255, 255, 255))  # White text
        self.screen.blit(human_text, (100, 150))

        ai_text = self.font.render(f"AI Players: {self.ai_players}", True, (255, 255, 255))  # White text
        self.screen.blit(ai_text, (100, 200))

        start_text = self.font.render("Start Game", True, (0, 0, 0))  # Black text
        start_rect = start_text.get_rect(center=(self.screen.get_width() // 2, 300))
        pygame.draw.rect(self.screen, (255, 255, 255), start_rect)  # White button
        self.screen.blit(start_text, start_rect)

        pygame.display.flip()


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if 100 <= event.pos[0] <= 300:
                    if 150 <= event.pos[1] <= 180:
                        self.human_players = (self.human_players % self.max_players) + 1
                    elif 200 <= event.pos[1] <= 230:
                        self.ai_players = (self.ai_players + 1) % (self.max_players + 1)  # Allow 0 to max_players
                elif self.screen.get_width() // 2 - 50 <= event.pos[0] <= self.screen.get_width() // 2 + 50:
                    if 280 <= event.pos[1] <= 320:
                        return True  # Start the game
        return False

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.handle_event(event):
                    return self.human_players, self.ai_players
            self.draw()
            clock.tick(30)