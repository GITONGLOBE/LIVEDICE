import tkinter as tk
from core.game_state.game_state import GameState

class ScoreTable:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Score Table", font=("Arial", 14, "bold")).pack()
        self.score_text = tk.Text(self.frame, height=10, width=30)
        self.score_text.pack(padx=5, pady=5)

    def update(self):
        self.score_text.delete(1.0, tk.END)
        for player in self.game_state.players:
            self.score_text.insert(tk.END, f"{player.user.username}: {player.score}\n")