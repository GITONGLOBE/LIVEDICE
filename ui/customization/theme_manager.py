import json
import os

class ThemeManager:
    def __init__(self):
        self.current_theme = {
            "background_color": "#FFFFFF",
            "text_color": "#000000",
            "font": "Arial"
        }
        self.themes_file = "themes.json"
        self.load_themes()

    def load_themes(self):
        if os.path.exists(self.themes_file):
            with open(self.themes_file, "r") as f:
                self.themes = json.load(f)
        else:
            self.themes = {
                "default": self.current_theme,
                "dark": {
                    "background_color": "#333333",
                    "text_color": "#FFFFFF",
                    "font": "Arial"
                }
            }
            self.save_themes()

    def save_themes(self):
        with open(self.themes_file, "w") as f:
            json.dump(self.themes, f, indent=4)

    def get_available_themes(self):
        return list(self.themes.keys())

    def apply_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            # Here you would apply the theme to your UI
            # For example: update_ui_with_theme(self.current_theme)

    def set_background_color(self, color):
        self.current_theme["background_color"] = color
        # Apply the change: update_background_color(color)

    def set_text_color(self, color):
        self.current_theme["text_color"] = color
        # Apply the change: update_text_color(color)

    def set_font(self, font):
        self.current_theme["font"] = font
        # Apply the change: update_font(font)

    def save_current_theme(self):
        theme_name = f"custom_theme_{len(self.themes)}"
        self.themes[theme_name] = self.current_theme.copy()
        self.save_themes()

    def get_current_theme(self):
        return self.current_theme