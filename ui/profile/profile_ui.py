import tkinter as tk
from tkinter import ttk
from core.user_management import UserManager

class ProfileUI:
    def __init__(self, master, user_id):
        self.master = master
        self.user_id = user_id if user_id else "Unknown"
        self.user_manager = UserManager()
        
        self.profile_window = tk.Toplevel(self.master)
        self.profile_window.title("User Profile")
        self.profile_window.geometry("400x300")
        
        self.create_widgets()
        self.load_user_data()

    def load_user_data(self):
        if self.user_id != "Unknown":
            user_data = self.user_manager.get_user_data(self.user_id)
            if user_data:
                self.username_value.config(text=user_data.get('username', 'N/A'))
                self.email_value.config(text=user_data.get('email', 'N/A'))
                self.games_played_value.config(text=str(user_data.get('games_played', 0)))
                self.wins_value.config(text=str(user_data.get('wins', 0)))
        else:
            self.username_value.config(text="N/A")
            self.email_value.config(text="N/A")
            self.games_played_value.config(text="0")
            self.wins_value.config(text="0")

    def create_widgets(self):
        self.username_label = ttk.Label(self.profile_window, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        
        self.username_value = ttk.Label(self.profile_window, text="")
        self.username_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        self.email_label = ttk.Label(self.profile_window, text="Email:")
        self.email_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        
        self.email_value = ttk.Label(self.profile_window, text="")
        self.email_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        self.games_played_label = ttk.Label(self.profile_window, text="Games Played:")
        self.games_played_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        
        self.games_played_value = ttk.Label(self.profile_window, text="")
        self.games_played_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.wins_label = ttk.Label(self.profile_window, text="Wins:")
        self.wins_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        
        self.wins_value = ttk.Label(self.profile_window, text="")
        self.wins_value.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.edit_button = ttk.Button(self.profile_window, text="Edit Profile", command=self.edit_profile)
        self.edit_button.grid(row=4, column=0, columnspan=2, pady=20)

    def load_user_data(self):
        user_data = self.user_manager.get_user_data(self.user_id)
        if user_data:
            self.username_value.config(text=user_data.get('username', 'N/A'))
            self.email_value.config(text=user_data.get('email', 'N/A'))
            self.games_played_value.config(text=str(user_data.get('games_played', 0)))
            self.wins_value.config(text=str(user_data.get('wins', 0)))

    def edit_profile(self):
        # This method will be implemented in the future to allow users to edit their profile
        pass