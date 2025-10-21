"""
UI EVENTS MODULE
Event handling for LIVEDICE game UI.
Processes user input including mouse clicks, scrolling, and keyboard events.
"""

import pygame
import sys
import time
from typing import List, Tuple, Optional
from ui.in_game.ui_helpers import UIHelpers
from games.livedice_f.livedice_f_rules import GameStateEnum


class UIEvents:
    """Handles all UI event processing"""
    
    def __init__(self, ui_instance):
        """
        Initialize events module with reference to main UI instance.
        
        Args:
            ui_instance: Reference to InGameUI instance
        """
        self.ui = ui_instance
        
        # Double-click detection variables
        self.last_click_time = 0
        self.last_clicked_dice = None
        self.double_click_threshold = 0.3  # 300ms window for double-click
    
    def animate_dice_roll(self):
        """Animate dice rolling"""
        self.ui.game_board.generate_dice_positions(len(self.ui.game_state.dice_values))
        self.ui.update_dice_positions([])
        
        animation_start_time = time.time()
        while time.time() - animation_start_time < 1.0:
            current_time = time.time()
            dt = current_time - self.ui.last_update_time
            self.ui.last_update_time = current_time

            self.ui.game_board.update(dt)
            self.ui.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
    
    def update_dice_positions(self, stashed_indices: List[int]):
        """Update dice positions after stashing"""
        self.ui.game_board.update_dice_positions(stashed_indices)

    # EVENT HANDLING

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events - required by UIInterface"""
        pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.ui.handle_left_click(pos)
            elif event.button == 4 or event.button == 5:
                if self.ui.sections["GAME_DATA_LOG"].collidepoint(pos):
                    self.ui.handle_log_scroll(event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.ui.log_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.ui.log_dragging:
                self.ui.handle_log_drag(pos)
        
        self.ui.draw()

        if self.ui.game_state.current_player.is_bot():
            self.ui.bot_turn()

    def handle_left_click(self, pos: Tuple[int, int]):
        """Handle left mouse button clicks"""
        # Import StashState locally to avoid circular import
        from ui.in_game.in_game_ui import StashState
        
        # X BUTTON - Return to menu (HIGHEST PRIORITY - check first)
        if hasattr(self.ui.drawing, 'x_button_rect'):
            if self.ui.drawing.x_button_rect.collidepoint(pos):
                print("X button clicked - returning to startup menu")
                self.ui.return_to_menu = True
                return
        
        # Color buttons
        for color, button in self.ui.color_buttons.items():
            if button.is_clicked(pos):
                self.ui.change_snaptray_color(color)
                return

        # BANK button (overlapping button from X:20 to X:540)
        bank_button_rect = pygame.Rect(20, 560, 520, 80)
        if bank_button_rect.collidepoint(pos):
            if self.ui.bank_button_enabled:
                print("BANK button clicked - enabled")
                self.ui.game_state.referee.perform_action("BANK")
            else:
                print("BANK button clicked - disabled")
                self.ui.game_state.add_log_entry("Cannot bank yet - must stash dice first!", prefix="@G-REF.")
            return
        
        # STASH button (plank + button area in selected state)
        if self.ui.stash_state == StashState.SELECTED:
            stash_button_rect = pygame.Rect(20, 680, 440, 110)
            if stash_button_rect.collidepoint(pos):
                print("STASH button clicked")
                self.ui.game_state.referee.perform_action("STASH")
                return
        
        # STASHSTASH button (only in full state)
        if self.ui.stash_state == StashState.FULL:
            stashstash_button_rect = pygame.Rect(20, 920, 500, 80)
            if stashstash_button_rect.collidepoint(pos):
                print("STASHSTASH button clicked")
                self.ui.game_state.referee.perform_action("START_NEW_STASH")
                return
        
        # Quick-stash all green dice (click plank in base state)
        if self.ui.stash_state == StashState.BASE:
            plank_rect = pygame.Rect(20, 680, 440, 110)
            if plank_rect.collidepoint(pos):
                stashable_dice = self.ui.game_state.referee.get_stashable_dice(self.ui.game_state.dice_values)
                if stashable_dice:
                    print("Stash plank clicked - stashing ALL green dice")
                    self.ui.game_state.selected_dice = stashable_dice.copy()
                    self.ui.game_state.referee.perform_action("STASH")
                    return
        
        # READY UP POPUP button
        ready_up_rect = self.ui.sections["READY_UP_POPUP"]
        if ready_up_rect.collidepoint(pos) and self.ui.game_state.current_game_state == GameStateEnum.NEXTUP_READYUP:
            self.ui.start_turn()
            return
        
        # TURN BUST POPUP button
        turn_bust_rect = self.ui.sections["TURN_BUST_POPUP"]
        if turn_bust_rect.collidepoint(pos) and self.ui.game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY:
            self.ui.game_state.referee.end_turn()
            return
        
        # BANKED POINTS POPUP button
        banked_points_rect = self.ui.sections["BANKED_POINTS_POPUP"]
        if banked_points_rect.collidepoint(pos) and self.ui.game_state.current_game_state == GameStateEnum.BANKED_TURN_SUMMARY:
            self.ui.game_state.referee.end_turn()
            return
        
        # SCORING INFO button
        if self.ui.scoring_info_button.is_clicked(pos):
            self.ui.show_scoring_info()
            return
        
        # DICECUP (roll dice)
        if self.ui.dicecup_rect.collidepoint(pos) and self.ui.game_state.referee.can_roll():
            self.ui.game_state.referee.perform_action("ROLL")
            return
        
        # DICE selection (only for human players)
        if self.ui.game_state.current_player.user.username.startswith("@VIDEO-GAMER"):
            self.ui.handle_dice_or_combination_click(pos)
        
        # Log scrolling
        log_rect = self.ui.sections["GAME_DATA_LOG"]
        if log_rect.collidepoint(pos):
            self.ui.log_dragging = True
            self.ui.log_auto_scroll = False
            return

    def start_turn(self):
        """Start a player's turn"""
        self.ui.game_state.roll_dice()
        self.ui.animate_dice_roll()
        self.ui.draw()
        pygame.display.flip()
        if self.ui.game_state.current_player.is_bot():
            pygame.time.delay(1000)

    def handle_dice_or_combination_click(self, pos: Tuple[int, int]):
        """
        Handle clicking on dice with THREE methods:
        1. Single click to select (existing)
        2. Double-click to instantly stash
        3. Click stash plank to stash all green (handled in handle_left_click)
        """
        if not self.ui.game_state.referee.can_select_dice():
            return

        # FIXED: Use self.get_clicked_dice instead of self.ui.get_clicked_dice
        clicked_dice = UIHelpers.get_clicked_dice(pos, self.ui.dice_rects)
        
        if clicked_dice is not None:
            current_time = time.time()
            
            # Check for double-click
            # FIXED: Use self.last_clicked_dice instead of self.ui.last_clicked_dice
            is_double_click = (
                self.last_clicked_dice == clicked_dice and 
                (current_time - self.last_click_time) < self.double_click_threshold
            )
            
            if is_double_click:
                # DOUBLE-CLICK: Instantly stash this die/combination
                print(f"Double-click detected on dice {clicked_dice} - instant stashing!")
                
                # FIXED: Use self.get_dice_collection instead of self.ui.get_dice_collection
                dice_collection = UIHelpers.get_dice_collection(self.ui.game_state.dice_values, clicked_dice)
                
                # Check if these dice can be stashed
                stashable_dice = self.ui.game_state.referee.get_stashable_dice(self.ui.game_state.dice_values)
                if all(die_idx in stashable_dice for die_idx in dice_collection):
                    # Select the dice
                    self.ui.game_state.selected_dice = dice_collection.copy()
                    self.ui.game_state.update_selection_state()
                    
                    # Immediately stash them
                    self.ui.game_state.referee.perform_action("STASH")
                    
                    # Reset double-click tracking
                    # FIXED: Use self.last_click_time instead of self.ui.last_click_time
                    self.last_click_time = 0
                    self.last_clicked_dice = None
                else:
                    print("Double-clicked dice are not stashable")
                
            else:
                # SINGLE CLICK: Normal selection/deselection behavior
                # FIXED: Use self.get_dice_collection instead of self.ui.get_dice_collection
                dice_collection = UIHelpers.get_dice_collection(self.ui.game_state.dice_values, clicked_dice)
                
                if self.ui.game_state.referee.can_select_dice(clicked_dice):
                    if set(dice_collection).issubset(set(self.ui.game_state.selected_dice)):
                        # Deselect
                        for die in dice_collection:
                            if die in self.ui.game_state.selected_dice:
                                self.ui.game_state.selected_dice.remove(die)
                    else:
                        # Select
                        for die in dice_collection:
                            if die not in self.ui.game_state.selected_dice:
                                self.ui.game_state.selected_dice.append(die)
                    
                    self.ui.game_state.update_selection_state()
                    print(f"Selected dice: {self.ui.game_state.selected_dice}")
                
                # Update double-click tracking
                # FIXED: Use self.last_click_time instead of self.ui.last_click_time
                self.last_click_time = current_time
                self.last_clicked_dice = clicked_dice

        # Update UI components
        self.ui.update_bank_button()

    def handle_log_scroll(self, event):
        """Handle log scrolling"""
        if event.button == 4:
            self.ui.log_scroll_y = max(0, self.ui.log_scroll_y - self.ui.log_line_height)
        elif event.button == 5:
            formatted_log = [self.ui.format_log_entry(entry) for entry in self.ui.game_state.game_log]
            total_height = sum(self.ui.get_entry_height(entry, self.ui.sections["GAME_DATA_LOG"].width - 20) for entry in formatted_log)
            max_scroll = max(0, total_height - self.ui.sections["GAME_DATA_LOG"].height)
            self.ui.log_scroll_y = min(max_scroll, self.ui.log_scroll_y + self.ui.log_line_height)
        self.ui.log_auto_scroll = False

    def scroll_log_to_bottom(self):
        """Auto-scroll game log to bottom when new entries added"""
        formatted_log = [self.ui.format_log_entry(entry) for entry in self.ui.game_state.game_log]
        total_height = sum(self.ui.get_entry_height(entry, self.ui.sections["GAME_DATA_LOG"].width - 20) for entry in formatted_log)
        visible_height = self.ui.sections["GAME_DATA_LOG"].height
        max_scroll = max(0, total_height - visible_height)
        self.ui.log_scroll_y = max_scroll

    def handle_log_drag(self, mouse_pos):
        """Handle log dragging"""
        if self.ui.log_dragging:
            rect = self.ui.sections["GAME_DATA_LOG"]
            visible_height = rect.height
            formatted_log = [self.ui.format_log_entry(entry) for entry in self.ui.game_state.game_log]
            total_height = sum(self.ui.get_entry_height(entry, rect.width - 20) for entry in formatted_log)
            max_scroll = max(0, total_height - visible_height)
            
            drag_pos = mouse_pos[1] - rect.top
            scroll_ratio = drag_pos / rect.height
            self.ui.log_scroll_y = int(scroll_ratio * max_scroll)
            self.ui.log_scroll_y = min(max_scroll, max(0, self.ui.log_scroll_y))


    # BOT AI HANDLING
