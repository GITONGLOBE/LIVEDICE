import tkinter as tk
from core.game_state.game_state import GameState

class RealtimeStash:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Realtime Stash", font=("Arial", 14, "bold")).pack()
        self.stash_text = tk.Text(self.frame, height=5, width=30)
        self.stash_text.pack(padx=5, pady=5)

    def update(self):
        self.stash_text.delete(1.0, tk.END)
        if self.game_state.players and len(self.game_state.players) > self.game_state.current_player_index:
            current_player = self.game_state.players[self.game_state.current_player_index]
            self.stash_text.insert(tk.END, f"Player: {current_player.user.username}\n")
            self.stash_text.insert(tk.END, f"Stash: {', '.join(map(str, current_player.stash))}\n")
        else:
            self.stash_text.insert(tk.END, "No players in the game or invalid player index")