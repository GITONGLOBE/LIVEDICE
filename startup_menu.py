"""
LIVEDICE START MENU
Start menu for LIVEDICE game with game configuration options.
Uses 3-panel architecture similar to in-game UI.
"""

import os
import pygame
import sys


class StartupMenu:
    """Start menu with game configuration options"""
    
    def __init__(self, screen):
        """
        Initialize the startup menu.
        
        Args:
            screen: Pygame screen surface
        """
        self.screen = screen
        self.WINDOW_WIDTH = 1920
        self.WINDOW_HEIGHT = 1080
        
        # Setup colors
        self._setup_colors()
        
        # Setup sections
        self._setup_sections()
        
        # Setup fonts
        self._setup_fonts()
        
        # Load background image
        self.background_image = pygame.image.load(os.path.join("assets", "ld-f-logobg-1080.png")).convert()
        
        # Game settings with default values
        self.ruleset = "STANDARD"  # SIMPLE, STANDARD, ADVANCED
        self.endgoal = 4000  # 2000, 4000, 8000
        self.bot_difficulty = "NORMAL"  # EASY, NORMAL, HARD
        self.human_players = 1  # 1-4 or X for 0
        self.ai_players = 1  # 0-4
        
        # Hover states
        self.hover_button = None
        
    def _setup_colors(self):
        """Setup all color definitions"""
        self.colors = {
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255),
            "RED": (255, 0, 0),  # #FF0000 - Background
            "DARK_RED": (204, 0, 0),  # #CC0000 - Panel background
            "GREEN": (0, 255, 0),  # #00FF00 - Bright green for buttons
            "MEDIUM_GREEN": (0, 187, 0),  # #00BB00
            "BLUE": (0, 0, 255),  # #0000FF - Text color
            "DARK_BLUE": (0, 0, 170),  # #0000AA
        }
    
    def _setup_sections(self):
        """Setup all UI sections following 3-panel architecture"""
        self.sections = {
            # Main panels
            "STARTMENU_LEFTPANEL": pygame.Rect(0, 0, 660, 1080),
            "STARTMENU_MIDDLEPANEL": pygame.Rect(660, 0, 600, 1080),
            "STARTMENU_RIGHTPANEL": pygame.Rect(1260, 0, 660, 1080),
            
            # Middle panel overview section (top right of middle panel)
            "STARTMENU_GAME_OVERVIEW": pygame.Rect(880, 20, 340, 160),
            
            # Right panel sections
            "STARTMENU_GAME_SETTINGS": pygame.Rect(1280, 20, 620, 40),
            
            # Ruleset section
            "STARTMENU_RULESET_HEADER": pygame.Rect(1280, 60, 620, 20),
            "STARTMENU_RULESET_BUTTONS": pygame.Rect(1280, 80, 620, 80),
            "STARTMENU_RULESET_DESCRIPTION": pygame.Rect(1280, 160, 620, 80),
            
            # Endgoal section
            "STARTMENU_ENDGOAL_HEADER": pygame.Rect(1280, 240, 620, 20),
            "STARTMENU_ENDGOAL_BUTTONS": pygame.Rect(1280, 260, 620, 80),
            "STARTMENU_ENDGOAL_DESCRIPTION": pygame.Rect(1280, 340, 620, 60),
            
            # Bot difficulty section
            "STARTMENU_BOTDIFFICULTY_HEADER": pygame.Rect(1280, 400, 620, 20),
            "STARTMENU_BOTDIFFICULTY_BUTTONS": pygame.Rect(1280, 420, 620, 80),
            "STARTMENU_BOTDIFFICULTY_DESCRIPTION": pygame.Rect(1280, 500, 620, 80),
            
            # Playing players section
            "STARTMENU_PLAYINGPLAYERS_HEADER": pygame.Rect(1280, 580, 620, 20),
            "STARTMENU_PLAYINGPLAYERS_HUMAN": pygame.Rect(1280, 600, 620, 80),
            "STARTMENU_PLAYINGPLAYERS_BOTS": pygame.Rect(1280, 680, 620, 80),
            "STARTMENU_PLAYINGPLAYERS_DESCRIPTION": pygame.Rect(1280, 760, 620, 80),
            
            # Start button
            "STARTMENU_START_BUTTON": pygame.Rect(1280, 860, 620, 200),
        }
    
    def _setup_fonts(self):
        """Setup all font variations"""
        font_path = os.path.join("assets", "open-sauce-two")
        
        # Font style filenames
        font_files = {
            'black': 'OpenSauceTwo-Black.ttf',
            'bold': 'OpenSauceTwo-Bold.ttf',
            'semi_bold': 'OpenSauceTwo-SemiBold.ttf',
            'regular': 'OpenSauceTwo-Regular.ttf',
        }
        
        # Create fonts dictionary
        self.fonts = {}
        for style, filename in font_files.items():
            self.fonts[style] = {}
            for size in [10, 12, 14, 16, 18, 20, 24, 28, 36, 48]:
                self.fonts[style][size] = pygame.font.Font(os.path.join(font_path, filename), size)
        
        # Named font presets
        self.font_header_black = self.fonts['black'][16]
        self.font_header_semibold = self.fonts['semi_bold'][16]
        self.font_button_black = self.fonts['black'][36]
        self.font_button_semibold = self.fonts['semi_bold'][36]
        self.font_description_regular = self.fonts['regular'][14]
        self.font_title_black = self.fonts['black'][20]
        self.font_overview_semibold = self.fonts['semi_bold'][18]
    
    def draw(self):
        """Main draw method - renders entire start menu"""
        # Fill background with red
        self.screen.fill(self.colors["RED"])
        
        # Draw background image (centered)
        self.screen.blit(self.background_image, (0, 0))
        
        # Draw right panel background
        pygame.draw.rect(self.screen, self.colors["DARK_RED"], self.sections["STARTMENU_RIGHTPANEL"])
        
        # Draw game overview (in middle panel)
        self._draw_game_overview()
        
        # Draw game settings title
        self._draw_game_settings_title()
        
        # Draw all sections
        self._draw_ruleset_section()
        self._draw_endgoal_section()
        self._draw_bot_difficulty_section()
        self._draw_playing_players_section()
        self._draw_start_button()
        
        pygame.display.flip()
    
    def _draw_game_overview(self):
        """Draw real-time game overview in middle panel"""
        rect = self.sections["STARTMENU_GAME_OVERVIEW"]
        
        # Background
        pygame.draw.rect(self.screen, self.colors["DARK_RED"], rect)
        pygame.draw.rect(self.screen, self.colors["GREEN"], rect, 3)  # Border
        
        # Title
        x = rect.x + 10
        y = rect.y + 10
        self._draw_text_with_font("CURRENT SETTINGS", x, y, self.colors["GREEN"], self.fonts['black'][18])
        
        y += 30
        
        # Game configuration lines
        lines = [
            f"RULESET: {self.ruleset}",
            f"ENDGOAL: {self.endgoal} POINTS",
            f"BOT DIFF: {self.bot_difficulty}",
            f"PLAYERS: {self.human_players}H + {self.ai_players}B"
        ]
        
        for line in lines:
            self._draw_text_with_font(line, x, y, self.colors["WHITE"], self.fonts['semi_bold'][16])
            y += 24
    
    def _draw_text_with_font(self, text, x, y, color, font):
        """Helper function to draw text with a specific font"""
        text_surface = font.render(str(text), True, color)
        self.screen.blit(text_surface, (x, y))
        return text_surface.get_width()
    
    def _draw_game_settings_title(self):
        """Draw 'GAME SETTINGS' title"""
        rect = self.sections["STARTMENU_GAME_SETTINGS"]
        pygame.draw.rect(self.screen, self.colors["GREEN"], rect)
        
        x = rect.x + 10
        y = rect.y + 8
        self._draw_text_with_font("GAME", x, y, self.colors["BLUE"], self.font_title_black)
        x += self.font_title_black.size("GAME")[0]
        self._draw_text_with_font(" SETTINGS", x, y, self.colors["BLUE"], self.font_title_black)
    
    def _draw_ruleset_section(self):
        """Draw RULESET section"""
        # Header
        header_rect = self.sections["STARTMENU_RULESET_HEADER"]
        pygame.draw.rect(self.screen, self.colors["BLUE"], header_rect)
        x = header_rect.x + 10
        y = header_rect.y + 3
        self._draw_text_with_font("RULESET", x, y, self.colors["GREEN"], self.font_header_black)
        
        # Buttons
        button_rect = self.sections["STARTMENU_RULESET_BUTTONS"]
        button_width = (button_rect.width - 40) // 3
        button_height = button_rect.height - 20
        
        rulesets = ["SIMPLE", "STANDARD", "ADVANCED"]
        for i, ruleset in enumerate(rulesets):
            x = button_rect.x + 10 + i * (button_width + 10)
            y = button_rect.y + 10
            btn_rect = pygame.Rect(x, y, button_width, button_height)
            
            # Check if this is the selected button
            is_selected = (self.ruleset == ruleset)
            
            # Draw button
            color = self.colors["GREEN"] if is_selected else self.colors["RED"]
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, self.colors["GREEN"], btn_rect, 3)  # Border
            
            # Draw text
            text_color = self.colors["BLUE"] if is_selected else self.colors["WHITE"]
            text_surface = self.font_button_black.render(ruleset, True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Description
        desc_rect = self.sections["STARTMENU_RULESET_DESCRIPTION"]
        pygame.draw.rect(self.screen, self.colors["RED"], desc_rect)
        
        descriptions = {
            "SIMPLE": "ONLY ONES (100 PTS) AND FIVES (50 PTS)\nCAN BE STASHED. NO TRIPLES OR COMBOS.",
            "STANDARD": "INCLUDES TRIPLES, DOUBLE-SIXES,\nONES, AND FIVES. CLASSIC GAMEPLAY.",
            "ADVANCED": "ALL STANDARD RULES PLUS STREETS\nAND FULL HOUSES FOR BIG SCORES."
        }
        
        description = descriptions.get(self.ruleset, "")
        lines = description.split("\n")
        y_offset = desc_rect.y + 10
        for line in lines:
            self._draw_description_line(line, desc_rect.x + 10, y_offset)
            y_offset += 20
    
    def _draw_description_line(self, text, x, y):
        """Helper to draw a description line"""
        self._draw_text_with_font(text, x, y, self.colors["WHITE"], self.font_description_regular)
    
    def _draw_endgoal_section(self):
        """Draw ENDGOAL section"""
        # Header
        header_rect = self.sections["STARTMENU_ENDGOAL_HEADER"]
        pygame.draw.rect(self.screen, self.colors["BLUE"], header_rect)
        x = header_rect.x + 10
        y = header_rect.y + 3
        self._draw_text_with_font("ENDGOAL", x, y, self.colors["GREEN"], self.font_header_black)
        
        # Buttons
        button_rect = self.sections["STARTMENU_ENDGOAL_BUTTONS"]
        button_width = (button_rect.width - 40) // 3
        button_height = button_rect.height - 20
        
        endgoals = [2000, 4000, 8000]
        for i, endgoal in enumerate(endgoals):
            x = button_rect.x + 10 + i * (button_width + 10)
            y = button_rect.y + 10
            btn_rect = pygame.Rect(x, y, button_width, button_height)
            
            # Check if this is the selected button
            is_selected = (self.endgoal == endgoal)
            
            # Draw button
            color = self.colors["GREEN"] if is_selected else self.colors["RED"]
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, self.colors["GREEN"], btn_rect, 3)  # Border
            
            # Draw text
            text_color = self.colors["BLUE"] if is_selected else self.colors["WHITE"]
            text_surface = self.font_button_black.render(str(endgoal), True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Description
        desc_rect = self.sections["STARTMENU_ENDGOAL_DESCRIPTION"]
        pygame.draw.rect(self.screen, self.colors["RED"], desc_rect)
        
        descriptions = {
            2000: "QUICK GAME - FIRST TO 2000 WINS",
            4000: "STANDARD LENGTH - FIRST TO 4000 WINS",
            8000: "MARATHON MODE - FIRST TO 8000 WINS"
        }
        
        description = descriptions.get(self.endgoal, "")
        y_offset = desc_rect.y + 10
        self._draw_description_line(description, desc_rect.x + 10, y_offset)
    
    def _draw_bot_difficulty_section(self):
        """Draw BOT DIFFICULTY section"""
        # Header
        header_rect = self.sections["STARTMENU_BOTDIFFICULTY_HEADER"]
        pygame.draw.rect(self.screen, self.colors["BLUE"], header_rect)
        x = header_rect.x + 10
        y = header_rect.y + 3
        self._draw_text_with_font("BOT DIFFICULTY", x, y, self.colors["GREEN"], self.font_header_black)
        
        # Buttons
        button_rect = self.sections["STARTMENU_BOTDIFFICULTY_BUTTONS"]
        button_width = (button_rect.width - 40) // 3
        button_height = button_rect.height - 20
        
        difficulties = ["EASY", "NORMAL", "HARD"]
        for i, difficulty in enumerate(difficulties):
            x = button_rect.x + 10 + i * (button_width + 10)
            y = button_rect.y + 10
            btn_rect = pygame.Rect(x, y, button_width, button_height)
            
            # Check if this is the selected button
            is_selected = (self.bot_difficulty == difficulty)
            
            # Draw button
            color = self.colors["GREEN"] if is_selected else self.colors["RED"]
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, self.colors["GREEN"], btn_rect, 3)  # Border
            
            # Draw text
            text_color = self.colors["BLUE"] if is_selected else self.colors["WHITE"]
            text_surface = self.font_button_black.render(difficulty, True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Description
        desc_rect = self.sections["STARTMENU_BOTDIFFICULTY_DESCRIPTION"]
        pygame.draw.rect(self.screen, self.colors["RED"], desc_rect)
        
        descriptions = {
            "EASY": "BOTS PLAY CAUTIOUSLY, BANK\nOFTEN WITH LOW SCORES. BEGINNER-FRIENDLY.",
            "NORMAL": "BALANCED AI STRATEGY.\nMODERATE RISK-TAKING.",
            "HARD": "AGGRESSIVE BOTS TAKE RISKS FOR\nBIG SCORES. CHALLENGING GAMEPLAY."
        }
        
        description = descriptions.get(self.bot_difficulty, "")
        lines = description.split("\n")
        y_offset = desc_rect.y + 10
        for line in lines:
            self._draw_description_line(line, desc_rect.x + 10, y_offset)
            y_offset += 20
    
    def _draw_playing_players_section(self):
        """Draw PLAYING PLAYERS section"""
        # Header
        header_rect = self.sections["STARTMENU_PLAYINGPLAYERS_HEADER"]
        pygame.draw.rect(self.screen, self.colors["BLUE"], header_rect)
        x = header_rect.x + 10
        y = header_rect.y + 3
        self._draw_text_with_font("PLAYING PLAYERS", x, y, self.colors["GREEN"], self.font_header_black)
        
        # Human players buttons
        human_rect = self.sections["STARTMENU_PLAYINGPLAYERS_HUMAN"]
        
        # Label
        pygame.draw.rect(self.screen, self.colors["BLUE"], pygame.Rect(human_rect.x, human_rect.y, 620, 20))
        self._draw_text_with_font("HUMANS", human_rect.x + 10, human_rect.y + 3, self.colors["GREEN"], self.font_header_black)
        
        # Buttons
        button_width = (human_rect.width - 60) // 5
        button_height = human_rect.height - 30
        
        human_options = ["X", "1", "2", "3", "4"]
        for i, option in enumerate(human_options):
            x = human_rect.x + 10 + i * (button_width + 10)
            y = human_rect.y + 20
            btn_rect = pygame.Rect(x, y, button_width, button_height)
            
            # Check if this is the selected button
            is_selected = (option == "X" and self.human_players == 0) or (option != "X" and self.human_players == int(option))
            
            # Draw button
            color = self.colors["GREEN"] if is_selected else self.colors["RED"]
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, self.colors["GREEN"], btn_rect, 3)  # Border
            
            # Draw text
            text_color = self.colors["BLUE"] if is_selected else self.colors["WHITE"]
            text_surface = self.font_button_black.render(option, True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Bot players buttons
        bot_rect = self.sections["STARTMENU_PLAYINGPLAYERS_BOTS"]
        
        # Label
        pygame.draw.rect(self.screen, self.colors["BLUE"], pygame.Rect(bot_rect.x, bot_rect.y, 620, 20))
        self._draw_text_with_font("BOTS", bot_rect.x + 10, bot_rect.y + 3, self.colors["GREEN"], self.font_header_black)
        
        # Buttons
        bot_options = ["0", "1", "2", "3", "4"]
        for i, option in enumerate(bot_options):
            x = bot_rect.x + 10 + i * (button_width + 10)
            y = bot_rect.y + 20
            btn_rect = pygame.Rect(x, y, button_width, button_height)
            
            # Check if this is the selected button
            is_selected = (self.ai_players == int(option))
            
            # Draw button
            color = self.colors["GREEN"] if is_selected else self.colors["RED"]
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, self.colors["GREEN"], btn_rect, 3)  # Border
            
            # Draw text
            text_color = self.colors["BLUE"] if is_selected else self.colors["WHITE"]
            text_surface = self.font_button_black.render(option, True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            self.screen.blit(text_surface, text_rect)
        
        # Description
        desc_rect = self.sections["STARTMENU_PLAYINGPLAYERS_DESCRIPTION"]
        pygame.draw.rect(self.screen, self.colors["RED"], desc_rect)
        
        # Build description based on current selection
        human_text = "ONE HUMAN" if self.human_players == 1 else f"{['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR'][self.human_players]} HUMANS" if self.human_players > 0 else "ZERO HUMANS"
        
        bot_text = "ONE GO-BOT" if self.ai_players == 1 else f"{['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR'][self.ai_players]} GO-BOTS" if self.ai_players > 0 else "ZERO GO-BOTS"
        
        description = f"{human_text} AND {bot_text}\nWILL COMPETE IN THIS GAME"
        
        lines = description.split("\n")
        y_offset = desc_rect.y + 10
        for line in lines:
            self._draw_description_line(line, desc_rect.x + 10, y_offset)
            y_offset += 20
    
    def _draw_start_button(self):
        """Draw START GAME button"""
        btn_rect = self.sections["STARTMENU_START_BUTTON"]
        
        # Check if hovering
        is_hover = (self.hover_button == "START_GAME")
        
        # Draw button
        pygame.draw.rect(self.screen, self.colors["GREEN"], btn_rect)
        pygame.draw.rect(self.screen, self.colors["BLUE"], btn_rect, 5)  # Border
        
        # Draw text
        text_surface = self.fonts['black'][48].render("START GAME", True, self.colors["BLUE"])
        text_rect = text_surface.get_rect(center=btn_rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            True if game should start, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            
            # Check ruleset buttons
            button_rect = self.sections["STARTMENU_RULESET_BUTTONS"]
            button_width = (button_rect.width - 40) // 3
            button_height = button_rect.height - 20
            
            rulesets = ["SIMPLE", "STANDARD", "ADVANCED"]
            for i, ruleset in enumerate(rulesets):
                x = button_rect.x + 10 + i * (button_width + 10)
                y = button_rect.y + 10
                btn_rect = pygame.Rect(x, y, button_width, button_height)
                if btn_rect.collidepoint(pos):
                    self.ruleset = ruleset
                    return False
            
            # Check endgoal buttons
            button_rect = self.sections["STARTMENU_ENDGOAL_BUTTONS"]
            endgoals = [2000, 4000, 8000]
            for i, endgoal in enumerate(endgoals):
                x = button_rect.x + 10 + i * (button_width + 10)
                y = button_rect.y + 10
                btn_rect = pygame.Rect(x, y, button_width, button_height)
                if btn_rect.collidepoint(pos):
                    self.endgoal = endgoal
                    return False
            
            # Check bot difficulty buttons
            button_rect = self.sections["STARTMENU_BOTDIFFICULTY_BUTTONS"]
            difficulties = ["EASY", "NORMAL", "HARD"]
            for i, difficulty in enumerate(difficulties):
                x = button_rect.x + 10 + i * (button_width + 10)
                y = button_rect.y + 10
                btn_rect = pygame.Rect(x, y, button_width, button_height)
                if btn_rect.collidepoint(pos):
                    self.bot_difficulty = difficulty
                    return False
            
            # Check human player buttons
            human_rect = self.sections["STARTMENU_PLAYINGPLAYERS_HUMAN"]
            button_width = (human_rect.width - 60) // 5
            button_height = human_rect.height - 30
            
            human_options = ["X", "1", "2", "3", "4"]
            for i, option in enumerate(human_options):
                x = human_rect.x + 10 + i * (button_width + 10)
                y = human_rect.y + 20
                btn_rect = pygame.Rect(x, y, button_width, button_height)
                if btn_rect.collidepoint(pos):
                    self.human_players = 0 if option == "X" else int(option)
                    return False
            
            # Check bot player buttons
            bot_rect = self.sections["STARTMENU_PLAYINGPLAYERS_BOTS"]
            bot_options = ["0", "1", "2", "3", "4"]
            for i, option in enumerate(bot_options):
                x = bot_rect.x + 10 + i * (button_width + 10)
                y = bot_rect.y + 20
                btn_rect = pygame.Rect(x, y, button_width, button_height)
                if btn_rect.collidepoint(pos):
                    self.ai_players = int(option)
                    return False
            
            # Check start button
            if self.sections["STARTMENU_START_BUTTON"].collidepoint(pos):
                # Validate that we have at least one player
                if self.human_players + self.ai_players > 0:
                    return True
        
        return False
    
    def run(self):
        """
        Run the startup menu.
        
        Returns:
            Tuple of (human_players, ai_players, endgoal, ruleset, bot_difficulty)
        """
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.handle_event(event):
                    # CRITICAL FIX: Return in CORRECT order!
                    # Was: (human_players, ai_players, ruleset, endgoal, bot_difficulty)
                    # Now: (human_players, ai_players, endgoal, ruleset, bot_difficulty)
                    return (self.human_players, self.ai_players, 
                           self.endgoal, self.ruleset, self.bot_difficulty)
            
            self.draw()
            clock.tick(30)
