import tkinter as tk
from core.game_state.game_state import GameState

class Snaptray:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Snaptray", font=("Arial", 14, "bold")).pack()
        self.dice_frame = tk.Frame(self.frame)
        self.dice_frame.pack(padx=5, pady=5)
        self.dice_labels = [tk.Label(self.dice_frame, text="", font=("Arial", 24), width=2, height=1) for _ in range(5)]
        for i, label in enumerate(self.dice_labels):
            label.grid(row=0, column=i, padx=5)

    def update(self):
        for i, value in enumerate(self.game_state.dice_values):
            self.dice_labels[i].config(text=str(value))