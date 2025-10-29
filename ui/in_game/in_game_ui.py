"""
LIVEDICE IN-GAME UI (REFACTORED)
Main UI class that coordinates all UI modules.
This file imports and integrates: sections, helpers, drawing, events, and bot modules.
"""

import pygame
import sys
import os
import time
import math
from typing import List, Tuple, Optional
from enum import Enum

# Setup project path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# Core imports
from core.game_state.game_state import GameStateManager
from games.livedice_f.livedice_f_rules import GameStateEnum
from core.account.user import User
from ui.in_game.button import Button
from ui.ui_interface import UIInterface
from ui.in_game.game_board import GameBoard
from ui.in_game.dice_renderer import DiceRenderer
from core.game_engine.go_bot_ai import BotAI

# Import our modular UI components
from ui.in_game.ui_sections import UISections
from ui.in_game.ui_helpers import UIHelpers
from ui.in_game.ui_drawing import UIDrawing
from ui.in_game.ui_events import UIEvents
from ui.in_game.ui_bot import UIBot


class StashState(Enum):
    """Enum for stash section display states"""
    BASE = "base"
    SELECTED = "selected"
    FULL = "full"


class InGameUI(UIInterface):
    """
    Main UI class for LIVEDICE in-game interface.
    Coordinates all UI modules and manages game display.
    """
    
    def __init__(self, human_players, ai_players, endgoal=4000, ruleset="STANDARD", bot_difficulty="NORMAL"):
        """
        Initialize the in-game UI.
        
        Args:
            human_players: Number of human players
            ai_players: Number of AI players
            endgoal: Target score to win (2000, 4000, or 8000)
            ruleset: Scoring rules to use (SIMPLE, STANDARD, or ADVANCED)
            bot_difficulty: AI difficulty level (EASY, NORMAL, or HARD)
        """
        pygame.init()
        self.WINDOW_WIDTH = 1920
        self.WINDOW_HEIGHT = 1080
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("• LIVEDICE [ IF ]")

        # Store player counts and game configuration
        self.human_players = human_players
        self.ai_players = ai_players
        self.endgoal = int(endgoal) if endgoal else 4000
        self.ruleset = ruleset if ruleset else "STANDARD"
        self.bot_difficulty = bot_difficulty if bot_difficulty else "NORMAL"
        
        # Initialize modular components
        self._setup_ui_modules()
        
        # Setup core UI elements
        self.setup_fonts()
        self.setup_game()
        self.setup_ui_components()
        self.setup_scoring_info_button()
        self.setup_rotating_image()
        
        # Setup buttons

        # Button states
        self.bank_button_enabled = False
        self.bank_button_hover = False
        
        # Stash state management
        self.stash_state = StashState.BASE
        self.stash_button_hover = False
        self.stashstash_button_hover = False

        # Popup hover states
        self.ready_up_popup_hover = False
        self.turn_bust_popup_hover = False
        self.banked_points_popup_hover = False

        self.buttons = {}
        
        # Initialize renderers
        self.dice_renderer = DiceRenderer(self.screen)

        # Load dicecup assets
        self.dicecup_bounds = pygame.image.load(os.path.join("assets", "dicecup_button_bounds.png")).convert_alpha()
        self.dicecup_hover = pygame.image.load(os.path.join("assets", "dicecup_blue_button_hover.png")).convert_alpha()
        self.dicecup_mask = pygame.mask.from_surface(self.dicecup_bounds)
        self.dicecup_rect = self.dicecup_bounds.get_rect()
        self.dicecup_rect.topleft = (self.sections["DICECUP"].left, self.sections["DICECUP"].top)

        # Load snaptray overlays
        self.snaptray_color = "red"
        self.snaptray_images = {
            "red": pygame.image.load(os.path.join("assets", "snaptray_lineart_red.png")).convert_alpha(),
            "blue": pygame.image.load(os.path.join("assets", "snaptray_lineart_blue.png")).convert_alpha(),
            "green": pygame.image.load(os.path.join("assets", "snaptray_lineart_green.png")).convert_alpha()
        }
        self.snaptray_overlay = self.snaptray_images["red"]

        # Load stash plank images
        self.stashplank_images = {
            "red": pygame.image.load(os.path.join("assets", "stashplank_red.png")).convert_alpha(),
            "blue": pygame.image.load(os.path.join("assets", "stashplank_blue.png")).convert_alpha(),
            "green": pygame.image.load(os.path.join("assets", "stashplank_green.png")).convert_alpha(),
            "hover": pygame.image.load(os.path.join("assets", "stashplank_button_hover.png")).convert_alpha()
        }

        # Dice images for stash display
        self.dice_images = {
            'red': [pygame.image.load(os.path.join("assets", f"dice_olgreen_{i}_70px.png")) for i in range(1, 7)],
            'blue': [pygame.image.load(os.path.join("assets", f"dice_blueolgreen_{i}_70px.png")) for i in range(1, 7)]
        }
        
        # Small dice images for game log (36px)
        self.dice_images_small = {
            'white': [pygame.transform.scale(pygame.image.load(os.path.join("assets", f"dice_olgreen_{i}_70px.png")), (36, 36)) for i in range(1, 7)],
            'green': [pygame.transform.scale(pygame.image.load(os.path.join("assets", f"dice_olgreen_{i}_70px.png")), (36, 36)) for i in range(1, 7)]
        }

        # Dice positions in stash plank
        self.stash_dice_positions = [
            (30, 700), (100, 700), (170, 700),
            (240, 700), (310, 700), (380, 700)
        ]

        # Create color change buttons
        button_size = 30
        spacing = 10
        start_x = self.sections["SNAPTRAY"].right - (button_size + spacing) * 5
        start_y = self.sections["SNAPTRAY"].bottom - button_size - spacing
        self.color_buttons = {
            "red": Button(start_x, start_y, button_size, button_size, "", (255, 0, 0), (255, 255, 255), (255, 0, 0), (255, 0, 0)),
            "green": Button(start_x + button_size + spacing, start_y, button_size, button_size, "", (0, 255, 0), (255, 255, 255), (0, 255, 0), (0, 255, 0)),
            "blue": Button(start_x + (button_size + spacing) * 2, start_y, button_size, button_size, "", (0, 0, 255), (255, 255, 255), (0, 0, 255), (0, 0, 255))
        }

        # Initialize scrolling variables
        self.log_scroll_y = 0
        self.log_dragging = False
        self.log_auto_scroll = True

        self.use_start_turn_button = True
        self.last_update_time = time.time()
        # Bot messages migrated to message_manager in game_state
        # Return to menu flag (for X button)
        self.return_to_menu = False
        self.show_exit_confirmation = False  # Flag for exit confirmation popup
        # Dice rectangles for click detection
        self.dice_rects = []
    
    def _setup_ui_modules(self):
        """Initialize all modular UI components"""
        # Initialize sections and colors
        ui_sections = UISections()
        self.sections = ui_sections.sections
        
        # Setup colors from sections module
        colors = ui_sections.colors
        self.BLACK = colors["BLACK"]
        self.WHITE = colors["WHITE"]
        self.RED = colors["RED"]
        self.DARK_RED = colors["DARK_RED"]
        self.GREEN = colors["GREEN"]
        self.MEDIUM_GREEN = colors["MEDIUM_GREEN"]
        self.DARK_GREEN = colors["DARK_GREEN"]
        self.DARKER_GREEN = colors["DARKER_GREEN"]
        self.BLUE = colors["BLUE"]
        self.DARK_BLUE = colors["DARK_BLUE"]
        self.DARKER_RED = colors["DARKER_RED"]
        self.CYAN = colors["CYAN"]
        self.YELLOW = colors["YELLOW"]
        self.MAGENTA = colors["MAGENTA"]
        self.ORANGE = colors["ORANGE"]
        self.PURPLE = colors["PURPLE"]
        self.GRAY = colors["GRAY"]
        
        # Initialize helper modules (pass self as reference)
        self.drawing = UIDrawing(self)
        self.events = UIEvents(self)
        self.bot_ui = UIBot(self)
    
    # ========================================================================
    # PROPERTIES
    # ========================================================================
    
    @property
    def show_green_dicecup(self):
        """Check if dicecup should be green"""
        return self.game_state.current_game_state in [
            GameStateEnum.STASHCHOICE_STASHED_FULL,
            GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL
        ]

    @property
    def show_blue_dicecup(self):
        """Check if dicecup should be blue"""
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
        """Check if dicecup should be red"""
        return (not (self.show_blue_dicecup or self.show_green_dicecup) or 
                self.game_state.current_game_state in [
                    GameStateEnum.START_TURN,
                    GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH,
                    GameStateEnum.NEXTUP_READYUP
                ])
    
    # ========================================================================
    # SETUP METHODS
    # ========================================================================
    
    def setup_ui_components(self):
        """Setup UI components"""
        self.game_board = GameBoard(self.screen, self.sections["SNAPTRAY"])
        self.dice_renderer = DiceRenderer(self.screen)
    
    def setup_fonts(self):
        """Setup all font variations according to design specification"""
        font_path = os.path.join("assets", "open-sauce-two")
        
        # Font style filenames
        font_files = {
            'black': 'OpenSauceTwo-Black.ttf',
            'black_italic': 'OpenSauceTwo-BlackItalic.ttf',
            'bold': 'OpenSauceTwo-Bold.ttf',
            'bold_italic': 'OpenSauceTwo-BoldItalic.ttf',
            'extra_bold': 'OpenSauceTwo-ExtraBold.ttf',
            'extra_bold_italic': 'OpenSauceTwo-ExtraBoldItalic.ttf',
            'italic': 'OpenSauceTwo-Italic.ttf',
            'light': 'OpenSauceTwo-Light.ttf',
            'light_italic': 'OpenSauceTwo-LightItalic.ttf',
            'medium': 'OpenSauceTwo-Medium.ttf',
            'medium_italic': 'OpenSauceTwo-MediumItalic.ttf',
            'regular': 'OpenSauceTwo-Regular.ttf',
            'semi_bold': 'OpenSauceTwo-SemiBold.ttf',
            'semi_bold_italic': 'OpenSauceTwo-SemiBoldItalic.ttf'
        }
        
        # All sizes needed
        font_sizes = [10, 12, 14, 16, 18, 20, 22, 24, 28, 36]
        
        # Create fonts dictionary
        self.fonts = {}
        for style, filename in font_files.items():
            self.fonts[style] = {}
            for size in font_sizes:
                self.fonts[style][size] = pygame.font.Font(os.path.join(font_path, filename), size)
        
        # Named font presets from design specification
        self.font_minititle_black = self.fonts['black'][10]
        self.font_minititle_semibold = self.fonts['semi_bold'][10]
        self.font_textbox_black = self.fonts['black'][12]
        self.font_textbox_semibold = self.fonts['semi_bold'][12]
        self.font_textbar_black = self.fonts['black'][16]
        self.font_textbar_semibold = self.fonts['semi_bold'][16]
        self.font_mediumtextbar_black = self.fonts['black'][24]
        self.font_mediumtextbar_semibold = self.fonts['semi_bold'][24]
        self.font_bigtextbar_black = self.fonts['black'][36]
        self.font_bigtextbar_semibold = self.fonts['semi_bold'][36]
        
        # Legacy font references for other parts
        self.log_font = self.fonts['regular'][18]
        self.log_line_height = 22
        self.max_visible_lines = 24

    def setup_game(self):
        """Initialize game state manager with configuration"""
        self.game_state = GameStateManager(self, self.human_players, self.ai_players, self.endgoal, self.ruleset, self.bot_difficulty)
        self.game_state.set_active_task("Click START TURN to begin your turn")

    def setup_scoring_info_button(self):
        """Setup scoring information button"""
        snaptray_rect = self.sections["SNAPTRAY"]
        button_size = 60
        button_pos = (snaptray_rect.right - button_size - 10, snaptray_rect.bottom - button_size - 10)
        self.scoring_info_button = Button(button_pos[0], button_pos[1], button_size, button_size, 
                                          "?", self.WHITE, self.BLACK, self.BLACK, self.BLACK, font_size=48)

    def setup_rotating_image(self):
        """Setup rotating image for dicecup"""
        image_path = os.path.join("assets", "PRECISE-G-154x154.png")
        dicecup_rect = self.sections["DICECUP"]
        pos = (dicecup_rect.left + 72, dicecup_rect.top + 177)
        pivot = (pos[0] + 77, pos[1] + 77)
        self.rotating_image = RotatingImage(image_path, pos, pivot)

    def initialize_game_log(self):
        """Initialize game log with first entry - called from main.py"""
        self.game_state.add_log_entry(f"{self.game_state.current_player.user.username} starts the game")
    
    # ========================================================================
    # UPDATE METHODS
    # ========================================================================
    
    def update(self):
        """Update game state and UI components - required by UIInterface"""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        self.game_board.update(dt)
        self.rotating_image.update()

        # Update stash state
        self.update_stash_state()

        # Bot turn handling
        if self.game_state.current_player.is_bot():
            if not self.bot_ui.bot_turn_in_progress:
                self.bot_ui.bot_turn_in_progress = True
                self.bot_ui.bot_turn()
        else:
            self.bot_ui.bot_turn_in_progress = False

        # Check game over
        if self.game_state.check_game_over():
            self.bot_ui.end_game()
        
        # Update buttons (only if not in bot turn)
        if not self.bot_ui.bot_turn_in_progress:
            self.update_bank_button()

    def update_stash_state(self):
        """Update the stash section state based on game situation"""
        stashed_count = len(self.game_state.current_player.stashed_dice)
        selected_count = len(self.game_state.selected_dice)
        
        # Check if stash is full (6 dice)
        if stashed_count == 6:
            self.stash_state = StashState.FULL
        # Check if dice are selected
        elif selected_count > 0:
            self.stash_state = StashState.SELECTED
        # Default state
        else:
            self.stash_state = StashState.BASE

    def update_bank_button(self):
        """Update bank button enabled state"""
        self.bank_button_enabled = self.game_state.referee.can_bank()

    def update_leaderboard(self):
        """Update leaderboard with current turn results"""
        current_player = self.game_state.current_player
        turn_score = self.game_state.real_time_counters.turn_vscore
        rolls = self.game_state.real_time_counters.turn_rolls_var
        stashes = self.game_state.real_time_counters.stashstashtimes_vscore
        
        # current_player.record_turn(self.game_state.current_turn_number, turn_score, rolls, stashes) # DISABLED: Causes double recording
        self.game_state.total_turns += 1
        
        log_entry = f"{current_player.user.username} scored {UIHelpers.format_number(turn_score)} points in turn {UIHelpers.format_number(self.game_state.current_turn_number)} with {UIHelpers.format_number(rolls)} rolls and {UIHelpers.format_number(stashes)} stashes"
        self.game_state.add_log_entry(log_entry)
    
    def update_leaderboard_scroll(self):
        """Update leaderboard scroll position - required by UIInterface"""
        # This method is required by the abstract UIInterface class
        # In the new design, the leaderboard doesn't need separate scrolling
        pass
    
    # ========================================================================
    # HELPER METHODS (delegate to UIHelpers)
    # ========================================================================
    
    def format_number(self, number):
        """Format numbers replacing 0 with O"""
        return UIHelpers.format_number(number)

    def format_log_entry(self, entry: str):
        """Format log entry with dice markup"""
        return UIHelpers.format_log_entry(entry)

    def draw_text_with_font(self, text: str, x: int, y: int, color: Tuple[int, int, int], font):
        """Helper function to draw text with a specific font"""
        UIHelpers.draw_text_with_font(self.screen, text, x, y, color, font)
    
    def get_virtual_rank(self):
        """Calculate virtual rank if player banks now"""
        return UIHelpers.get_virtual_rank(self.game_state, self.game_state.current_player)
    
    def should_draw_popup(self, popup_name):
        """Check if popup should be drawn"""
        return UIHelpers.should_draw_popup(popup_name, self.game_state)
    
    def get_entry_height(self, entry, max_width):
        """Calculate height needed for a log entry"""
        return UIHelpers.get_entry_height(entry, max_width, self.fonts['regular'][16])
    
    # ========================================================================
    # DRAWING METHODS (delegate to UIDrawing)
    # ========================================================================
    
    def draw(self):
        """Main draw method - delegates to UIDrawing module"""
        self.drawing.draw()
    
    def render_log_line(self, surface, line, x, y):
        """Render a single log line - delegates to UIDrawing module"""
        return self.drawing.render_log_line(surface, line, x, y)
    
    def create_bust_text_box(self):
        """Create the bust text box - delegates to UIDrawing module"""
        return self.drawing.create_bust_text_box()
    
    # ========================================================================
    # EVENT HANDLING (delegate to UIEvents)
    # ========================================================================
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events - delegates to UIEvents module"""
        self.events.handle_event(event)
    
    def scroll_log_to_bottom(self):
        """Auto-scroll game log to bottom - delegates to UIEvents module"""
        self.events.scroll_log_to_bottom()
    
    def animate_dice_roll(self):
        """Animate dice rolling - delegates to UIEvents module"""
        self.events.animate_dice_roll()
    
    def update_dice_positions(self, stashed_indices: List[int]):
        """Update dice positions after stashing - delegates to UIEvents module"""
        self.events.update_dice_positions(stashed_indices)
    
    def handle_left_click(self, pos: Tuple[int, int]):
        """Handle left mouse button clicks - delegates to UIEvents module"""
        self.events.handle_left_click(pos)
    
    def start_turn(self):
        """Start a player's turn - delegates to UIEvents module"""
        self.events.start_turn()
    
    def handle_dice_or_combination_click(self, pos: Tuple[int, int]):
        """Handle clicking on dice - delegates to UIEvents module"""
        self.events.handle_dice_or_combination_click(pos)
    
    def handle_log_scroll(self, event):
        """Handle log scrolling - delegates to UIEvents module"""
        self.events.handle_log_scroll(event)
    
    def handle_log_drag(self, mouse_pos):
        """Handle log dragging - delegates to UIEvents module"""
        self.events.handle_log_drag(mouse_pos)
    
    # ========================================================================
    # BOT & UTILITY METHODS (delegate to UIBot)
    # ========================================================================
    
    def change_snaptray_color(self, color):
        """Change snaptray overlay color - delegates to UIBot module"""
        self.bot_ui.change_snaptray_color(color)
    
    def force_redraw(self):
        """Force screen redraw - delegates to UIBot module"""
        self.bot_ui.force_redraw()
    
    def bot_turn(self):
        """Handle AI bot turn - delegates to UIBot module"""
        self.bot_ui.bot_turn()
    
    def end_game(self):
        """Handle end of game - delegates to UIBot module"""
        self.bot_ui.end_game()
    
    def display_bot_thinking(self, thought):
        """Display bot thinking message - delegates to UIBot module"""
        self.bot_ui.display_bot_thinking(thought)
    
    def display_bot_decision(self, decision):
        """Display bot decision message - delegates to UIBot module"""
        self.bot_ui.display_bot_decision(decision)
    
    def wait_for_click(self):
        """Wait for user to click - delegates to UIBot module"""
        self.bot_ui.wait_for_click()
    
    def show_scoring_info(self):
        """Show scoring information in log - delegates to UIBot module"""
        self.bot_ui.show_scoring_info()


# ============================================================================
# ROTATING IMAGE CLASS (used by dicecup)
# ============================================================================

class RotatingImage:
    """Rotating image for dicecup animation"""
    
    def __init__(self, image_path, pos, pivot):
        """Initialize rotating image"""
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
        """Start rotating"""
        if not self.rotating and not self.reverse_rotation:
            self.rotating = True
            self.rotation_speed = 16
            self.last_rotation_time = pygame.time.get_ticks()
            self.total_rotation = 0

    def stop_rotation(self):
        """Stop rotating"""
        if self.rotating:
            self.rotating = False
            self.reverse_rotation = True
            self.reverse_rotation_start_time = pygame.time.get_ticks()
            self.reverse_rotation_speed = self.total_rotation
            self.reverse_rotation_total = self.total_rotation

    def update(self):
        """Update rotation"""
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
        """Draw the rotating image"""
        surface.blit(self.image, self.rect)
