import tkinter as tk
from core.game_state.game_state import GameState

class GameChat:
    def __init__(self, master, game_state: GameState):
        self.master = master
        self.game_state = game_state
        self.frame = tk.Frame(self.master, bd=2, relief=tk.RAISED)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.frame, text="Game Chat", font=("Arial", 14, "bold")).pack()
        self.chat_text = tk.Text(self.frame, height=10, width=40)
        self.chat_text.pack(padx=5, pady=5)
        self.chat_entry = tk.Entry(self.frame, width=30)
        self.chat_entry.pack(side=tk.LEFT, padx=5, pady=5)
        self.send_button = tk.Button(self.frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5, pady=5)

    def send_message(self):
        message = self.chat_entry.get()
        if message:
            current_player = self.game_state.players[self.game_state.current_player_index]
            self.game_state.add_chat_message(current_player.user, message)
            self.chat_entry.delete(0, tk.END)
            self.update()

    def update(self):
        self.chat_text.delete(1.0, tk.END)
        for message in self.game_state.game_chat:
            self.chat_text.insert(tk.END, f"{message['user']}: {message['message']}\n")
        self.chat_text.see(tk.END)