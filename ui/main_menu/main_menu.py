import tkinter as tk
from tkinter import ttk
from ..profile.profile_ui import ProfileUI

class MainMenu:
    def __init__(self, master, game_state):
        self.master = master
        self.game_state = game_state
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(main_frame, text="LIVEDICE", font=("Arial", 24, "bold"))
        title_label.pack(pady=20)

        start_button = ttk.Button(main_frame, text="Start Game", command=self.start_game)
        start_button.pack(pady=10)

        self.profile_button = ttk.Button(main_frame, text="Profile", command=self.open_profile)
        self.profile_button.pack(pady=10)

        options_button = ttk.Button(main_frame, text="Options", command=self.open_options)
        options_button.pack(pady=10)

        quit_button = ttk.Button(main_frame, text="Quit", command=self.quit_game)
        quit_button.pack(pady=10)

    def start_game(self):
        # Implement game start logic
        print("Starting the game...")

    def open_profile(self):
        # Assuming you have a user_id in game_state. If not, you'll need to add it.
        ProfileUI(self.master, self.game_state.user_id)

    def open_options(self):
        # Implement options menu
        print("Opening options...")

    def quit_game(self):
        self.master.quit()