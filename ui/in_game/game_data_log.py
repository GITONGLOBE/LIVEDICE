import tkinter as tk
from core.game_state.game_state import GameState

class GameDataLog:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Game Data Log", font=("Arial", 14, "bold")).pack()
        self.log_text = tk.Text(self.frame, height=10, width=40)
        self.log_text.pack(padx=5, pady=5)

    def update(self):
        self.log_text.delete(1.0, tk.END)
        for entry in self.game_state.game_log:
            self.log_text.insert(tk.END, f"{entry}\n")
        self.log_text.see(tk.END)