import os
import pygame
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from ui.in_game.in_game_ui import InGameUI
from ui.in_game.game_runner import GameRunner
from startup_menu import StartupMenu

def main():
    pygame.init()
    
    # Set up the game window
    screen_width = 1920
    screen_height = 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("•LIVEDICE [ F ]")

    # Run the startup menu
    startup_menu = StartupMenu(screen)
    human_players, ai_players = startup_menu.run()

    # Create the InGameUI instance with the selected number of players
    in_game_ui = InGameUI(human_players, ai_players)
    in_game_ui.initialize_game_log()

    # Run the game
    GameRunner.run_game(in_game_ui)

if __name__ == "__main__":
    main()