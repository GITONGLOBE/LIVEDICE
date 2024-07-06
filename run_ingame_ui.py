import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from ui.in_game.in_game_ui import InGameUI
from core.account.user import User
from core.game_state.game_state import GameState

def main():
    root = tk.Tk()
    root.title("LIVEDICE In-Game UI")
    root.geometry("1024x768")

    # Create a sample game state with some players
    game_state = GameState()
    
    # Add players to the game state
    game_state.add_player(User("Player1", "player1@example.com", "password1"))
    game_state.add_player(User("Player2", "player2@example.com", "password2"))
    game_state.add_player(User("Player3", "player3@example.com", "password3"))
    game_state.add_player(User("Player4", "player4@example.com", "password4"))

    # Initialize the game
    game_state.roll_dice()
    game_state.set_active_task("Roll three of a kind")
    game_state.add_log_entry("Game started")

    in_game_ui = InGameUI(root)
    in_game_ui.game_state = game_state

    def update_ui():
        in_game_ui.update()
        root.after(1000, update_ui)  # Update every second

    update_ui()
    root.mainloop()

if __name__ == "__main__":
    main()