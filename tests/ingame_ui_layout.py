import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("•LIVEDICE [ F ] - In-Game UI")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Define UI sections
sections = {
    "GAME SETTINGS": pygame.Rect(0, 0, 300, 100),
    "LEADERBOARD": pygame.Rect(0, 100, 300, 350),
    "REALTIME STASH": pygame.Rect(0, 450, 300, 150),
    "SNAPTRAY": pygame.Rect(300, 50, 600, 600),
    "ACTIVE TASK": pygame.Rect(900, 0, 300, 100),
    "SCORE TABLE": pygame.Rect(900, 100, 300, 350),
    "TURN & ROLL OVERVIEW": pygame.Rect(900, 450, 300, 150),
    "GAME CHAT": pygame.Rect(0, 600, 600, 200),
    "GAME DATA LOG": pygame.Rect(600, 600, 600, 200)
}

# Define colors for each section
section_colors = {
    "GAME SETTINGS": RED,
    "LEADERBOARD": GREEN,
    "REALTIME STASH": BLUE,
    "SNAPTRAY": YELLOW,
    "ACTIVE TASK": CYAN,
    "SCORE TABLE": MAGENTA,
    "TURN & ROLL OVERVIEW": ORANGE,
    "GAME CHAT": PURPLE,
    "GAME DATA LOG": (100, 100, 100)  # Dark gray
}

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a background color
    screen.fill(WHITE)

    # Draw each section
    for section, rect in sections.items():
        pygame.draw.rect(screen, section_colors[section], rect)
        font = pygame.font.Font(None, 24)
        text = font.render(section, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()