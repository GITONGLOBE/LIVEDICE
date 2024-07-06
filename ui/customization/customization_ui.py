import tkinter as tk
from tkinter import ttk, colorchooser
from ui.customization.theme_manager import ThemeManager

class CustomizationUI:
    def __init__(self, master):
        self.master = master
        self.theme_manager = ThemeManager()
        
        self.frame = ttk.Frame(self.master)
        self.frame.pack(padx=20, pady=20)

        self.create_widgets()

    def create_widgets(self):
        # Theme selection
        ttk.Label(self.frame, text="Select Theme:").grid(row=0, column=0, sticky="w", pady=5)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(self.frame, textvariable=self.theme_var)
        theme_combo['values'] = self.theme_manager.get_available_themes()
        theme_combo.grid(row=0, column=1, pady=5)
        theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        # Color customization
        ttk.Label(self.frame, text="Customize Colors:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Button(self.frame, text="Background Color", command=self.choose_bg_color).grid(row=1, column=1, pady=5)
        ttk.Button(self.frame, text="Text Color", command=self.choose_text_color).grid(row=2, column=1, pady=5)

        # Font customization
        ttk.Label(self.frame, text="Select Font:").grid(row=3, column=0, sticky="w", pady=5)
        self.font_var = tk.StringVar()
        font_combo = ttk.Combobox(self.frame, textvariable=self.font_var)
        font_combo['values'] = ("Arial", "Helvetica", "Times New Roman", "Courier", "Verdana")
        font_combo.grid(row=3, column=1, pady=5)
        font_combo.bind("<<ComboboxSelected>>", self.on_font_change)

        # Save button
        ttk.Button(self.frame, text="Save Changes", command=self.save_changes).grid(row=4, column=0, columnspan=2, pady=20)

    def on_theme_change(self, event):
        selected_theme = self.theme_var.get()
        self.theme_manager.apply_theme(selected_theme)

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color")
        if color[1]:
            self.theme_manager.set_background_color(color[1])

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose text color")
        if color[1]:
            self.theme_manager.set_text_color(color[1])

    def on_font_change(self, event):
        selected_font = self.font_var.get()
        self.theme_manager.set_font(selected_font)

    def save_changes(self):
        self.theme_manager.save_current_theme()
        tk.messagebox.showinfo("Success", "Customization settings saved successfully!")

def open_customization_ui(root):
    customization_window = tk.Toplevel(root)
    customization_window.title("LIVEDICE Customization")
    CustomizationUI(customization_window)