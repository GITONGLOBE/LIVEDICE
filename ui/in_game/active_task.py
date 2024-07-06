import tkinter as tk
from core.game_state.game_state import GameState

class ActiveTask:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Active Task", font=("Arial", 14, "bold")).pack()
        self.task_label = tk.Label(self.frame, text="", font=("Arial", 12))
        self.task_label.pack(padx=5, pady=5)

    def update(self):
        self.task_label.config(text=self.game_state.active_task)