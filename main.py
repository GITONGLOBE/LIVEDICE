import pygame
from ui.in_game.in_game_ui import InGameUI

def main():
    pygame.init()
    game_ui = InGameUI()
    game_ui.run()

if __name__ == "__main__":
    main()