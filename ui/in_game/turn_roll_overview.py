import tkinter as tk
from core.game_state.game_state import GameState

class TurnRollOverview:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Turn & Roll Overview", font=("Arial", 14, "bold")).pack()
        self.overview_label = tk.Label(self.frame, text="", font=("Arial", 12))
        self.overview_label.pack(padx=5, pady=5)

    def update(self):
        if self.game_state.players and len(self.game_state.players) > self.game_state.current_player_index:
            current_player = self.game_state.players[self.game_state.current_player_index]
            overview_text = f"Round: {self.game_state.round}\n"
            overview_text += f"Current Player: {current_player.user.username}\n"
            overview_text += f"Dice Roll: {', '.join(map(str, self.game_state.dice_values))}"
        else:
            overview_text = "No players in the game or invalid player index"
        
        self.overview_label.config(text=overview_text)