import pygame
import sys
import os
import time
import math
from typing import List, Tuple, Optional

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from core.game_state.game_state import GameStateManager
from games.livedice_f.livedice_f_rules import GameStateEnum
from core.account.user import User
from ui.in_game.button import Button
from ui.ui_interface import UIInterface
from ui.in_game.game_board import GameBoard
from ui.in_game.dice_renderer import DiceRenderer
from core.game_engine.go_bot_ai import BotAI

class InGameUI(UIInterface):
    def __init__(self, human_players, ai_players):
        pygame.init()
        self.WINDOW_WIDTH = 1920
        self.WINDOW_HEIGHT = 1080
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("• LIVEDICE [ F ]")

        self.human_players = human_players
        self.ai_players = ai_players
        self.game_state = None  # We'll initialize this later
        self.dice_rects: List[pygame.Rect] = []
        self.setup_ui_components()
        self.setup_fonts()
        self.setup_stash_section()
        self.setup_stashstash_section()
        self.setup_scoring_info_button()
        self.setup_rotating_image()

        self.setup_bank_button()
        self.setup_start_turn_button()
        self.setup_bust_button()
        self.setup_banked_turn_summary_button()


        self.buttons = {}

        self.dice_renderer = DiceRenderer(self.screen)

        self.dicecup_bounds = pygame.image.load(os.path.join("assets", "dicecup_button_bounds.png")).convert_alpha()
        self.dicecup_hover = pygame.image.load(os.path.join("assets", "dicecup_blue_button_hover.png")).convert_alpha()
        self.dicecup_mask = pygame.mask.from_surface(self.dicecup_bounds)
        self.dicecup_rect = self.dicecup_bounds.get_rect()
        self.dicecup_rect.topleft = (self.sections["DICECUP"].left, self.sections["DICECUP"].top)

        self.dicecupstartturn_bounds = self.dicecup_bounds.copy()
        self.dicecupstartturn_hover = pygame.image.load(os.path.join("assets", "dicecup_red_button_hover.png")).convert_alpha()
        self.dicecupstartturn_mask = self.dicecup_mask.copy()
        self.dicecupstartturn_rect = self.dicecup_rect.copy()
        self.use_start_turn_button = True

        # Initialize scrolling variables
        self.log_scroll_y = 0
        self.log_dragging = False
        self.log_auto_scroll = True
        self.leaderboard_scroll_y = 0
        self.leaderboard_dragging = False

        self.last_update_time = time.time()

        self.bot_thinking_message = ""
        self.bot_decision_message = ""

        self.setup_game()

    @property
    def show_green_dicecup(self):
        return self.game_state.current_game_state in [GameStateEnum.STASHCHOICE_STASHED_FULL, GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL]

    @property
    def show_blue_dicecup(self):
        return (self.game_state.can_roll_once or 
                (self.game_state.referee.can_roll() and
                self.game_state.current_player.stashed_dice_this_roll and
                not self.game_state.referee.can_roll_six_dice(
                    self.game_state.turn_started,
                    self.game_state.current_player.stashed_dice,
                    self.game_state.current_player.roll_count
                )) or 
                self.game_state.current_game_state in [
                    GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED,
                    GameStateEnum.STASHCHOICE_STASHED_PARTIAL
                ])

    @property
    def show_red_dicecup(self):
        return (not (self.show_blue_dicecup or self.show_green_dicecup) or 
                self.game_state.current_game_state in [
                    GameStateEnum.START_TURN,
                    GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH,
                    GameStateEnum.NEXTUP_READYUP
                ])

    def setup_ui_components(self):
        self.setup_colors()
        self.setup_sections()
        self.setup_scrollbars()
        self.setup_fonts()
        self.game_board = GameBoard(self.screen, self.sections["SNAPTRAY"])
        self.dice_renderer = DiceRenderer(self.screen)

    def setup_colors(self):
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.BUTTON_RED = (204, 0, 0)  # #CC0000
        self.GREEN = (0, 255, 0)
        self.BGGREEN = (0, 187, 0)  # #00BB00
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.CYAN = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)

    def setup_sections(self):
        self.sections = {
            # Panel Sections (background)
            "LEFTPANEL": pygame.Rect(0, 0, 480, 1080),
            "CENTRALPANEL": pygame.Rect(480, 0, 960, 1080),
            "RIGHTPANEL": pygame.Rect(1440, 0, 480, 1080),
            
            # Updated and New Sections
            "GAME_INFO": pygame.Rect(20, 20, 140, 200),
            "LEADERBOARD_STANDING": pygame.Rect(180, 20, 280, 200),
            "LEADERBOARD_SCORE": pygame.Rect(20, 240, 280, 400),
            "RT_STATS": pygame.Rect(320, 240, 140, 240),
            "BANK_BUTTON": pygame.Rect(320, 480, 140, 160),
            "STASH": pygame.Rect(20, 660, 440, 240),
            "STASHSTASH": pygame.Rect(20, 920, 440, 140),
            "SNAPTRAY": pygame.Rect(480, 0, 960, 1080),
            "DICECUP": pygame.Rect(1460, 20, 440, 400),
            "GAME_DATA_LOG_FRAME": pygame.Rect(1460, 440, 440, 620),
            "GAME_DATA_LOG": pygame.Rect(1480, 460, 400, 580),
            
            # Up Sections (foreground)
            "READY_UP_POPUP": pygame.Rect(800, 460, 320, 160),
            "TURN_BUST_POPUP": pygame.Rect(800, 460, 320, 160),
            "END_GAME_SUMMARY_POPUP": pygame.Rect(660, 290, 600, 500),
            "NOW_PLAYING_PLAYER_POPUP": pygame.Rect(520, 20, 300, 100)
        }
        self.section_colors = {
            "LEFTPANEL": (204, 0, 0),  # #CC0000
            "CENTRALPANEL": (255, 255, 255),  # White
            "RIGHTPANEL": (204, 0, 0),  # #CC0000
            "GAME_INFO": (0, 0, 255),  # #0000FF
            "LEADERBOARD_STANDING": (0, 0, 170),  # #0000AA
            "LEADERBOARD_SCORE": (0, 0, 255),  # #0000FF
            "RT_STATS": (0, 0, 255),  # #0000FF
            "BANK_BUTTON": (0, 0, 170),  # #0000AA
            "STASH": (0, 187, 0),  # #00BB00
            "STASHSTASH": (0, 187, 0),  # #00BB00
            "GAME_DATA_LOG_FRAME": (0, 0, 170),  # #0000AA
            "GAME_DATA_LOG": (0, 0, 255),  # #0000FF
            "READY_UP_POPUP": (0, 0, 255),  # #0000FF
            "TURN_BUST_POPUP": (0, 0, 255),  # #0000FF
            "END_GAME_SUMMARY_POPUP": (0, 0, 255),  # #0000FF
            "NOW_PLAYING_PLAYER_POPUP": (255, 0, 0),  # #FF0000
        }
        for key in self.sections:
            if key not in self.section_colors:
                self.section_colors[key] = self.RED

    def setup_scrollbars(self):
        self.dragging_scrollbar = False
        self.drag_start_y = 0
        self.leaderboard_dragging_scrollbar = False
        self.leaderboard_drag_start_y = 0

    def setup_fonts(self):
        font_path = os.path.join("assets", "open-sauce-two")
        font_sizes = [16, 18, 20, 22, 24, 28, 36]  # Added size 20
        font_styles = [
            'black', 'black_italic', 'bold', 'bold_italic', 'extra_bold',
            'extra_bold_italic', 'italic', 'light', 'light_italic', 'medium',
            'medium_italic', 'regular', 'semi_bold', 'semi_bold_italic'
        ]
        self.fonts = {style: {} for style in font_styles}

        for style, filename in [
            ('black', 'OpenSauceTwo-Black.ttf'),
            ('black_italic', 'OpenSauceTwo-BlackItalic.ttf'),
            ('bold', 'OpenSauceTwo-Bold.ttf'),
            ('bold_italic', 'OpenSauceTwo-BoldItalic.ttf'),
            ('extra_bold', 'OpenSauceTwo-ExtraBold.ttf'),
            ('extra_bold_italic', 'OpenSauceTwo-ExtraBoldItalic.ttf'),
            ('italic', 'OpenSauceTwo-Italic.ttf'),
            ('light', 'OpenSauceTwo-Light.ttf'),
            ('light_italic', 'OpenSauceTwo-LightItalic.ttf'),
            ('medium', 'OpenSauceTwo-Medium.ttf'),
            ('medium_italic', 'OpenSauceTwo-MediumItalic.ttf'),
            ('regular', 'OpenSauceTwo-Regular.ttf'),
            ('semi_bold', 'OpenSauceTwo-SemiBold.ttf'),
            ('semi_bold_italic', 'OpenSauceTwo-SemiBoldItalic.ttf')
        ]:
            for size in font_sizes:
                self.fonts[style][size] = pygame.font.Font(os.path.join(font_path, filename), size)
        
        # Set up specific font variables for different UI elements
        self.log_font = self.fonts['regular'][18]
        self.log_line_height = 22
        self.max_visible_lines = 24
        self.leaderboard_font = self.fonts['regular'][18]
        self.leaderboard_line_height = 22
        self.leaderboard_max_visible_lines = 24
        self.stash_font = self.fonts['regular'][16]
        self.button_font = self.fonts['bold'][18]
        self.title_font = self.fonts['bold'][24]

    def setup_game(self):
        self.game_state = GameStateManager(self, self.human_players, self.ai_players)
        self.game_state.set_active_task("Click START TURN to begin your turn")

    def setup_scoring_info_button(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        button_size = 60
        button_pos = (snaptray_rect.right - button_size - 10, snaptray_rect.bottom - button_size - 10)
        self.scoring_info_button = Button(button_pos[0], button_pos[1], button_size, button_size, "?", self.WHITE, self.BLACK, self.BLACK, self.BLACK, font_size=48)

    def setup_stash_section(self):
        stash_rect = self.sections["STASH"]
        self.stash_plank = StashPlank(pygame.Rect(stash_rect.left, stash_rect.top, stash_rect.width, stash_rect.height), self.fonts['regular'][16])

    def setup_stashstash_section(self):
        stashstash_rect = self.sections["STASHSTASH"]
        self.stash_stash = StashStash(pygame.Rect(stashstash_rect.left, stashstash_rect.top, stashstash_rect.width, stashstash_rect.height), self.fonts['regular'][16])

    def setup_rotating_image(self):
        image_path = os.path.join("assets", "PRECISE-G-154x154.png")
        dicecup_rect = self.sections["DICECUP"]
        pos = (dicecup_rect.left + 72, dicecup_rect.top + 177)
        pivot = (pos[0] + 77, pos[1] + 77)  # Center of the 154x154 image
        self.rotating_image = RotatingImage(image_path, pos, pivot)

    def setup_bank_button(self):
        leaderboard_score_rect = self.sections["LEADERBOARD_SCORE"]
        self.bank_button = Button(
            leaderboard_score_rect.centerx - 100, leaderboard_score_rect.centery,
            200, 40, "BANK", (0, 255, 0), (0, 0, 0), (0, 255, 0), (0, 0, 0)
        )

    def setup_start_turn_button(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        self.start_turn_button = Button(
            snaptray_rect.right - 120, snaptray_rect.top + 10,
            110, 30, "START TURN", (0, 0, 255), (255, 255, 255), (0, 0, 255), (255, 255, 255)
        )

    def setup_bust_button(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        self.bust_button = Button(
            snaptray_rect.centerx - 100, snaptray_rect.centery + 100,
            200, 40, "END BUSTED TURN", (255, 0, 0), (255, 255, 255), (255, 0, 0), (255, 255, 255)
        )

    def setup_banked_turn_summary_button(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        self.banked_turn_summary_button = Button(
            snaptray_rect.centerx - 100, snaptray_rect.centery + 100,
            200, 40, "END BANKED TURN", (0, 255, 0), (0, 0, 0), (0, 255, 0), (0, 0, 0)
        )

    def initialize_game_log(self):
        self.game_state.add_log_entry(f"{self.game_state.current_player.user.username} starts the game")

    def update(self):
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        self.game_board.update(dt)
        self.rotating_image.update()

        if self.game_state.current_player.is_bot():
            if not hasattr(self, 'bot_turn_in_progress'):
                self.bot_turn_in_progress = False

            if not self.bot_turn_in_progress:
                self.bot_turn_in_progress = True
                self.bot_turn()
        else:
            self.bot_turn_in_progress = False

        if self.game_state.check_game_over():
            self.end_game()
        
        if not self.bot_turn_in_progress:
            self.update_bank_button()
            self.update_start_turn_button()
            self.update_bust_button()
            self.update_banked_turn_summary_button()
            self.stash_plank.update(self.game_state, self.game_state.referee)
            self.stash_stash.update(self.game_state)
            self.update_leaderboard_scroll()

    def update_bank_button(self):
        current_state = self.game_state.current_game_state
        referee = self.game_state.referee

        if current_state in [GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS, 
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED,
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL, 
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_FULL,
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH,
                            GameStateEnum.STASHCHOICE_STASHED_ALL, 
                            GameStateEnum.STASHCHOICE_STASHED_PARTIAL]:
            self.bank_button.set_text(referee.get_bank_button_text())
            self.bank_button.enabled = True
        else:
            self.bank_button.enabled = False

    def update_start_turn_button(self):
        current_state = self.game_state.current_game_state

        if current_state in [GameStateEnum.START_TURN, GameStateEnum.NEXTUP_READYUP]:
            self.start_turn_button.set_text(f"LET'S GO {self.game_state.current_player.user.username}!")
            self.start_turn_button.enabled = True
        elif current_state == GameStateEnum.NEW_STASH:
            self.start_turn_button.set_text("ROLL NOW FOR NEW STASH!")
            self.start_turn_button.enabled = True
        else:
            self.start_turn_button.enabled = False

    def update_stash_button(self):
        current_state = self.game_state.current_game_state
        referee = self.game_state.referee

        if current_state in [GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL, 
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_FULL]:
            if self.game_state.selected_dice:
                self.stash_plank.set_button_text(referee.get_stash_button_text())
                self.stash_plank.button_enabled = True
            else:
                self.stash_plank.set_button_text("")
                self.stash_plank.button_enabled = False
        else:
            self.stash_plank.set_button_text("")
            self.stash_plank.button_enabled = False

    def update_bust_button(self):
        self.bust_button.enabled = self.game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY

    def update_banked_turn_summary_button(self):
        self.banked_turn_summary_button.enabled = self.game_state.current_game_state == GameStateEnum.BANKED_TURN_SUMMARY

    def update_stash_stash_button(self):
        current_state = self.game_state.current_game_state

        if current_state == GameStateEnum.STASHCHOICE_STASHED_FULL:
            self.stash_stash.set_button_text("CLICK HERE TO MOVE FULL STASH INTO STASHSTASH")
            self.stash_stash.button_enabled = True
        else:
            self.stash_stash.button_enabled = False

    def update_leaderboard(self):
        current_player = self.game_state.current_player
        turn_score = self.game_state.real_time_counters.turn_vscore
        rolls = self.game_state.real_time_counters.turn_rolls_var
        stashes = self.game_state.real_time_counters.stashstashtimes_vscore
        
        current_player.record_turn(self.game_state.current_turn_number, turn_score, rolls, stashes)
        self.game_state.total_turns += 1
        
        log_entry = f"{current_player.user.username} scored {turn_score} points in turn {self.game_state.current_turn_number} with {rolls} rolls and {stashes} stashes"
        self.game_state.add_log_entry(log_entry)

    def update_leaderboard_scroll(self):
        visible_lines = (self.sections["LEADERBOARD_SCORE"].height - 60) // self.leaderboard_line_height
        total_lines = max(1, self.game_state.total_turns)
        self.leaderboard_scroll_y = max(0, total_lines - visible_lines)

    def draw(self):
        self.screen.fill(self.WHITE)
        
        # Draw background panel sections
        for section in ["LEFTPANEL", "CENTRALPANEL", "RIGHTPANEL"]:
            pygame.draw.rect(self.screen, self.section_colors[section], self.sections[section])
        
        # Draw other sections
        for section, rect in self.sections.items():
            if section not in ["LEFTPANEL", "CENTRALPANEL", "RIGHTPANEL", "READY_UP_POPUP", "TURN_BUST_POPUP", "END_GAME_SUMMARY_POPUP", "NOW_PLAYING_PLAYER_POPUP"]:
                pygame.draw.rect(self.screen, self.section_colors[section], rect)
                self.draw_section_content(section, rect)
        
        self.draw_bust_box()

        if self.bot_thinking_message:
            self.draw_bot_message(self.bot_thinking_message, (0, 0, 255))  # Blue color
            self.bot_thinking_message = ""  # Clear the message after drawing
        if self.bot_decision_message:
            self.draw_bot_message(self.bot_decision_message, (255, 0, 0))  # Red color
            self.bot_decision_message = ""  # Clear the message after drawing

        gameloop_text = f"CURRENT GAMELOOP: {self.game_state.current_game_state.name}"
        gameloop_font = self.fonts['regular'][24]
        gameloop_surface = gameloop_font.render(gameloop_text, True, (255, 0, 0))  # Red color
        gameloop_rect = gameloop_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 20))
        self.screen.blit(gameloop_surface, gameloop_rect)
        
        self.bank_button.draw(self.screen)
        self.start_turn_button.draw(self.screen)

        if self.game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY:
            self.bust_button.draw(self.screen)

        elif self.game_state.current_game_state == GameStateEnum.BANKED_TURN_SUMMARY:
            self.banked_turn_summary_button.draw(self.screen)

        self.scoring_info_button.draw(self.screen)
        
        # Draw foreground popup sections
        for section in ["READY_UP_POPUP", "TURN_BUST_POPUP", "END_GAME_SUMMARY_POPUP", "NOW_PLAYING_PLAYER_POPUP"]:
            if self.should_draw_popup(section):
                pygame.draw.rect(self.screen, self.section_colors[section], self.sections[section])
                self.draw_section_content(section, self.sections[section])

        pygame.display.update()
    
    def should_draw_popup(self, popup_name):
        if popup_name == "READY_UP_POPUP":
            return self.game_state.current_game_state == GameStateEnum.NEXTUP_READYUP
        elif popup_name == "TURN_BUST_POPUP":
            return self.game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY
        elif popup_name == "END_GAME_SUMMARY_POPUP":
            return self.game_state.check_game_over()
        elif popup_name == "NOW_PLAYING_PLAYER_POPUP":
            return True  # Always show the current player
        return False

    def draw_scrollable_log(self, rect: pygame.Rect):
        MAX_LOG_ENTRIES = 100
        log_surface = pygame.Surface((rect.width, rect.height))
        log_surface.fill(self.section_colors["GAME_DATA_LOG"])

        formatted_log = [self.format_log_entry(entry) for entry in self.game_state.game_log[-MAX_LOG_ENTRIES:]]

        y = 0
        entry_heights = []
        for entry in formatted_log:
            entry_height = self.get_entry_height(entry, rect.width - 20)
            entry_heights.append(entry_height)
            y += entry_height

        total_height = sum(entry_heights)
        visible_height = rect.height
        max_scroll = max(0, total_height - visible_height)

        self.log_scroll_y = min(max_scroll, self.log_scroll_y)

        y = -self.log_scroll_y
        for entry, height in zip(formatted_log, entry_heights):
            if y + height > 0 and y < visible_height:
                self.render_log_line(log_surface, entry, 10, y)
            y += height

        if total_height > visible_height:
            scrollbar_height = (visible_height / total_height) * visible_height
            scrollbar_pos = (self.log_scroll_y / max_scroll) * (visible_height - scrollbar_height)
            pygame.draw.rect(log_surface, self.WHITE, (rect.width - 10, scrollbar_pos, 10, scrollbar_height))

        self.screen.blit(log_surface, rect)

    def get_entry_height(self, entry, max_width):
        words = entry.split()
        x = 0
        lines = 1
        for word in words:
            if word.startswith("<DICE>") and word.endswith("</DICE>"):
                word_width = 36
            else:
                word_width = self.log_font.size(word)[0]
            if x + word_width > max_width:
                lines += 1
                x = word_width
            else:
                x += word_width + 5
        return lines * (self.log_font.get_height() + 5) + 15  # Increased padding between entries
        
    def render_log_line(self, surface, line, x, y):
        words = line.split()
        start_x = x
        max_width = surface.get_width() - 30
        line_height = self.log_font.get_height() + 5

        for i, word in enumerate(words):
            if word.startswith("<DICE>") and word.endswith("</DICE>"):
                dice_info = word[6:-7]
                dice_width = 36
                if x + dice_width > max_width:
                    x = start_x
                    y += line_height
                x = self.dice_renderer.render_dice_in_log(surface, dice_info, x, y)
            elif word.startswith("<prefix>") and word.endswith("</prefix>"):
                prefix = word[8:-9]
                word_surface = self.log_font.render(prefix, True, self.WHITE)
                word_width = word_surface.get_width()
                prefix_rect = pygame.Rect(x, y, word_width, self.log_font.get_height())
                pygame.draw.rect(surface, self.BLUE, prefix_rect)
                surface.blit(word_surface, (x, y))
                x += word_width + 5
            elif word.startswith("<player>") and word.endswith("</player>") or word.startswith("@GO-BOT-"):
                player = word[8:-9] if word.startswith("<player>") else word
                word_surface = self.log_font.render(player, True, self.GREEN)
                word_width = word_surface.get_width()
                surface.blit(word_surface, (x, y))
                x += word_width + 5
            elif word.startswith("<green>") and word.endswith("</green>"):
                green_text = word[7:-8]
                word_surface = self.log_font.render(green_text, True, self.GREEN)
                word_width = word_surface.get_width()
                surface.blit(word_surface, (x, y))
                x += word_width + 5
            else:
                word_surface = self.log_font.render(word, True, self.BLACK)
                word_width = word_surface.get_width()
                if x + word_width > max_width:
                    x = start_x
                    y += line_height
                surface.blit(word_surface, (x, y))
                x += word_width + 5

        return y + line_height
    
    def wrap_text(self, text, max_width, return_lines=False):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            if word.startswith("<dice>") and word.endswith("</dice>"):
                word_width = self.dice_size['log'] + 1  # Minimal spacing between dice
            else:
                word_width = self.log_font.size(word + " ")[0]
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(" ".join(current_line))

        return lines if return_lines else len(lines)

    def handle_log_scroll(self, event):
        if event.button == 4:  # Scroll up
            self.log_scroll_y = max(0, self.log_scroll_y - self.log_line_height)
        elif event.button == 5:  # Scroll down
            formatted_log = [self.format_log_entry(entry) for entry in self.game_state.game_log]
            total_height = sum(len(self.wrap_text(entry, self.sections["GAME_DATA_LOG"].width - 20, return_lines=True)) for entry in formatted_log)
            max_scroll = max(0, total_height * self.log_line_height - self.sections["GAME_DATA_LOG"].height)
            self.log_scroll_y = min(max_scroll, self.log_scroll_y + self.log_line_height)
        self.log_auto_scroll = False

    def scroll_log_to_bottom(self):
        formatted_log = [self.format_log_entry(entry) for entry in self.game_state.game_log]
        total_height = sum(len(self.wrap_text(entry, self.sections["GAME_DATA_LOG"].width - 20, return_lines=True)) for entry in formatted_log)
        max_scroll = max(0, total_height * self.log_line_height - self.sections["GAME_DATA_LOG"].height)
        self.log_scroll_y = max_scroll

    def scroll_log_up(self):
        self.log_auto_scroll = False
        self.log_scroll_y = min(0, self.log_scroll_y + 20)

    def scroll_log_down(self):
        visible_height = self.sections["GAME_DATA_LOG"].height
        total_height = sum(self.wrap_text(entry, self.sections["GAME_DATA_LOG"].width - 20) for entry in self.game_state.game_log)
        max_scroll = max(0, total_height - visible_height)
        self.log_scroll_y = max(-max_scroll, self.log_scroll_y - 20)
        if self.log_scroll_y == -max_scroll:
            self.log_auto_scroll = True

    def handle_log_drag(self, mouse_pos):
        if self.log_dragging:
            rect = self.sections["GAME_DATA_LOG"]
            visible_height = rect.height
            formatted_log = [self.format_log_entry(entry) for entry in self.game_state.game_log]
            total_height = sum(len(self.wrap_text(entry, rect.width - 20, return_lines=True)) for entry in formatted_log) * self.log_line_height
            max_scroll = max(0, total_height - visible_height)
            
            drag_pos = mouse_pos[1] - rect.top
            scroll_ratio = drag_pos / rect.height
            self.log_scroll_y = int(scroll_ratio * max_scroll)
            self.log_scroll_y = min(max_scroll, max(0, self.log_scroll_y))

    def handle_leaderboard_drag(self, mouse_pos):
        if self.leaderboard_dragging:
            rect = self.sections["LEADERBOARD_SCORE"]
            visible_height = rect.height - 60  # Adjust for header
            total_height = self.game_state.total_turns * self.leaderboard_line_height
            max_scroll = max(0, total_height - visible_height)
            
            drag_pos = mouse_pos[1] - rect.top - 60  # Adjust for header
            scroll_ratio = drag_pos / (rect.height - 60)
            self.leaderboard_scroll_y = int(scroll_ratio * max_scroll)
            self.leaderboard_scroll_y = min(max_scroll, max(0, self.leaderboard_scroll_y))

    def draw_rt_stats(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, self.section_colors["RT_STATS"], rect)
        
        title_font = self.fonts['bold'][24]
        normal_font = self.fonts['regular'][18]
        small_font = self.fonts['regular'][16]
        
        # RT_STATS Status
        status_text = f"Game State: {self.game_state.current_game_state.name}"
        self.draw_text_on_surface(status_text, self.screen, (rect.left + 10, rect.top + 10), self.BLACK, 'bold', 24)
        
        # Current Turn Info
        current_player = self.game_state.current_player
        turn_info = [
            f"Player: {current_player.user.username}",
            f"Turn: {self.game_state.current_turn_number}",
            f"Rolls: {current_player.roll_count}",
            f"Stash: {current_player.get_stash_score()} pts ({len(current_player.stashed_dice)} dice)",
            f"Stash Stash: {current_player.stash_stash} pts ({current_player.full_stashes_moved_this_turn} stashes)",
            f"Turn Score: {self.game_state.real_time_counters.turn_vscore} pts",
            f"Total Banked Stashes: {current_player.get_total_banked_full_stashes()}"
        ]
        
        for i, info in enumerate(turn_info):
            self.draw_text_on_surface(info, self.screen, (rect.left + 10, rect.top + 40 + i * 25), self.BLACK, 'regular', 16)


    def draw_game_info(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, self.section_colors["GAME_INFO"], rect)
        
        font = self.fonts['regular'][24]
        
        info_text = [
            "• LIVEDICE [ IF ]",
            "",
            "COREGAME",
            "6DICE",
            "FIRST TO 4OOO"
        ]
        
        for i, line in enumerate(info_text):
            text_surface = font.render(line, True, self.BLACK)
            text_rect = text_surface.get_rect(centerx=rect.centerx, top=rect.top + 20 + i * 30)
            self.screen.blit(text_surface, text_rect)

    def draw_bank_button(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, self.section_colors["BANK_BUTTON"], rect)
        # The actual button is drawn separately, this is just the section for it

    def draw_stash(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, self.section_colors["STASH"], rect)
        self.stash_plank.draw(self.screen)

    def draw_stashstash(self, rect: pygame.Rect):
        pygame.draw.rect(self.screen, self.section_colors["STASHSTASH"], rect)
        self.stash_stash.draw(self.screen)

    def draw_leaderboard_score(self, rect: pygame.Rect):
        leaderboard_surface = pygame.Surface((rect.width, rect.height))
        leaderboard_surface.fill(self.section_colors["LEADERBOARD_SCORE"])

        header_font = self.fonts['bold'][24]
        normal_font = self.fonts['regular'][24]
        small_font = self.fonts['regular'][18]
        large_font = self.fonts['bold'][36]

        current_player = self.game_state.current_player
        
        header_text = header_font.render("CURRENT PLAYER", True, self.BLACK)
        leaderboard_surface.blit(header_text, (10, 5))

        player_name_text = normal_font.render(current_player.user.username, True, (0, 255, 0))
        leaderboard_surface.blit(player_name_text, (10, 35))

        column_widths = [40, 100, 40, 40]
        pygame.draw.line(leaderboard_surface, self.BLACK, (0, 60), (rect.width, 60), 2)
        
        headers = ["TURN", "SCORE", "R", "S"]
        x_offset = 10
        for header, width in zip(headers, column_widths):
            self.draw_text_on_surface(header, leaderboard_surface, (x_offset, 70), self.BLACK, 'regular', 18)
            x_offset += width

        visible_lines = (rect.height - 140) // self.leaderboard_line_height
        total_turns = self.game_state.current_turn_number
        start_index = max(1, total_turns - visible_lines + 1)
        end_index = total_turns + 1

        for turn in range(start_index, end_index):
            y = 100 + (turn - start_index) * self.leaderboard_line_height
            turn_data = current_player.get_turn_score(turn)
            
            x_offset = 10
            self.draw_text_on_surface(turn, leaderboard_surface, (x_offset + column_widths[0] // 2, y), self.BLACK, 'regular', 18, 'center')
            x_offset += column_widths[0]
            
            self.draw_text_on_surface(turn_data["SCORE"], leaderboard_surface, (x_offset + 5, y), self.WHITE, 'regular', 24)
            x_offset += column_widths[1]
            self.draw_text_on_surface(turn_data["ROLLS"], leaderboard_surface, (x_offset + column_widths[2] // 2, y), self.BLACK, 'regular', 18, 'center')
            x_offset += column_widths[2]
            self.draw_text_on_surface(turn_data["STASHES"], leaderboard_surface, (x_offset + column_widths[3] // 2, y), self.BLACK, 'regular', 18, 'center')

        # Total score
        total_score = current_player.get_total_score()
        pygame.draw.line(leaderboard_surface, self.BLACK, (0, rect.height - 40), (rect.width, rect.height - 40), 2)
        self.draw_text_on_surface(f"TOTAL: {total_score}", leaderboard_surface, (10, rect.height - 30), self.WHITE, 'bold', 36)

        self.screen.blit(leaderboard_surface, rect)

    def draw_leaderboard_standing(self, rect: pygame.Rect):
        standing_surface = pygame.Surface((rect.width, rect.height))
        standing_surface.fill(self.section_colors["LEADERBOARD_STANDING"])

        header_font = self.fonts['bold'][24]
        normal_font = self.fonts['regular'][24]

        header_text = header_font.render("STANDINGS", True, self.BLACK)
        standing_surface.blit(header_text, (10, 5))

        players_sorted = sorted(self.game_state.players, key=lambda p: p.get_total_score(), reverse=True)
        for i, player in enumerate(players_sorted):
            y = 45 + i * 30
            rank_text = f"{i+1}."

            self.draw_text_on_surface(rank_text, standing_surface, (10, y), self.BLACK, 'regular', 24)
            self.draw_text_on_surface(player.user.username, standing_surface, (40, y), (0, 255, 0) if player.user.username.startswith("@") else self.BLACK, 'regular', 24)
            self.draw_text_on_surface(str(player.get_total_score()), standing_surface, (rect.width - 10, y), self.WHITE, 'regular', 24, 'right')

        self.screen.blit(standing_surface, rect)

    def draw_default_section(self, section: str, rect: pygame.Rect):
        self.draw_text(section, rect, self.BLACK)

    def draw_text(self, text: str, rect: pygame.Rect, color: Tuple[int, int, int], offset_y: int = 0, offset_x: int = 0, font_size: int = 24):
        # Find the closest available font size
        available_sizes = sorted(self.fonts['regular'].keys())
        closest_size = min(available_sizes, key=lambda x: abs(x - font_size))
        
        font = self.fonts['regular'][closest_size]
        text_surface = font.render(str(text).upper(), True, color)
        text_rect = text_surface.get_rect(topleft=(rect.left + 10 + offset_x, rect.top + 10 + offset_y))
        self.screen.blit(text_surface, text_rect)

    def draw_section_content(self, section: str, rect: pygame.Rect):
        if section == "GAME_DATA_LOG":
            self.draw_scrollable_log(rect)
        elif section == "LEADERBOARD_SCORE":
            self.draw_leaderboard_score(rect)
        elif section == "LEADERBOARD_STANDING":
            self.draw_leaderboard_standing(rect)
        elif section == "SNAPTRAY":
            self.game_board.draw()
            self.draw_dice()
            self.draw_scoring_combinations()
        elif section == "STASH":
            self.draw_stash(rect)
        elif section == "STASHSTASH":
            self.draw_stashstash(rect)
        elif section == "DICECUP":
            self.draw_dicecup(rect)
        elif section == "RT_STATS":
            self.draw_rt_stats(rect)
        elif section == "GAME_INFO":
            self.draw_game_info(rect)
        elif section == "BANK_BUTTON":
            self.draw_bank_button(rect)
        elif section == "GAME_DATA_LOG_FRAME":
            # This section is just a frame, so we don't need to draw anything inside it
            pass
        else:
            self.draw_default_section(section, rect)

    def draw_bot_message(self, message, color):
        text_surface = self.fonts['regular'][36].render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 50))
        self.screen.blit(text_surface, text_rect)

    def draw_dice(self):
        if self.game_state.dice_values:
            stashable_dice = self.game_state.referee.get_stashable_dice(self.game_state.dice_values)
            formatted_dice = [f"{'green' if i in stashable_dice else 'white'}_{value}" for i, value in enumerate(self.game_state.dice_values)]
            hovered_dice, hovered_combination = self.get_hovered_combination(pygame.mouse.get_pos())
            
            if len(self.game_board.dice_positions) != len(self.game_state.dice_values):
                self.game_board.generate_dice_positions(len(self.game_state.dice_values))
            
            self.dice_rects = self.dice_renderer.render_dice_in_snaptray(
                formatted_dice,
                self.game_board.dice_positions[:len(self.game_state.dice_values)],
                self.game_state.selected_dice,
                hovered_dice,
                stashable_dice
            )
        else:
            self.dice_rects = []

    def draw_bust_box(self):
        if self.game_state.bust_state:
            if not hasattr(self, 'bust_text_box') or self.bust_text_box is None:
                self.create_bust_text_box()

            if self.bust_text_box:
                pygame.draw.rect(self.screen, self.RED, self.bust_text_box)
                busted_player = self.game_state.busted_player
                lost_points = self.game_state.busted_lost_score
                
                prefix = "@G-REF.:"
                prefix_surface = self.fonts['regular'][18].render(prefix, True, self.WHITE)
                prefix_rect = prefix_surface.get_rect(topleft=(self.bust_text_box.left + 10, self.bust_text_box.top + 10))
                pygame.draw.rect(self.screen, self.BLUE, prefix_rect)
                self.screen.blit(prefix_surface, prefix_rect)
                
                bust_text = f" Oh Noo! {busted_player.user.username} That's a BUST!"
                self.draw_text_on_surface(bust_text, self.screen, (self.bust_text_box.left + 10 + prefix_rect.width + 5, self.bust_text_box.top + 10), self.WHITE, 'regular', 28)
                
                points_text = f"{lost_points} POINTS LOST!"
                self.draw_text_on_surface(points_text, self.screen, (self.bust_text_box.left + 10, self.bust_text_box.top + 60), self.WHITE, 'regular', 20)
                
                self.draw_text_on_surface("TURN ENDED", self.screen, (self.bust_text_box.left + 10, self.bust_text_box.top + 90), self.WHITE, 'regular', 24)

        self.draw_dice()  # Always draw dice, even in bust state

    def create_bust_text_box(self):
        self.bust_text_box = pygame.Rect(self.WINDOW_WIDTH // 4, self.WINDOW_HEIGHT // 3,
                                        self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 3)

    def draw_scoring_combinations(self):
        if not self.game_state.dice_values:
            return

        scoring_combinations = self.game_state.referee.get_scoring_combinations(self.game_state.dice_values)
        snaptray_rect = self.sections["SNAPTRAY"]
        for i, (combination, points) in enumerate(scoring_combinations):
            text_box = pygame.Rect(snaptray_rect.left + i*200 + 50, snaptray_rect.top + 50, 180, 60)
            pygame.draw.rect(self.screen, self.WHITE, text_box)
            pygame.draw.rect(self.screen, self.BLACK, text_box, 2)
            
            mouse_pos = pygame.mouse.get_pos()
            if text_box.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, self.YELLOW, text_box.inflate(-4, -4), 2)
            
            self.draw_text(f"{combination}", text_box, self.BLACK, font_size=20)
            self.draw_text(f"[ {points} POINTS ]", text_box, self.BLACK, offset_y=30, font_size=20)

    def draw_dicecup(self, rect: pygame.Rect):
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var

        # Determine background color and cup image
        if self.show_green_dicecup or self.game_state.current_game_state == GameStateEnum.NEW_STASH:
            bg_color = (0, 187, 0)  # BGGreen
            cup_image_name = "dicecup_green.png"
        elif self.show_blue_dicecup:
            bg_color = (0, 0, 255)  # Blue
            cup_image_name = "dicecup_blue.png"
        else:
            bg_color = (255, 0, 0)  # Red
            cup_image_name = "dicecup_red.png"

        # Draw background
        pygame.draw.rect(self.screen, bg_color, rect)

        # Load images
        cup_image = pygame.image.load(os.path.join("assets", cup_image_name))
        
        # For STASHCHOICE_STASHED_FULL_READY_TO_ROLL or NEW_STASH, always show 6 dice
        if self.game_state.current_game_state in [GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL, GameStateEnum.NEW_STASH]:
            dice_image = pygame.image.load(os.path.join("assets", "dicecup_6.png"))
        else:
            dice_image = pygame.image.load(os.path.join("assets", f"dicecup_{remaining_dice}.png"))

        # Draw images
        self.screen.blit(cup_image, (rect.left, rect.top))
        self.screen.blit(dice_image, (rect.left + 270, rect.top))

        # Update rect positions
        self.dicecup_rect.topleft = (rect.left, rect.top)

        # Check if mouse is over the button and can roll
        mouse_pos = pygame.mouse.get_pos()
        relative_pos = (mouse_pos[0] - self.dicecup_rect.x, mouse_pos[1] - self.dicecup_rect.y)
        if 0 <= relative_pos[0] < self.dicecup_rect.width and 0 <= relative_pos[1] < self.dicecup_rect.height:
            if self.dicecup_mask.get_at(relative_pos) and self.game_state.referee.can_roll():
                self.screen.blit(self.dicecup_hover, (rect.left, rect.top))
                if not self.rotating_image.rotating:
                    self.rotating_image.start_rotation()
            else:
                self.rotating_image.stop_rotation()
        else:
            self.rotating_image.stop_rotation()

        self.rotating_image.update()
        self.rotating_image.draw(self.screen)

        # Debug information
        print(f"Can roll: {self.game_state.referee.can_roll()}, Show green: {self.show_green_dicecup}, Show blue: {self.show_blue_dicecup}, Show red: {self.show_red_dicecup}")
        print(f"Button color: {bg_color}, Image: {cup_image_name}")

    def draw_debug_text(self, text, rect, offset_y=0, offset_x=0, color=(255, 0, 0)):
        debug_text = self.fonts['regular'][20].render(text, True, color)
        self.screen.blit(debug_text, (rect.left + offset_x, rect.top + offset_y))

    def draw_text_on_surface(self, text: str, surface: pygame.Surface, position: Tuple[int, int], color: Tuple[int, int, int], font_style: str = 'regular', font_size: int = 24, align='left'):
        # Find the closest available font size
        available_sizes = sorted(self.fonts[font_style].keys())
        closest_size = min(available_sizes, key=lambda x: abs(x - font_size))
        
        font = self.fonts[font_style][closest_size]
        text_surface = font.render(str(text), True, color)
        if align == 'center':
            text_rect = text_surface.get_rect(center=position)
        elif align == 'right':
            text_rect = text_surface.get_rect(right=position[0], centery=position[1])
        else:
            text_rect = text_surface.get_rect(topleft=position)
        surface.blit(text_surface, text_rect)

    def animate_dice_roll(self):
        self.game_board.generate_dice_positions(len(self.game_state.dice_values))
        self.update_dice_positions([])
        
        animation_start_time = time.time()
        while time.time() - animation_start_time < 1.0:  # Run animation for 1 second
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time

            self.game_board.update(dt)
            self.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
    
    def update_dice_positions(self, stashed_indices: List[int]):
        self.game_board.update_dice_positions(stashed_indices)

    def handle_event(self, event: pygame.event.Event):
        pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.handle_left_click(pos)
            elif event.button == 4 or event.button == 5:  # Scroll up or down
                if self.sections["GAME_DATA_LOG"].collidepoint(pos):
                    self.handle_log_scroll(event)
                elif self.sections["LEADERBOARD_SCORE"].collidepoint(pos):
                    self.handle_leaderboard_scroll(event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.log_dragging = False
                self.leaderboard_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.log_dragging:
                self.handle_log_drag(pos)
            elif self.leaderboard_dragging:
                self.handle_leaderboard_drag(pos)
        
        self.draw()

    def handle_left_click(self, pos: Tuple[int, int]):
        if self.bank_button.is_clicked(pos):
            self.game_state.perform_action("BANK")
        elif self.start_turn_button.is_clicked(pos):
            self.start_turn()
        
        elif self.bust_button.is_clicked(pos) and self.game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY:
            self.game_state.next_player()
            self.game_state.referee.set_game_state(GameStateEnum.NEXTUP_READYUP)

        elif self.banked_turn_summary_button.is_clicked(pos) and self.game_state.current_game_state == GameStateEnum.BANKED_TURN_SUMMARY:
            self.game_state.next_player()
            self.game_state.referee.set_game_state(GameStateEnum.NEXTUP_READYUP)

        elif self.stash_stash.is_clicked(pos):
            self.game_state.start_new_stash()
            self.game_state.referee.set_game_state(GameStateEnum.NEW_STASH)
        elif self.stash_plank.is_clicked(pos):
            if self.game_state.selected_dice:
                self.game_state.stash_dice(self.game_state.selected_dice)
        elif self.scoring_info_button.is_clicked(pos):
            self.show_scoring_info()
        elif self.dicecup_rect.collidepoint(pos):
            if self.game_state.current_game_state == GameStateEnum.NEW_STASH:
                self.roll_dice_new_stash()
            elif self.game_state.referee.can_roll():
                self.game_state.roll_dice()
                self.animate_dice_roll()
        elif self.game_state.current_player.user.username.startswith("@VIDEO-GAMER"):
            print(f"Clicked position: {pos}")
            print(f"Current dice values: {self.game_state.dice_values}")
            print(f"Stashable dice: {self.game_state.referee.get_stashable_dice(self.game_state.dice_values)}")
            self.handle_dice_or_combination_click(pos)
                      
        log_rect = self.sections["GAME_DATA_LOG"]
        if log_rect.collidepoint(pos):
            self.log_dragging = True
            self.log_auto_scroll = False
        
        leaderboard_score_rect = self.sections["LEADERBOARD_SCORE"]
        if leaderboard_score_rect.collidepoint(pos):
            self.leaderboard_dragging = True

    def roll_dice_new_stash(self):
        self.game_state.roll_dice()
        self.animate_dice_roll()
        self.game_state.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS)
        self.draw()
        pygame.display.flip()

    def handle_dice_or_combination_click(self, pos: Tuple[int, int]):
        clicked_dice = self.get_clicked_dice(pos)
        
        if clicked_dice is not None:
            dice_collection = self.get_dice_collection(clicked_dice)
            if self.game_state.referee.can_select_dice(clicked_dice):
                if set(dice_collection).issubset(set(self.game_state.selected_dice)):
                    for die in dice_collection:
                        if die in self.game_state.selected_dice:
                            self.game_state.selected_dice.remove(die)
                else:
                    for die in dice_collection:
                        if die not in self.game_state.selected_dice:
                            self.game_state.selected_dice.append(die)
                
                self.game_state.update_selection_state()
                self.stash_plank.update(self.game_state, self.game_state.referee)
                print(f"Selected dice: {self.game_state.selected_dice}")  # Debug print

        # Update relevant UI components
        self.update_bank_button()
        self.update_start_turn_button()
        self.stash_plank.update(self.game_state, self.game_state.referee)
        self.stash_stash.update(self.game_state)

    def get_dice_collection(self, dice_index: int) -> List[int]:
        if dice_index >= len(self.game_state.dice_values):
            return []  # Return an empty list if the index is out of range
        
        dice_value = self.game_state.dice_values[dice_index]
        collection = [i for i, v in enumerate(self.game_state.dice_values) if v == dice_value]
        if len(collection) >= 3:
            return collection[:3]  # Return only the first three dice for triples
        elif len(collection) == 2 and dice_value == 6:
            return collection  # Return both dice for double 6
        return [dice_index]  # Return single die for other cases

    def get_clicked_dice(self, pos: Tuple[int, int]) -> Optional[int]:
        for i, dice_rect in enumerate(self.dice_rects):
            if dice_rect.collidepoint(pos):
                return i
        return None
    
    def handle_scroll_up(self, pos: Tuple[int, int]):
        if self.sections["GAME_DATA_LOG"].collidepoint(pos):
            self.log_scroll_y = max(0, self.log_scroll_y - 1)
        elif self.sections["LEADERBOARD_SCORE"].collidepoint(pos):
            self.leaderboard_scroll_y = min(self.leaderboard_scroll_y + 1, self.get_max_leaderboard_scroll())

    def handle_scroll_down(self, pos: Tuple[int, int]):
        if self.sections["GAME_DATA_LOG"].collidepoint(pos):
            visible_lines = self.sections["GAME_DATA_LOG"].height // self.log_line_height
            max_scroll = max(0, len(self.game_state.game_log) - visible_lines)
            self.log_scroll_y = min(max_scroll, self.log_scroll_y + 1)
        elif self.sections["LEADERBOARD_SCORE"].collidepoint(pos):
            self.leaderboard_scroll_y = max(0, self.leaderboard_scroll_y - 1)

    def handle_mouse_motion(self, pos: Tuple[int, int]):
        if self.dragging_scrollbar:
            dy = pos[1] - self.drag_start_y
            self.drag_start_y = pos[1]
            visible_lines = self.sections["GAME_DATA_LOG"].height // self.log_line_height
            total_lines = len(self.game_state.game_log)
            max_scroll = max(0, total_lines - visible_lines)
            self.log_scroll_y = max(0, min(max_scroll, self.log_scroll_y + int(dy * 0.1)))
        elif self.leaderboard_dragging_scrollbar:
            dy = pos[1] - self.leaderboard_drag_start_y
            self.leaderboard_drag_start_y = pos[1]
            scroll_change = int(dy / self.leaderboard_line_height)
            self.leaderboard_scroll_y = max(0, min(self.get_max_leaderboard_scroll(), self.leaderboard_scroll_y - scroll_change))

    def handle_leaderboard_scroll(self, event):
            if event.button == 4:  # Scroll up
                self.leaderboard_scroll_y = max(0, self.leaderboard_scroll_y - self.leaderboard_line_height)
            elif event.button == 5:  # Scroll down
                max_scroll = self.get_max_leaderboard_scroll()
                self.leaderboard_scroll_y = min(max_scroll, self.leaderboard_scroll_y + self.leaderboard_line_height)

    def start_turn(self):
        self.game_state.roll_dice()
        self.animate_dice_roll()
        self.draw()
        pygame.display.flip()
        if self.game_state.current_player.is_bot():
            pygame.time.delay(1000)  # Add a 1-second delay after the bot's first roll

    def bot_turn(self):
        pygame.event.pump()  # Process events to keep the window responsive

        def bot_delay():
            self.draw()
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait for 1 second
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        go_bot_ai = BotAI(self.game_state)
        
        bot_name = self.game_state.current_player.user.username
        print(f"{bot_name} turn started")
        self.game_state.add_log_entry(f"{bot_name} starts their turn", prefix=bot_name)

        self.game_state.turn_started = True
        self.game_state.turn_banked = False
        self.game_state.bust_state = False

        while not self.game_state.referee.is_turn_over():
            print(f"Current game state: {self.game_state.current_game_state}")
            print(f"Is turn over? {self.game_state.referee.is_turn_over()}")
            
            self.display_bot_thinking("What should I do next?")
            bot_delay()
            decision = go_bot_ai.make_decision()
            print(f"{bot_name} decision: {decision}")
            self.game_state.add_log_entry(f"{bot_name} decides to: {decision}", prefix=bot_name)
            bot_delay()

            if decision == "ROLL":
                if self.game_state.referee.can_roll():
                    self.display_bot_thinking("Time to roll the dice!")
                    bot_delay()
                    self.game_state.current_game_state = GameStateEnum.START_TURN  # Ensure correct game state before rolling
                    dice_values = self.game_state.roll_dice()
                    self.game_board.generate_dice_positions(len(dice_values))
                    self.game_board.update_dice_positions([])
                    self.draw()
                    pygame.display.flip()
                    bot_delay()
                else:
                    print(f"{bot_name} can't roll without stashing first")
                    self.game_state.add_log_entry(f"{bot_name} can't roll without stashing first", prefix=bot_name)
                    self.display_bot_decision("Can't roll without stashing. Ending turn.")
                    bot_delay()
                    break
          
            elif decision == "STASH":
                self.display_bot_thinking("These dice look good. I should stash them.")
                bot_delay()
                stash_indices = go_bot_ai.get_stash_indices()
                if stash_indices:
                    stashed_values = [self.game_state.dice_values[i] for i in stash_indices]
                    formatted_stashed = self.game_state.format_dice(stashed_values)

                    self.game_state.stash_dice(stash_indices)
                    self.game_state.add_log_entry(f"{bot_name} stashed dice: {formatted_stashed}", prefix=bot_name)
                    bot_delay()
                else:
                    print(f"{bot_name} tried to stash, but no stashable dice available")
                    self.game_state.add_log_entry(f"{bot_name} tried to stash, but no stashable dice available", prefix=bot_name)
                    self.display_bot_decision("No stashable dice available. Ending turn.")
                    bot_delay()
                    break
            
            elif decision == "BANK":
                self.display_bot_thinking("I've got a good score. Time to bank!")
                bot_delay()
                points = self.game_state.referee.calculate_turn_score()
                self.game_state.bank_points()
                self.update_leaderboard()
                self.game_state.add_log_entry(f"{bot_name} banked {points} points", prefix=bot_name)
                bot_delay()
                break
            
            elif decision == "START_NEW_STASH":
                self.display_bot_thinking("My stash is full. Let's start a new one!")
                bot_delay()
                self.game_state.start_new_stash()
                self.game_state.add_log_entry(f"{bot_name} ended their turn", prefix=bot_name)
                bot_delay()
            
            elif decision == "END_TURN":
                self.display_bot_thinking("I can't do anything else. Ending my turn.")
                bot_delay()
                break

            self.draw()
            pygame.display.flip()

        print(f"{bot_name} turn ended")
        print(f"{bot_name} final turn scores: {self.game_state.current_player.turn_scores}")
        print(f"{bot_name} final total score: {self.game_state.current_player.get_total_score()}")
        
        self.game_state.add_log_entry(f"{bot_name} ended their turn", prefix=bot_name)

        self.display_bot_decision(f"{bot_name} turn ended. Click to continue.")
        self.draw()
        pygame.display.flip()
        self.wait_for_click()

        self.game_state.next_player()
        self.bot_turn_in_progress = False

    def end_game(self):
        winner = self.game_state.get_winner()
        if winner:
            self.game_state.add_log_entry(f"GAME OVER! {winner.user.username} wins with {winner.get_total_score()} points!")
        self.game_state.set_active_task("GAME OVER")

    def get_max_leaderboard_scroll(self):
        visible_lines = (self.sections["LEADERBOARD_SCORE"].height - 60) // self.leaderboard_line_height
        total_lines = max(1, self.game_state.total_turns)
        return max(0, total_lines - visible_lines)
    
    def get_max_log_scroll(self):
        total_height = sum(len(self.wrap_text(entry, self.sections["GAME_DATA_LOG"].width - 20, return_lines=True)) 
                           for entry in self.game_state.game_log)
        return max(0, total_height * self.log_line_height - self.sections["GAME_DATA_LOG"].height)

    def get_hovered_combination(self, mouse_pos: Tuple[int, int]) -> Tuple[List[int], List[int]]:
        hovered_dice = []
        hovered_combination = []

        if self.dice_rects and self.game_state.dice_values:
            for i, dice_rect in enumerate(self.dice_rects):
                if dice_rect.collidepoint(mouse_pos):
                    if i < len(self.game_state.dice_values):  # Check if the index is valid
                        hovered_dice = self.get_dice_collection(i)
                        hovered_combination = hovered_dice
                    break

        return hovered_dice, hovered_combination

    def create_bust_text_box(self):
        self.bust_text_box = pygame.Rect(self.WINDOW_WIDTH // 4, self.WINDOW_HEIGHT // 3,
                                         self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 3)
        
    def display_bot_thinking(self, thought):
        bot_name = self.game_state.current_player.user.username
        self.bot_thinking_message = f"{bot_name} is thinking: {thought}"
        self.game_state.add_log_entry(f"{bot_name} is thinking: {thought}", prefix=bot_name)

    def display_bot_decision(self, decision):
        bot_name = self.game_state.current_player.user.username
        self.bot_decision_message = f"{bot_name} decision: {decision}"
        self.game_state.add_log_entry(decision, prefix=bot_name)

    def wait_for_click(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.delay(100)

    def format_log_entry(self, entry: str):
        words = entry.split()
        formatted_words = []
        for word in words:
            if word.startswith("[") and word.endswith("]"):
                dice_value = word[1:-2]  # Remove the last character (g or w)
                if dice_value.isdigit() and 1 <= int(dice_value) <= 6:
                    color = "olgreen" if word.endswith("g]") else ""
                    formatted_words.append(f"<DICE>{color}_{dice_value}</DICE>")
                else:
                    formatted_words.append(word)
            else:
                formatted_words.append(word)
        
        return " ".join(formatted_words)
    
    def show_scoring_info(self):
        current_player = self.game_state.current_player
        self.game_state.add_log_entry(f"{current_player.user.username} REQUESTED A REMINDER", prefix="@G-REF.")
        
        scoring_info = (
            "OFFICIAL SCORING TABLE\n"
            "FOR • LIVEDICE [ F ]\n"
            "\n"
            "SINGLE ONE <dice>green_1</dice> 100 POINTS\n"
            "SINGLE FIVE <dice>green_5</dice> 50 POINTS\n"
            "DOUBLE SIX <dice>green_6</dice> <dice>green_6</dice> 100 POINTS\n"
            "TRIPLE ONE <dice>green_1</dice> <dice>green_1</dice> <dice>green_1</dice> 1000 POINTS\n"
            "TRIPLE TWO <dice>green_2</dice> <dice>green_2</dice> <dice>green_2</dice> 200 POINTS\n"
            "TRIPLE THREE <dice>green_3</dice> <dice>green_3</dice> <dice>green_3</dice> 300 POINTS\n"
            "TRIPLE FOUR <dice>green_4</dice> <dice>green_4</dice> <dice>green_4</dice> 400 POINTS\n"
            "TRIPLE FIVE <dice>green_5</dice> <dice>green_5</dice> <dice>green_5</dice> 500 POINTS\n"
            "TRIPLE SIX <dice>green_6</dice> <dice>green_6</dice> <dice>green_6</dice> 600 POINTS"
        )
        
        self.game_state.add_log_entry(scoring_info, prefix="@G-REF.")

class StashPlank:
    def __init__(self, rect, font):
        self.rect = rect
        self.font = font
        self.stash_number = 1
        self.stash_points = 0
        self.selected_dice = []
        self.stashed_dice = []
        self.is_selection_mode = False
        self.button_text = ""
        self.button_enabled = False
        self.is_full_stash = False
        self.selected_points = 0
        self.total_points = 0
        self.load_images()

    def load_images(self):
        self.red_plank = pygame.image.load(os.path.join("assets", "stashplank_red.png"))
        self.blue_plank = pygame.image.load(os.path.join("assets", "stashplank_blue.png"))
        self.green_plank = pygame.image.load(os.path.join("assets", "stashplank_green.png"))
        self.button_bounds = pygame.image.load(os.path.join("assets", "stashplank_button_bounds.png"))
        self.button_hover = pygame.image.load(os.path.join("assets", "stashplank_button_hover.png"))
        self.dice_images = {
            'red': [pygame.image.load(os.path.join("assets", f"dice_olgreen_{i}_60px.png")) for i in range(1, 7)],
            'blue': [pygame.image.load(os.path.join("assets", f"dice_blueolgreen_{i}_60px.png")) for i in range(1, 7)]
        }

    def update(self, game_state, referee):
        self.stash_number = int(referee.get_stash_number()[:-2])
        self.stash_points = game_state.real_time_counters.stash_vscore
        self.selected_dice = [game_state.dice_values[i] for i in game_state.selected_dice]
        self.stashed_dice = game_state.current_player.stashed_dice
        self.is_selection_mode = len(self.selected_dice) > 0
        self.selected_points = referee.calculate_score(self.selected_dice)
        self.total_points = self.stash_points + self.selected_points
        self.is_full_stash = len(self.stashed_dice) + len(self.selected_dice) == 6
        self.button_enabled = self.is_selection_mode
        if self.is_selection_mode:
            self.button_text = f"STASH {self.selected_points} POINTS"
        else:
            self.button_text = ""

    def draw(self, surface):
        # Draw stashplank_titlebar
        title_rect = pygame.Rect(self.rect.left, self.rect.top, 440, 20)
        title_color = (0, 187, 0) if self.is_full_stash else (0, 0, 255) if self.is_selection_mode else (255, 0, 0)
        pygame.draw.rect(surface, title_color, title_rect)
        title_text = f"{self.get_ordinal(self.stash_number)} STASH {self.stash_points} POINTS"
        self.draw_text(surface, title_text, title_rect, self.font, (255, 255, 255))

        # Draw stashplank_plank
        plank_image = self.green_plank if self.is_full_stash else self.blue_plank if self.is_selection_mode else self.red_plank
        surface.blit(plank_image, (self.rect.left, self.rect.top + 20))

        # Draw dice
        dice_positions = [(40, 20), (100, 20), (160, 20), (220, 20), (280, 20), (340, 20)]
        for i, (x, y) in enumerate(dice_positions):
            if i < len(self.stashed_dice):
                die_value = self.stashed_dice[i]
                surface.blit(self.dice_images['red'][die_value - 1], (self.rect.left + x, self.rect.top + y + 20))
            elif i - len(self.stashed_dice) < len(self.selected_dice):
                die_value = self.selected_dice[i - len(self.stashed_dice)]
                surface.blit(self.dice_images['blue'][die_value - 1], (self.rect.left + x, self.rect.top + y + 20))

        # Draw stashplank_infobar
        info_rect = pygame.Rect(self.rect.left, self.rect.top + 120, 440, 100)
        info_color = (0, 187, 0) if self.is_full_stash else (0, 0, 255) if self.is_selection_mode else (255, 0, 0)
        pygame.draw.rect(surface, info_color, info_rect)
        if self.is_selection_mode:
            info_text = [
                f"ADDS {self.selected_points} POINTS TO GET {self.total_points} POINTS",
                f"IN {self.get_ordinal(self.stash_number)} STASH",
                "UNLOCKS OPTION: ROLL REMAINING DICE"
            ]
            for i, text in enumerate(info_text):
                self.draw_text(surface, text, info_rect.move(10, i * 25), self.font, (255, 255, 255), align='left')

        # Draw stashplank_actionbar
        action_rect = pygame.Rect(self.rect.left, self.rect.top + 220, 440, 20)
        action_color = (0, 187, 0) if self.is_full_stash else (0, 0, 170) if self.is_selection_mode else (255, 0, 0)
        pygame.draw.rect(surface, action_color, action_rect)
        if self.button_enabled:
            self.draw_text(surface, self.button_text, action_rect, self.font, (255, 255, 255))

        # Draw button hover effect if needed
        if self.is_selection_mode:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                relative_pos = (mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top - 20)
                if 0 <= relative_pos[0] < self.button_bounds.get_width() and 0 <= relative_pos[1] < self.button_bounds.get_height():
                    mask = pygame.mask.from_surface(self.button_bounds)
                    if mask.get_at(relative_pos):
                        surface.blit(self.button_hover, (self.rect.left, self.rect.top + 20))

    def draw_text(self, surface, text, rect, font, color, align='center'):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'left':
            text_rect.topleft = rect.topleft
        elif align == 'right':
            text_rect.topright = rect.topright
        else:
            text_rect.center = rect.center
        surface.blit(text_surface, text_rect)

    def get_ordinal(self, n):
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    def is_clicked(self, pos):
        if not self.is_selection_mode:
            return False
        relative_pos = (pos[0] - self.rect.left, pos[1] - self.rect.top - 20)
        if 0 <= relative_pos[0] < self.button_bounds.get_width() and 0 <= relative_pos[1] < self.button_bounds.get_height():
            mask = pygame.mask.from_surface(self.button_bounds)
            return mask.get_at(relative_pos)
        return False

    def set_button_text(self, text):
        self.button_text = text

class StashStash:
    def __init__(self, rect, font):
        self.rect = rect
        self.font = font
        self.stash_stash_points = 0
        self.full_stashes_moved = 0
        self.total_banked_stashes = 0
        self.is_full_stash = False
        self.button = None

    def update(self, game_state):
        self.stash_stash_points = game_state.current_player.stash_stash
        self.full_stashes_moved = game_state.current_player.full_stashes_moved_this_turn
        self.total_banked_stashes = game_state.current_player.get_total_banked_full_stashes()
        self.is_full_stash = game_state.referee.is_full_stash()

        if self.is_full_stash:
            self.button = Button(
                self.rect.left, self.rect.top + 120, 440, 20,
                "CLICK HERE TO MOVE FULL STASH INTO STASHSTASH",
                (0, 187, 0), (255, 255, 255), (0, 187, 0), (255, 255, 255)
            )
        else:
            self.button = None

    def draw(self, surface):
        # Draw stashstash_titlebar
        title_rect = pygame.Rect(self.rect.left, self.rect.top, 440, 20)
        title_color = (0, 187, 0) if self.is_full_stash else (204, 0, 0)
        pygame.draw.rect(surface, title_color, title_rect)
        title_text = f"STASHSTASH {self.stash_stash_points} POINTS"
        self.draw_text(surface, title_text, title_rect, self.font, (255, 255, 255))

        # Draw stashstash_infobar
        info_rect = pygame.Rect(self.rect.left, self.rect.top + 20, 440, 100)
        info_color = (0, 136, 0) if self.is_full_stash else (255, 0, 0)
        pygame.draw.rect(surface, info_color, info_rect)
        if self.is_full_stash:
            info_text = [
                f"MOVE {self.stash_stash_points} POINTS TO STASHSTASH",
                "GET A NEW EMPTY STASH"
            ]
        else:
            info_text = [
                f"HOLDING {self.full_stashes_moved} STASHES",
                f"TOTAL BANKED STASHES {self.total_banked_stashes}"
            ]
        for i, text in enumerate(info_text):
            self.draw_text(surface, text, info_rect.move(10, i * 25), self.font, (255, 255, 255), align='left')

        # Draw stashstash_actionbar
        action_rect = pygame.Rect(self.rect.left, self.rect.top + 120, 440, 20)
        action_color = (0, 187, 0) if self.is_full_stash else (204, 0, 0)
        pygame.draw.rect(surface, action_color, action_rect)
        if self.is_full_stash:
            action_text = "CLICK STASH AGAIN TO MOVE STASH TO STASHSTASH"
            self.draw_text(surface, action_text, action_rect, self.font, (255, 255, 255))

        if self.button:
            self.button.draw(surface)

    def draw_text(self, surface, text, rect, font, color, align='center'):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'left':
            text_rect.topleft = rect.topleft
        elif align == 'right':
            text_rect.topright = rect.topright
        else:
            text_rect.center = rect.center
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.button and self.button.is_clicked(pos)
    
import math

class RotatingImage:
    def __init__(self, image_path, pos, pivot):
        self.original_image = pygame.image.load(image_path)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.pivot = pivot
        self.angle = 0
        self.rotating = False
        self.rotation_speed = 0
        self.max_rotation_speed = 265
        self.acceleration = self.max_rotation_speed * 2
        self.last_rotation_time = 0
        self.total_rotation = 0
        self.reverse_rotation = False
        self.reverse_rotation_speed = 0
        self.reverse_rotation_start_time = 0
        self.reverse_rotation_total = 0

    def start_rotation(self):
        if not self.rotating and not self.reverse_rotation:
            self.rotating = True
            self.rotation_speed = 16
            self.last_rotation_time = pygame.time.get_ticks()
            self.total_rotation = 0

    def stop_rotation(self):
        if self.rotating:
            self.rotating = False
            self.reverse_rotation = True
            self.reverse_rotation_start_time = pygame.time.get_ticks()
            self.reverse_rotation_speed = self.total_rotation
            self.reverse_rotation_total = self.total_rotation

    def update(self):
        current_time = pygame.time.get_ticks()
        
        if self.rotating:
            dt = (current_time - self.last_rotation_time) / 1000
            self.rotation_speed = min(self.rotation_speed + self.acceleration * dt, self.max_rotation_speed)
            rotation_amount = self.rotation_speed * dt
            self.angle += rotation_amount
            self.total_rotation += rotation_amount
            self.last_rotation_time = current_time
        elif self.reverse_rotation:
            dt = (current_time - self.reverse_rotation_start_time) / 1000
            rotation_amount = min(self.reverse_rotation_speed * dt, self.reverse_rotation_total)
            self.angle -= rotation_amount
            self.reverse_rotation_total -= rotation_amount
            if self.reverse_rotation_total <= 0 or abs(self.angle % 360) < 1:
                self.reverse_rotation = False
                self.angle = 0

        self.angle %= 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pivot)

    def draw(self, surface):
        surface.blit(self.image, self.rect)