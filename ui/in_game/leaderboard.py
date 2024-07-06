import tkinter as tk
from core.game_state.game_state import GameState

class Leaderboard:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Leaderboard", font=("Arial", 14, "bold")).pack()
        self.leaderboard_text = tk.Text(self.frame, height=10, width=30)
        self.leaderboard_text.pack(padx=5, pady=5)

    def update(self):
        self.leaderboard_text.delete(1.0, tk.END)
        leaderboard = self.game_state.get_leaderboard()
        for i, player in enumerate(leaderboard, 1):
            self.leaderboard_text.insert(tk.END, f"{i}. {player.user.username}: {player.score}\n")