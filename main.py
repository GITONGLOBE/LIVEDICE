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
    result = startup_menu.run()
    
    # Debug: Show what we got
    print(f"DEBUG: startup_menu.run() returned: {result}")
    print(f"DEBUG: Type: {type(result)}")
    if isinstance(result, tuple):
        print(f"DEBUG: Length: {len(result)}")
        for i, val in enumerate(result):
            print(f"DEBUG:   [{i}] = {val} (type: {type(val).__name__})")
    
    # Handle different return formats
    if isinstance(result, tuple):
        if len(result) == 5:
            # New menu with full configuration
            human_players, ai_players, endgoal, ruleset, bot_difficulty = result
            
            # Type safety: ensure correct types
            human_players = int(human_players)
            ai_players = int(ai_players)
            endgoal = int(endgoal) if str(endgoal).isdigit() else 4000
            ruleset = str(ruleset)
            bot_difficulty = str(bot_difficulty)
            
            print()
            print("=" * 60)
            print("GAME CONFIGURATION:")
            print(f"  Human Players: {human_players}")
            print(f"  AI Players: {ai_players}")
            print(f"  End Goal: {endgoal}")
            print(f"  Ruleset: {ruleset}")
            print(f"  Bot Difficulty: {bot_difficulty}")
            print("=" * 60)
            print()
            
        elif len(result) == 2:
            # Old menu - only player counts
            human_players, ai_players = result
            endgoal = 4000
            ruleset = "STANDARD"
            bot_difficulty = "NORMAL"
            
            print()
            print("=" * 60)
            print("⚠️  OLD STARTUP MENU DETECTED")
            print("Using default configuration:")
            print(f"  Human Players: {human_players}")
            print(f"  AI Players: {ai_players}")
            print(f"  End Goal: {endgoal} (default)")
            print(f"  Ruleset: {ruleset} (default)")
            print(f"  Bot Difficulty: {bot_difficulty} (default)")
            print("=" * 60)
            print()
        else:
            print(f"ERROR: Unexpected number of return values: {len(result)}")
            print(f"Expected 2 or 5, got {len(result)}")
            print(f"Values: {result}")
            print()
            print("Please check your startup_menu.py return statement!")
            sys.exit(1)
    else:
        print(f"ERROR: Unexpected return type: {type(result)}")
        print(f"Expected tuple, got {result}")
        sys.exit(1)

    # Create the InGameUI instance with the selected game configuration
    print("Initializing game UI...")
    in_game_ui = InGameUI(human_players, ai_players, endgoal, ruleset, bot_difficulty)
    in_game_ui.initialize_game_log()

    # Run the game
    print("Starting game...")
    print()
    GameRunner.run_game(in_game_ui)

if __name__ == "__main__":
    main()
