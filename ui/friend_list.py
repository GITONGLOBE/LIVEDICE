import tkinter as tk
from tkinter import ttk

class FriendList:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.friend_list_window = tk.Toplevel(self.master)
        self.friend_list_window.title("Friend List")
        self.friend_list_window.geometry("300x400")

        self.friend_listbox = tk.Listbox(self.friend_list_window)
        self.friend_listbox.pack(expand=True, fill='both', padx=10, pady=10)

        # Placeholder for friend list population
        self.populate_friend_list()

    def populate_friend_list(self):
        # This method should be implemented to populate the friend list
        # For now, we'll just add some dummy data
        dummy_friends = ["Friend 1", "Friend 2", "Friend 3"]
        for friend in dummy_friends:
            self.friend_listbox.insert(tk.END, friend)