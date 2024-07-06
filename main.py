import pygame
import sys
from ui.in_game.in_game_ui import InGameUI
from core.game_state.game_state import GameState

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("•LIVEDICE [ F ] - In-Game UI")

# Initialize game state and UI
game_state = GameState()
in_game_ui = InGameUI(screen)

# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        in_game_ui.handle_event(event)

    # Update game state (this will be replaced with actual game logic later)
    game_state.update()

    # Update and draw the UI
    in_game_ui.update(game_state)
    screen.fill((255, 255, 255))  # White background
    in_game_ui.draw()
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()