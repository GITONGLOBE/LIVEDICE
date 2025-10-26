"""
UI DRAWING MODULE
All drawing methods for LIVEDICE game UI.
Handles rendering of all visual elements including panels, scores, dice, and game state.

MODIFIED: 2025-10-22
FILE: ui/in_game/ui_drawing.py  
CHANGES: Fixed multiple AttributeError, NameError, and ValueError crashes
- Line 20: Added missing 'import re' (Required for regex in _parse_message_text)
- Line 1172: Changed 'G-REF' → '@G-REF' (Correct sender name includes @ symbol)
- Line 1200: Changed message.text → message.content (Message class uses .content attribute)
- Lines 1217-1229: Fixed max() empty sequence error (text_lines contains tuples, not strings)
WHY: Fix crashes during game start with messaging system
TESTING: Start game, messages should display correctly in GAME_DATA_LOG without any crashes
DEPENDENCIES: core.messaging.message_system (GREFMessage, BOTMessage classes)
ALSO CHECKED: game_state.py, message_system.py - no similar issues found (game_state.py max() already has fallback)
PROJECT SCAN: Comprehensively searched entire codebase for similar issues - all found issues fixed
"""

import pygame
from pathlib import Path
import sys
import os
import re
import time
from typing import List, Tuple, Optional
from ui.in_game.ui_helpers import UIHelpers
from games.livedice_f.livedice_f_rules import GameStateEnum
from core.messaging import MessageType, GREFMessage, BOTMessage


class UIDrawing:
    """Handles all UI drawing operations"""
    
    def __init__(self, ui_instance):
        """
        Initialize drawing module with reference to main UI instance.
        
        Args:
            ui_instance: Reference to InGameUI instance for accessing game state and resources
        """
        self.ui = ui_instance
        
        # PERFORMANCE: Message rendering cache
        self.message_cache = {}  # {message_id: (surface, width, height, is_left)}
        self.last_message_count = 0
    
    def draw_text_with_font(self, text: str, x: int, y: int, color: Tuple[int, int, int], font):
        """Helper function to draw text with a specific font"""
        text_surface = font.render(str(text), True, color)
        self.ui.screen.blit(text_surface, (x, y))

    # DRAWING METHODS

    def draw(self):
        """Main draw method - renders entire screen - required by UIInterface"""
        # Fill background with red
        self.ui.screen.fill(self.ui.RED)
        
        # Draw background panel sections
        pygame.draw.rect(self.ui.screen, self.ui.DARK_RED, self.ui.sections["LEFTPANEL"])
        pygame.draw.rect(self.ui.screen, self.ui.WHITE, self.ui.sections["CENTRALPANEL"])
        pygame.draw.rect(self.ui.screen, self.ui.DARK_RED, self.ui.sections["RIGHTPANEL"])
        
        # Draw red sidebars behind overlapping sections on left panel
        # Left sidebar (behind left edge) - 20px wide, full height
        left_sidebar = pygame.Rect(0, 0, 20, 1080)
        pygame.draw.rect(self.ui.screen, self.ui.DARKER_RED, left_sidebar)
        
        # Right sidebar (behind overlapping sections) - 20px wide at X:460-480
        right_sidebar = pygame.Rect(460, 0, 20, 1080)
        pygame.draw.rect(self.ui.screen, self.ui.DARKER_RED, right_sidebar)
 
        # Draw the snaptray overlay
        snaptray_rect = self.ui.sections["SNAPTRAY"]
        self.ui.screen.blit(self.ui.snaptray_overlay, snaptray_rect.topleft)

        # Draw all left panel sections (FIXED: use self.draw_* not self.ui.draw_*)
        self.draw_game_info()
        self.draw_leaderboard_standing()
        self.draw_now_playing_player()
        self.draw_rt_stats()
        self.draw_leaderboard_score()
        self.draw_bank_button()
        self.draw_stash_section()
        
        # Draw right panel sections (FIXED: use self.draw_* not self.ui.draw_*)
        self.draw_dicecup()
        
        self.draw_scrollable_log(self.ui.sections["GAME_DATA_LOG"])
        
        # Draw game content
        self.draw_bust_box()
        self.ui.game_board.draw()
        self.draw_dice()

        # NEW: Draw bot chat bubbles instead of old text messages
        if self.should_draw_popup("READY_UP_POPUP"):
            self.draw_ready_up_popup()
        elif self.should_draw_popup("TURN_BUST_POPUP"):
            self.draw_turn_bust_popup()
        elif self.should_draw_popup("BANKED_POINTS_POPUP"):
            self.draw_banked_points_popup()
        elif self.ui.game_state.current_game_state == GameStateEnum.END_GAME_SUMMARY:
            self.draw_end_game_summary()

        self.ui.scoring_info_button.draw(self.ui.screen)
        
        # Draw X button (overlay on top right corner)
        self.draw_x_button()

        # Draw color change buttons
        for button in self.ui.color_buttons.values():
            button.draw(self.ui.screen)

        pygame.display.update()
    
    def should_draw_popup(self, popup_name):
        """Check if popup should be drawn"""
        if popup_name == "READY_UP_POPUP":
            return self.ui.game_state.current_game_state == GameStateEnum.NEXTUP_READYUP
        elif popup_name == "TURN_BUST_POPUP":
            return self.ui.game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY
        elif popup_name == "END_GAME_SUMMARY_POPUP":
            return self.ui.game_state.check_game_over()
        elif popup_name == "BANKED_POINTS_POPUP":
            return self.ui.game_state.current_game_state == GameStateEnum.BANKED_TURN_SUMMARY
        return False

    def draw_game_info(self):
        """Draw GAME_INFO section following exact specification"""
        rect = self.ui.sections["GAME_INFO"]
        
        # game_info_top_bar (empty green bar) - #00FF00 BRIGHT GREEN
        top_bar = pygame.Rect(rect.x, rect.y, 160, 20)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, top_bar)
        
        # game_info_minititle_bar - #00FF00 BRIGHT GREEN
        minititle_bar = pygame.Rect(rect.x, rect.y + 20, 160, 20)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, minititle_bar)
        x_pos = rect.x + 10
        y_pos = rect.y + 25  # Added 5px padding from top
        text = "GAME"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_black)
        x_pos += self.ui.font_minititle_black.size(text)[0]
        text = " IN "
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_semibold)
        x_pos += self.ui.font_minititle_semibold.size(text)[0]
        text = "SESSION"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_black)
        
        # game_info_base - #00BB00 DARKER GREEN
        base = pygame.Rect(rect.x, rect.y + 40, 160, 140)
        pygame.draw.rect(self.ui.screen, self.ui.MEDIUM_GREEN, base)
        
        x = rect.x + 10
        y = rect.y + 45
        
        # Bullet point and text - BULLET AND DICE IN RED #FF0000
        # FIXED: Bullet in red and same font as LIVE
        self.draw_text_with_font("•", x, y + 2, (255, 0, 0), self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size("• ")[0]
        
        text = "LIVE"
        self.draw_text_with_font(text, x, y + 2, self.ui.WHITE, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text)[0]
        
        # FIXED: DICE in red #FF0000
        text = "DICE"
        self.draw_text_with_font(text, x, y + 2, (255, 0, 0), self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text)[0]
        
        text = " [ "
        self.draw_text_with_font(text, x, y + 2, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text)[0]
        
        text = "IF"
        self.draw_text_with_font(text, x, y + 2, self.ui.WHITE, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text)[0]
        
        text = " ]"
        self.draw_text_with_font(text, x, y + 2, self.ui.WHITE, self.ui.font_textbox_semibold)
        
        # Next lines - DYNAMIC GAME SETTINGS (WHITE TEXT)
        y += 25
        x = rect.x + 10
        
        # Show current ruleset
        ruleset_text = self.ui.game_state.ruleset
        text = ruleset_text
        self.draw_text_with_font(text, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text)[0]
        
        text = " RULES"
        self.draw_text_with_font(text, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        
        y += 20
        x = rect.x + 10
        
        # Show endgoal
        text = "ENDGOAL "
        self.draw_text_with_font(text, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text)[0]
        
        endgoal_text = self.ui.format_number(str(self.ui.game_state.endgoal))
        text = endgoal_text
        self.draw_text_with_font(text, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        
        y += 20
        x = rect.x + 10
        
        # Show bot difficulty
        bot_diff_text = self.ui.game_state.bot_difficulty
        text = bot_diff_text
        self.draw_text_with_font(text, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text)[0]
        
        text = " BOTS"
        self.draw_text_with_font(text, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)


    def draw_leaderboard_standing(self):
        """Draw LEADERBOARD_STANDING section (top 8 player rankings)"""
        rect = self.ui.sections["LEADERBOARD_STANDING"]
        
        # leaderboard_standing_top_bar (empty green bar)
        top_bar = pygame.Rect(rect.x, rect.y, 280, 20)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, top_bar)
        
        # leaderboard_standing_minititle_bar
        minititle_bar = pygame.Rect(rect.x, rect.y + 20, 280, 20)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, minititle_bar)
        x_pos = rect.x + 10
        y_pos = rect.y + 25  # Added 5px padding from top
        text = "LEADER"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_black)
        x_pos += self.ui.font_minititle_black.size(text)[0]
        text = "BOARD"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_semibold)
        
        # leaderboard_standing_base (3 columns)
        base = pygame.Rect(rect.x, rect.y + 40, 280, 140)
        
        # Column 1: Numbers (60px wide, #0000AA background)
        number_col = pygame.Rect(rect.x, rect.y + 40, 60, 140)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, number_col)
        
        # Column 2: Names (140px wide, #0000FF background)
        name_col = pygame.Rect(rect.x + 60, rect.y + 40, 140, 140)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, name_col)
        
        # Column 3: Scores (80px wide, #0000AA background)
        score_col = pygame.Rect(rect.x + 200, rect.y + 40, 80, 140)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, score_col)
        
        # Get sorted players
        players_sorted = sorted(self.ui.game_state.players, key=lambda p: self.ui.game_state.referee.get_total_score(p), reverse=True)
        
        # Draw up to 8 players
        y_offset = 5
        for i, player in enumerate(players_sorted[:8]):
            y = rect.y + 45 + (i * 16)
            
            # Rank number (cyan text, left-aligned)
            rank_text = str(i + 1)
            self.draw_text_with_font(rank_text, rect.x + 10, y, self.ui.CYAN, self.ui.font_textbox_black)
            
            # Player name (green text, left-aligned)
            self.draw_text_with_font(player.user.username, rect.x + 70, y, self.ui.GREEN, self.ui.font_textbox_black)
            
            # Player score (white text, right-aligned)
            score_text = self.ui.format_number(self.ui.game_state.referee.get_total_score(player))
            score_width = self.ui.font_textbox_black.size(score_text)[0]
            self.draw_text_with_font(score_text, rect.x + 270 - score_width, y, self.ui.WHITE, self.ui.font_textbox_black)

    def draw_now_playing_player(self):
        """Draw NOW_PLAYING_PLAYER section (overlaps 40px into central panel)"""
        # now_playing_player_nowplaying (160px wide)
        nowplaying_rect = pygame.Rect(20, 180, 160, 40)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, nowplaying_rect)
        
        x = 30
        y = 185
        text = "NOW "
        self.draw_text_with_font(text, x, y, self.ui.BLUE, self.ui.font_textbar_semibold)
        x += self.ui.font_textbar_semibold.size(text)[0]
        text = "PLAYING"
        self.draw_text_with_font(text, x, y, self.ui.BLUE, self.ui.font_textbar_black)
        
        # now_playing_player_player (360px wide, overlaps 40px into central panel)
        player_rect = pygame.Rect(180, 180, 340, 40)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, player_rect)
        
        # now_playing_player_clickangle (20px wide, overlaps into central panel)
        clickangle_rect = pygame.Rect(520, 180, 20, 40)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, clickangle_rect)
        
        # Draw rotated "CLICK" text
        click_text = self.ui.font_minititle_black.render("CLICK", True, self.ui.BLUE)
        rotated_click = pygame.transform.rotate(click_text, 90)
        click_rect = rotated_click.get_rect(center=(530, 200))
        self.ui.screen.blit(rotated_click, click_rect)
        
        x = 190
        y = 185  # Aligned with NOW PLAYING text at top
        username = self.ui.game_state.current_player.user.username
        text = "@"
        self.draw_text_with_font(text, x, y, self.ui.BLUE, self.ui.font_mediumtextbar_semibold)
        x += self.ui.font_mediumtextbar_semibold.size(text)[0]
        text = username[1:] if username.startswith("@") else username
        self.draw_text_with_font(text, x, y, self.ui.BLUE, self.ui.font_mediumtextbar_black)

    def draw_rt_stats(self):
        """Draw RT_STATS section (8 rows with alternating colors)"""
        rect = self.ui.sections["RT_STATS"]
        
        # rt_stats_minititle_bar
        minititle_bar = pygame.Rect(rect.x, rect.y, 160, 20)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, minititle_bar)
        x_pos = rect.x + 10
        y_pos = rect.y + 5  # Added 5px padding from top
        text = "RT "
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_semibold)
        x_pos += self.ui.font_minititle_semibold.size(text)[0]
        text = "STATS"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_black)
        
        # rt_stats_base (8 rows, alternating colors)
        rows = [
            ("TURN\nNUMBER", str(self.ui.game_state.current_player.turn_count + 1), self.ui.DARK_GREEN),
            ("ROLLS\nROLLED", str(self.ui.game_state.current_player.roll_count), self.ui.MEDIUM_GREEN),
            ("STASH\nNUMBER", self.ui.game_state.referee.get_stash_number(), self.ui.DARK_GREEN),
            ("MOVED TO\nSTASHSTASH", str(self.ui.game_state.current_player.full_stashes_moved_this_turn), self.ui.MEDIUM_GREEN),
            ("POINTS IN\nSTASHSTASH", self.ui.format_number(self.ui.game_state.current_player.stash_stash), self.ui.DARK_GREEN),
            ("V SCORE\nTURN", self.ui.format_number(self.ui.game_state.referee.calculate_turn_score()), self.ui.MEDIUM_GREEN),
            ("V SCORE\nGAME", self.ui.format_number(self.ui.game_state.referee.calculate_total_score()), self.ui.DARK_GREEN),
            ("VIRTUAL\nGAME RANK", str(self.get_virtual_rank()), self.ui.MEDIUM_GREEN),
        ]
        
        y_offset = 240
        for label_text, value_text, bg_color in rows:
            row_rect = pygame.Rect(rect.x, y_offset, 160, 40)
            pygame.draw.rect(self.ui.screen, bg_color, row_rect)
            
            # Type column (left side, 2 lines)
            lines = label_text.split('\n')
            for i, line in enumerate(lines):
                self.draw_text_with_font(line, rect.x + 10, y_offset + 5 + (i * 14), self.ui.CYAN, self.ui.font_textbox_black)
            
            # Value column (right side)
            value_width = self.ui.font_textbar_black.size(value_text)[0]
            self.draw_text_with_font(value_text, rect.x + 150 - value_width, y_offset + 10, self.ui.WHITE, self.ui.font_textbar_black)
            
            y_offset += 40

    def draw_leaderboard_score(self):
        """Draw LEADERBOARD_SCORE section (turn-by-turn breakdown)"""
        rect = self.ui.sections["LEADERBOARD_SCORE"]
        
        # leaderboard_score_minititle_bar
        minititle_bar = pygame.Rect(rect.x, rect.y, 320, 20)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, minititle_bar)
        x_pos = rect.x + 10
        y_pos = rect.y + 5  # Added 5px padding from top
        text = "SCORE"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_black)
        x_pos += self.ui.font_minititle_black.size(text)[0]
        text = "BOARD"
        self.draw_text_with_font(text, x_pos, y_pos, self.ui.BLUE, self.ui.font_minititle_semibold)
        
        # Type row headers
        type_row_y = rect.y + 20
        
        # TURN column header (60px)
        turn_header = pygame.Rect(rect.x, type_row_y, 60, 20)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, turn_header)
        self.draw_text_with_font("TURN", rect.x + 10, type_row_y + 5, self.ui.CYAN, self.ui.font_minititle_black)
        
        # POINTS column header (140px)
        points_header = pygame.Rect(rect.x + 60, type_row_y, 140, 20)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, points_header)
        self.draw_text_with_font("POINTS", rect.x + 70, type_row_y + 5, self.ui.CYAN, self.ui.font_minititle_black)
        
        # R column header (40px - was 60px, now 20px narrower)
        r_header = pygame.Rect(rect.x + 200, type_row_y, 40, 20)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, r_header)
        r_width = self.ui.font_minititle_black.size("R")[0]
        self.draw_text_with_font("R", rect.x + 230 - r_width, type_row_y + 5, self.ui.CYAN, self.ui.font_minititle_black)
        
        # S column header (40px)
        s_header = pygame.Rect(rect.x + 240, type_row_y, 40, 20)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, s_header)
        s_width = self.ui.font_minititle_black.size("S")[0]
        self.draw_text_with_font("S", rect.x + 270 - s_width, type_row_y + 5, self.ui.CYAN, self.ui.font_minititle_black)
        
        # Red sidebar (40px) - now starts at X:280
        sidebar_header = pygame.Rect(rect.x + 280, type_row_y, 40, 20)
        pygame.draw.rect(self.ui.screen, self.ui.DARKER_RED, sidebar_header)
        
        # Base row (scrollable turn data) - Draw background for all 13 rows
        base_row_y = rect.y + 40
        base_row_height = 260  # 13 rows * 20px each
        
        # Always draw backgrounds for all 13 possible rows
        for row_idx in range(13):
            y = base_row_y + (row_idx * 20)
            
            # TURN column background (dark blue) - 60px
            turn_col = pygame.Rect(rect.x, y, 60, 20)
            pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, turn_col)
            
            # POINTS column background (blue) - 140px
            points_col = pygame.Rect(rect.x + 60, y, 140, 20)
            pygame.draw.rect(self.ui.screen, self.ui.BLUE, points_col)
            
            # R column background (dark blue) - 40px
            r_col = pygame.Rect(rect.x + 200, y, 40, 20)
            pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, r_col)
            
            # S column background (blue) - 40px
            s_col = pygame.Rect(rect.x + 240, y, 40, 20)
            pygame.draw.rect(self.ui.screen, self.ui.BLUE, s_col)
            
            # Red sidebar - 40px
            sidebar_col = pygame.Rect(rect.x + 280, y, 40, 20)
            pygame.draw.rect(self.ui.screen, self.ui.DARKER_RED, sidebar_col)
        
        current_player = self.ui.game_state.current_player
        
        # Draw actual turn data on top of backgrounds
        y = base_row_y + 5
        for turn_num in range(1, min(current_player.turn_count + 1, 14)):  # FIXED: Use player's turn_count  # Max 13 turns displayed
            turn_data = current_player.get_turn_score(turn_num)
            
            # TURN number (cyan text)
            self.draw_text_with_font(self.ui.format_number(turn_num), rect.x + 10, y, self.ui.CYAN, self.ui.font_textbox_semibold)
            
            # POINTS (white text)
            self.draw_text_with_font(self.ui.format_number(turn_data["SCORE"]), rect.x + 70, y, self.ui.WHITE, self.ui.font_textbox_semibold)
            
            # R (rolls - white text, right-aligned in 40px column)
            r_text = self.ui.format_number(turn_data["ROLLS"])
            r_width = self.ui.font_textbox_semibold.size(r_text)[0]
            self.draw_text_with_font(r_text, rect.x + 230 - r_width, y, self.ui.WHITE, self.ui.font_textbox_semibold)
            
            # S (stashes - white text, right-aligned in 40px column)
            s_text = self.ui.format_number(turn_data["STASHES"])
            s_width = self.ui.font_textbox_semibold.size(s_text)[0]
            self.draw_text_with_font(s_text, rect.x + 270 - s_width, y, self.ui.WHITE, self.ui.font_textbox_semibold)
            
            y += 20
        
        # Total row
        total_row_y = rect.y + 300
        total_row_height = 40
        
        # Calculate totals
        total_score = current_player.get_total_score()
        total_rolls = sum(turn_data["ROLLS"] for turn_data in current_player.turn_scores.values())
        total_stashes = sum(turn_data["STASHES"] for turn_data in current_player.turn_scores.values())
        
        # TOTAL label column
        total_label = pygame.Rect(rect.x, total_row_y, 60, total_row_height)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, total_label)
        self.draw_text_with_font("TOTAL", rect.x + 10, total_row_y + 5, self.ui.CYAN, self.ui.font_minititle_black)
        
        # Total POINTS column
        total_points_col = pygame.Rect(rect.x + 60, total_row_y, 140, total_row_height)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, total_points_col)
        self.draw_text_with_font(self.ui.format_number(total_score), rect.x + 70, total_row_y + 5, self.ui.WHITE, self.ui.font_textbox_semibold)
        
        # Total R column (40px)
        total_r_col = pygame.Rect(rect.x + 200, total_row_y, 40, total_row_height)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, total_r_col)
        r_text = self.ui.format_number(total_rolls)
        r_width = self.ui.font_textbox_semibold.size(r_text)[0]
        self.draw_text_with_font(r_text, rect.x + 230 - r_width, total_row_y + 5, self.ui.WHITE, self.ui.font_textbox_semibold)
        
        # Total S column (40px)
        total_s_col = pygame.Rect(rect.x + 240, total_row_y, 40, total_row_height)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, total_s_col)
        s_text = self.ui.format_number(total_stashes)
        s_width = self.ui.font_textbox_semibold.size(s_text)[0]
        self.draw_text_with_font(s_text, rect.x + 270 - s_width, total_row_y + 5, self.ui.WHITE, self.ui.font_textbox_semibold)
        
        # Red sidebar for total row (40px)
        total_sidebar = pygame.Rect(rect.x + 280, total_row_y, 40, total_row_height)
        pygame.draw.rect(self.ui.screen, self.ui.DARKER_RED, total_sidebar)

    def draw_bank_button(self):
        """Draw BANK_BUTTON section with hover effect (overlaps 40px into central panel)"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(20, 560, 520, 80)
        
        # Check hover
        is_hovering = button_rect.collidepoint(mouse_pos) and self.ui.bank_button_enabled
        self.ui.bank_button_hover = is_hovering
        
        # Choose colors based on state
        if is_hovering:
            bg_color = self.ui.BLUE  # Changed from RED to BLUE
            text_color = self.ui.GREEN  # Changed from WHITE to GREEN
        else:
            bg_color = self.ui.GREEN
            text_color = self.ui.BLUE
        
        # bank_button_bigbar_bigtext (500px wide)
        bigtext_rect = pygame.Rect(20, 560, 500, 80)
        pygame.draw.rect(self.ui.screen, bg_color, bigtext_rect)
        
        # bank_button_bigbar_clickangle (20px wide, rotated text, overlaps into central panel)
        clickangle_rect = pygame.Rect(520, 560, 20, 80)
        pygame.draw.rect(self.ui.screen, bg_color, clickangle_rect)
        
        # Draw rotated "CLICK" text
        click_text = self.ui.font_minititle_black.render("CLICK", True, text_color)
        rotated_click = pygame.transform.rotate(click_text, 90)
        click_rect = rotated_click.get_rect(center=(530, 600))
        self.ui.screen.blit(rotated_click, click_rect)
        
        # Draw text
        if is_hovering:
            virtual_game_score = self.ui.game_state.referee.calculate_total_score()
            text1 = "BANKING FOR "
            self.draw_text_with_font(text1, 30, 565, text_color, self.ui.font_bigtextbar_semibold)
            x = 30 + self.ui.font_bigtextbar_semibold.size(text1)[0]
            
            text2 = f"{self.ui.format_number(virtual_game_score)} POINTS"
            self.draw_text_with_font(text2, x, 565, text_color, self.ui.font_bigtextbar_black)
            x += self.ui.font_bigtextbar_black.size(text2)[0]
            
            text3 = " GAME SCORE"
            self.draw_text_with_font(text3, x, 565, text_color, self.ui.font_bigtextbar_semibold)
        else:
            virtual_turn_score = self.ui.game_state.referee.calculate_turn_score()
            text1 = "BANK "
            self.draw_text_with_font(text1, 30, 565, text_color, self.ui.font_bigtextbar_semibold)
            x = 30 + self.ui.font_bigtextbar_semibold.size(text1)[0]
            
            text2 = f"{self.ui.format_number(virtual_turn_score)} POINTS"
            self.draw_text_with_font(text2, x, 565, text_color, self.ui.font_bigtextbar_black)

    def draw_stash_section(self):
        """Draw STASH section with 3 state variations"""
        # Import StashState here to avoid circular import
        from ui.in_game.in_game_ui import StashState
        
        if self.ui.stash_state == StashState.BASE:
            self.draw_stash_base()
        elif self.ui.stash_state == StashState.SELECTED:
            self.draw_stash_selected()
        elif self.ui.stash_state == StashState.FULL:
            self.draw_stash_full()

    def draw_stash_base(self):
        """Draw stash_base variation (RED theme)"""
        # stash_base_stash_uppertextbox
        upper_rect = pygame.Rect(20, 640, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.RED, upper_rect)
        
        x = 30
        y = 645
        stash_num = self.ui.game_state.referee.get_stash_number()
        text1 = stash_num + " "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text1)[0]
        
        text2 = "STASH "
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text2)[0]
        
        stash_points = self.ui.game_state.current_player.get_stash_score()
        text3 = f"{self.ui.format_number(stash_points)} POINTS"
        self.draw_text_with_font(text3, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        
        # stash_base_stash_stashplank_button (not clickable, red plank) - 440x110
        plank_rect = pygame.Rect(20, 680, 440, 110)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_RED, plank_rect)
        self.ui.screen.blit(self.ui.stashplank_images["red"], (20, 680))
        
        # Draw stashed dice
        self.draw_stashed_dice()
        
        # stash_base_stash_lowertextbox
        lower_rect = pygame.Rect(20, 800, 440, 80)
        pygame.draw.rect(self.ui.screen, self.ui.RED, lower_rect)
        
        x = 30
        y = 805
        text1 = "CLICK ON DICE TO SELECT FOR "
        self.draw_text_with_font(text1, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        
        y += 18
        x = 30
        text2 = "STASHING"
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        # STASHSTASH section
        self.draw_stashstash_base()

    def draw_stash_selected(self):
        """Draw stash_selected variation (BLUE theme)"""
        mouse_pos = pygame.mouse.get_pos()
        
        # stash_selected_stash_uppertextbox
        upper_rect = pygame.Rect(20, 640, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, upper_rect)
        
        x = 30
        y = 645
        stash_num = self.ui.game_state.referee.get_stash_number()
        text1 = stash_num + " "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text1)[0]
        
        text2 = "STASH "
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text2)[0]
        
        stash_points = self.ui.game_state.current_player.get_stash_score()
        text3 = f"{self.ui.format_number(stash_points)} POINTS"
        self.draw_text_with_font(text3, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        
        # stash_selected_stash_stashplank_button (clickable) - 440x110, no overlap
        plank_button_rect = pygame.Rect(20, 680, 440, 110)
        is_hovering = plank_button_rect.collidepoint(mouse_pos)
        self.ui.stash_button_hover = is_hovering
        
        if is_hovering:
            # Hover state - show hover effect
            stashplank_rect = pygame.Rect(20, 680, 440, 110)
            pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, stashplank_rect)
            
            # Draw red plank background
            self.ui.screen.blit(self.ui.stashplank_images["red"], (20, 680))
            
            # Draw hover overlay
            self.ui.screen.blit(self.ui.stashplank_images["hover"], (20, 680))
        else:
            # Normal state - blue plank
            stashplank_rect = pygame.Rect(20, 680, 440, 110)
            pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, stashplank_rect)
            self.ui.screen.blit(self.ui.stashplank_images["blue"], (20, 680))
        
        # Draw stashed dice and selected dice
        self.draw_stashed_dice()
        self.draw_selected_dice_in_stash()
        
        # stash_selected_stash_lowertextbox
        lower_rect = pygame.Rect(20, 800, 440, 80)
        pygame.draw.rect(self.ui.screen, self.ui.RED, lower_rect)
        
        x = 30
        y = 805
        
        selected_points = self.ui.game_state.referee.calculate_score([self.ui.game_state.dice_values[i] for i in self.ui.game_state.selected_dice])
        text1 = "STASHING ADDS "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text1)[0]
        
        text2 = f"{self.ui.format_number(selected_points)} POINTS"
        self.draw_text_with_font(text2, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        
        y += 18
        x = 30
        
        text3 = "UNLOCKS "
        self.draw_text_with_font(text3, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text3)[0]
        
        text4 = "ROLL AGAIN OPTION "
        self.draw_text_with_font(text4, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text4)[0]
        
        text5 = "WITH "
        self.draw_text_with_font(text5, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text5)[0]
        
        remaining_dice = len(self.ui.game_state.dice_values) - len(self.ui.game_state.selected_dice)
        text6 = f"{remaining_dice} DICE"
        self.draw_text_with_font(text6, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        # STASHSTASH section
        self.draw_stashstash_selected()

    def draw_stash_full(self):
        """Draw stash_full variation (GREEN theme)"""
        # stash_full_stash_uppertextbox
        upper_rect = pygame.Rect(20, 640, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, upper_rect)
        
        x = 30
        y = 645
        stash_num = self.ui.game_state.referee.get_stash_number()
        text1 = stash_num + " "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text1)[0]
        
        text2 = "STASH "
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text2)[0]
        
        stash_points = self.ui.game_state.current_player.get_stash_score()
        text3 = f"{self.ui.format_number(stash_points)} POINTS"
        self.draw_text_with_font(text3, x, y, self.ui.WHITE, self.ui.font_textbox_black)
        
        # stash_full_stash_stashplank_button (not clickable, green plank) - 440x110
        plank_rect = pygame.Rect(20, 680, 440, 110)
        pygame.draw.rect(self.ui.screen, self.ui.DARKER_GREEN, plank_rect)
        self.ui.screen.blit(self.ui.stashplank_images["green"], (20, 680))
        
        # Draw stashed dice (all 6)
        self.draw_stashed_dice()
        
        # stash_full_stash_lowertextbox
        lower_rect = pygame.Rect(20, 800, 440, 80)
        pygame.draw.rect(self.ui.screen, self.ui.MEDIUM_GREEN, lower_rect)
        
        x = 30
        y = 805
        text1 = "STASH FULL"
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        y += 18
        x = 30
        text2 = "CLICK BELOW TO MOVE TO "
        self.draw_text_with_font(text2, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text2)[0]
        
        text3 = "STASHSTASH"
        self.draw_text_with_font(text3, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        # STASHSTASH section (clickable button)
        self.draw_stashstash_full()

    def draw_stashstash_base(self):
        """Draw STASHSTASH section for stash_base state"""
        # stash_base_stashstash_uppertextbox
        upper_rect = pygame.Rect(20, 880, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_RED, upper_rect)
        
        x = 30
        y = 885
        text1 = "STASHSTASH "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text1)[0]
        
        stashes_moved = self.ui.game_state.current_player.full_stashes_moved_this_turn
        text2 = f"{stashes_moved} STASHES"
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        # stash_base_stashstash_bigbar_button (not clickable)
        bigbar_rect = pygame.Rect(20, 920, 440, 80)
        pygame.draw.rect(self.ui.screen, self.ui.RED, bigbar_rect)
        
        stashstash_points = self.ui.game_state.current_player.stash_stash
        points_text = f"{self.ui.format_number(stashstash_points)} POINTS"
        self.draw_text_with_font(points_text, 30, 925, self.ui.WHITE, self.ui.font_bigtextbar_black)
        
        # stash_base_stashstash_lowertextbox
        lower_rect = pygame.Rect(20, 1000, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_RED, lower_rect)
        
        x = 30
        y = 1005
        text1 = "MAKE A FULL STASH"
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        y += 18
        x = 30
        text2 = "STASH "
        self.draw_text_with_font(text2, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text2)[0]
        
        stashed_count = len(self.ui.game_state.current_player.stashed_dice)
        dice_needed = 6 - stashed_count
        text3 = f"{dice_needed} MORE "
        self.draw_text_with_font(text3, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text3)[0]
        
        text4 = "DICE"
        self.draw_text_with_font(text4, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)

    def draw_stashstash_selected(self):
        """Draw STASHSTASH section for stash_selected state"""
        # stash_selected_stashstash_uppertextbox
        upper_rect = pygame.Rect(20, 880, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, upper_rect)
        
        x = 30
        y = 885
        text1 = "STASHSTASH "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text1)[0]
        
        stashes_moved = self.ui.game_state.current_player.full_stashes_moved_this_turn
        text2 = f"{stashes_moved} STASHES"
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        # stash_selected_stashstash_bigbar_button (not clickable)
        bigbar_rect = pygame.Rect(20, 920, 480, 80)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, bigbar_rect)
        
        stashstash_points = self.ui.game_state.current_player.stash_stash
        points_text = f"{self.ui.format_number(stashstash_points)} POINTS"
        self.draw_text_with_font(points_text, 30, 925, self.ui.WHITE, self.ui.font_bigtextbar_black)
        
        # stash_selected_stashstash_lowertextbox
        lower_rect = pygame.Rect(20, 1000, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, lower_rect)
        
        x = 30
        y = 1005
        text1 = "MAKE A FULL STASH"
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        y += 18
        x = 30
        text2 = "STASH "
        self.draw_text_with_font(text2, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text2)[0]
        
        stashed_count = len(self.ui.game_state.current_player.stashed_dice)
        selected_count = len(self.ui.game_state.selected_dice)
        dice_needed = 6 - (stashed_count + selected_count)
        text3 = f"{dice_needed} MORE "
        self.draw_text_with_font(text3, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text3)[0]
        
        text4 = "DICE"
        self.draw_text_with_font(text4, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)

    def draw_stashstash_full(self):
        """Draw STASHSTASH section for stash_full state (clickable button)"""
        mouse_pos = pygame.mouse.get_pos()
        
        # stash_full_stashstash_uppertextbox
        upper_rect = pygame.Rect(20, 880, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.DARKER_GREEN, upper_rect)
        
        x = 30
        y = 885
        text1 = "STASHSTASH "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text1)[0]
        
        stashes_moved = self.ui.game_state.current_player.full_stashes_moved_this_turn
        text2 = f"{stashes_moved} STASHES"
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        # stash_full_stashstash_bigbar_button (CLICKABLE)
        button_rect = pygame.Rect(20, 920, 500, 80)
        is_hovering = button_rect.collidepoint(mouse_pos)
        self.ui.stashstash_button_hover = is_hovering
        
        if is_hovering:
            # Hover state - red background
            bigbar_rect = pygame.Rect(20, 920, 460, 80)
            pygame.draw.rect(self.ui.screen, self.ui.RED, bigbar_rect)
            
            sidebar_rect = pygame.Rect(480, 920, 20, 80)
            pygame.draw.rect(self.ui.screen, self.ui.RED, sidebar_rect)
            
            text_color = self.ui.WHITE
        else:
            # Normal state - green background
            bigbar_rect = pygame.Rect(20, 920, 460, 80)
            pygame.draw.rect(self.ui.screen, self.ui.MEDIUM_GREEN, bigbar_rect)
            
            sidebar_rect = pygame.Rect(480, 920, 20, 80)
            pygame.draw.rect(self.ui.screen, self.ui.MEDIUM_GREEN, sidebar_rect)
            
            text_color = self.ui.WHITE
        
        stashstash_points = self.ui.game_state.current_player.stash_stash
        points_text = f"{self.ui.format_number(stashstash_points)} POINTS"
        self.draw_text_with_font(points_text, 30, 925, text_color, self.ui.font_bigtextbar_black)
        
        # Draw rotated "CLICK" text
        click_color = self.ui.BLUE if is_hovering else self.ui.BLUE
        click_text = self.ui.font_minititle_black.render("CLICK", True, click_color)
        rotated_click = pygame.transform.rotate(click_text, 90)
        click_rect = rotated_click.get_rect(center=(490, 960))
        self.ui.screen.blit(rotated_click, click_rect)
        
        # stash_full_stashstash_lowertextbox
        lower_rect = pygame.Rect(20, 1000, 440, 40)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, lower_rect)
        
        x = 30
        y = 1005
        text1 = "ADDS "
        self.draw_text_with_font(text1, x, y, self.ui.GREEN, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text1)[0]
        
        stash_points = self.ui.game_state.current_player.get_stash_score()
        text2 = f"{self.ui.format_number(stash_points)} POINTS"
        self.draw_text_with_font(text2, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        
        y += 18
        x = 30
        text3 = "UNLOCKS "
        self.draw_text_with_font(text3, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text3)[0]
        
        text4 = "ROLL AGAIN OPTION "
        self.draw_text_with_font(text4, x, y, self.ui.GREEN, self.ui.font_textbox_black)
        x += self.ui.font_textbox_black.size(text4)[0]
        
        text5 = "WITH "
        self.draw_text_with_font(text5, x, y, self.ui.WHITE, self.ui.font_textbox_semibold)
        x += self.ui.font_textbox_semibold.size(text5)[0]
        
        text6 = "6 DICE"
        self.draw_text_with_font(text6, x, y, self.ui.GREEN, self.ui.font_textbox_black)

    def draw_stashed_dice(self):
        """Draw stashed dice on the plank"""
        stashed_dice = self.ui.game_state.current_player.stashed_dice
        for i, die_value in enumerate(stashed_dice):
            if i < 6:  # Only draw up to 6 dice
                pos = self.ui.stash_dice_positions[i]
                self.ui.screen.blit(self.ui.dice_images['red'][die_value - 1], pos)

    def draw_selected_dice_in_stash(self):
        """Draw selected dice (in blue) in the stash plank"""
        stashed_count = len(self.ui.game_state.current_player.stashed_dice)
        selected_dice_values = [self.ui.game_state.dice_values[i] for i in self.ui.game_state.selected_dice]
        
        for i, die_value in enumerate(selected_dice_values):
            position_index = stashed_count + i
            if position_index < 6:
                pos = self.ui.stash_dice_positions[position_index]
                self.ui.screen.blit(self.ui.dice_images['blue'][die_value - 1], pos)


    def draw_message_balloon(self, surface, message, x, y, max_width):
        """
        Draw a message balloon (text bubble) for G-REF or BOT messages.
        
        Args:
            surface: Surface to draw on
            message: Message object (GREFMessage or BOTMessage)
            x: X coordinate
            y: Y coordinate
            max_width: Maximum width for text wrapping
            
        Returns:
            Height of the drawn balloon
        """
        from core.messaging import MessageType
        
        # Determine balloon style based on message type
        if message.type == MessageType.GREF:
            # G-REF: Red balloon, left-aligned, left arrow
            bg_color = (220, 20, 20)  # Red
            text_color = (255, 255, 255)  # White
            border_color = (180, 0, 0)  # Dark red
            align_left = True
        else:  # BOT
            # BOT: Dark blue balloon, right-aligned, right arrow
            bg_color = (20, 20, 120)  # Dark blue
            text_color = (255, 255, 255)  # White
            border_color = (10, 10, 80)  # Darker blue
            align_left = False
        
        # Measure text size for balloon dimensions
        font = self.ui.fonts['regular'][14] if hasattr(self.ui, 'fonts') else pygame.font.Font(None, 14)
        
        # Word wrap the message content
        words = message.content.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = font.size(word + " ")[0]
            if current_width + word_width > max_width - 40:  # Leave margin
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    lines.append(word)
                    current_line = []
                    current_width = 0
            else:
                current_line.append(word)
                current_width += word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Calculate balloon dimensions
        line_height = font.get_height() + 2
        balloon_height = len(lines) * line_height + 20  # Padding
        balloon_width = min(max_width - 40, max([font.size(line)[0] for line in lines]) + 20)
        
        # Draw balloon background
        if align_left:
            balloon_rect = pygame.Rect(x + 10, y, balloon_width, balloon_height)
        else:
            balloon_rect = pygame.Rect(x + max_width - balloon_width - 10, y, balloon_width, balloon_height)
        
        pygame.draw.rect(surface, bg_color, balloon_rect, border_radius=8)
        pygame.draw.rect(surface, border_color, balloon_rect, width=2, border_radius=8)
        
        # Draw sender name bar at top
        name_font = self.ui.fonts['regular'][12] if hasattr(self.ui, 'fonts') else pygame.font.Font(None, 12)
        name_surface = name_font.render(message.sender, True, text_color)
        surface.blit(name_surface, (balloon_rect.x + 10, balloon_rect.y + 5))
        
        # Draw message text
        text_y = balloon_rect.y + 25
        for line in lines:
            text_surface = font.render(line, True, text_color)
            surface.blit(text_surface, (balloon_rect.x + 10, text_y))
            text_y += line_height
        
        return balloon_height + 10  # Height + spacing


    def draw_message_balloon(self, surface, message, x, y, max_width):
        """
        Draw a message balloon (text bubble) for G-REF or BOT messages.
        
        Args:
            surface: Surface to draw on
            message: Message object (GREFMessage or BOTMessage)
            x: X coordinate
            y: Y coordinate
            max_width: Maximum width for text wrapping
            
        Returns:
            Height of the drawn balloon
        """
        from core.messaging import MessageType
        
        # Determine balloon style based on message type
        if message.type == MessageType.GREF:
            # G-REF: Red balloon, left-aligned, left arrow
            bg_color = (220, 20, 20)  # Red
            text_color = (255, 255, 255)  # White
            border_color = (180, 0, 0)  # Dark red
            align_left = True
        else:  # BOT
            # BOT: Dark blue balloon, right-aligned, right arrow
            bg_color = (20, 20, 120)  # Dark blue
            text_color = (255, 255, 255)  # White
            border_color = (10, 10, 80)  # Darker blue
            align_left = False
        
        # Measure text size for balloon dimensions
        font = self.ui.fonts['regular'][14] if hasattr(self.ui, 'fonts') else pygame.font.Font(None, 14)
        
        # Word wrap the message content
        words = message.content.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = font.size(word + " ")[0]
            if current_width + word_width > max_width - 40:  # Leave margin
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    lines.append(word)
                    current_line = []
                    current_width = 0
            else:
                current_line.append(word)
                current_width += word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Calculate balloon dimensions
        line_height = font.get_height() + 2
        balloon_height = len(lines) * line_height + 20  # Padding
        balloon_width = min(max_width - 40, max([font.size(line)[0] for line in lines]) + 20)
        
        # Draw balloon background
        if align_left:
            balloon_rect = pygame.Rect(x + 10, y, balloon_width, balloon_height)
        else:
            balloon_rect = pygame.Rect(x + max_width - balloon_width - 10, y, balloon_width, balloon_height)
        
        pygame.draw.rect(surface, bg_color, balloon_rect, border_radius=8)
        pygame.draw.rect(surface, border_color, balloon_rect, width=2, border_radius=8)
        
        # Draw sender name bar at top
        name_font = self.ui.fonts['regular'][12] if hasattr(self.ui, 'fonts') else pygame.font.Font(None, 12)
        name_surface = name_font.render(message.sender, True, text_color)
        surface.blit(name_surface, (balloon_rect.x + 10, balloon_rect.y + 5))
        
        # Draw message text
        text_y = balloon_rect.y + 25
        for line in lines:
            text_surface = font.render(line, True, text_color)
            surface.blit(text_surface, (balloon_rect.x + 10, text_y))
            text_y += line_height
        
        return balloon_height + 10  # Height + spacing

    def draw_scrollable_log(self, rect: pygame.Rect):
        """Draw scrollable game log - messages appear at BOTTOM and scroll UP"""
        MAX_LOG_ENTRIES = 100
        log_surface = pygame.Surface((rect.width, rect.height))
        log_surface.fill(self.ui.BLUE)

        # Get messages from message_manager
        messages = self.ui.game_state.message_manager.get_recent_messages(MAX_LOG_ENTRIES)
        
        # PERFORMANCE: Clear cache if messages changed
        if len(messages) != self.last_message_count:
            self.message_cache.clear()
            self.last_message_count = len(messages)
        
        # Calculate heights and render messages (with caching)
        max_width = rect.width - 40  # 20px padding on each side
        message_surfaces = []
        message_heights = []
        
        for i, message in enumerate(messages):
            # Check cache first
            cache_key = f"{i}_{message.timestamp}"
            if cache_key in self.message_cache:
                cached = self.message_cache[cache_key]
                message_surfaces.append((cached[0], cached[3]))
                message_heights.append(cached[2] + 10)
            else:
                # Render and cache
                msg_surface, width, height, is_left_aligned = self.render_message(message, max_width)
                self.message_cache[cache_key] = (msg_surface, width, height, is_left_aligned)
                message_surfaces.append((msg_surface, is_left_aligned))
                message_heights.append(height + 10)  # 10px spacing between messages

        total_height = sum(message_heights)
        visible_height = rect.height
        max_scroll = max(0, total_height - visible_height)

        # FIX #3: Auto-scroll to bottom when new messages arrive (unless user is manually scrolling)
        if self.ui.log_auto_scroll:
            self.ui.log_scroll_y = max_scroll
        else:
            self.ui.log_scroll_y = min(max_scroll, self.ui.log_scroll_y)

        # FIX #2: Render messages from BOTTOM UP (latest at bottom)
        # Start from bottom of visible area
        y = visible_height - 10  # Start 10px from bottom
        
        # Render messages in reverse order (newest first, at bottom)
        for (msg_surface, is_left_aligned), height in zip(reversed(message_surfaces), reversed(message_heights)):
            # Calculate y position for this message
            y -= height
            
            # Adjust for scroll
            adjusted_y = y + max_scroll - self.ui.log_scroll_y
            
            # Only render if visible (PERFORMANCE: skip off-screen messages)
            if adjusted_y + height > 0 and adjusted_y < visible_height:
                # Position based on alignment
                if is_left_aligned:
                    x = 10  # Left padding (FIXED: moved 10px left from 20)
                else:
                    x = rect.width - msg_surface.get_width() - 20  # Right aligned with padding
                
                log_surface.blit(msg_surface, (x, adjusted_y))

        # Draw scrollbar if needed
        if total_height > visible_height:
            scrollbar_height = max(20, (visible_height / total_height) * visible_height)
            scrollbar_pos = (self.ui.log_scroll_y / max_scroll) * (visible_height - scrollbar_height) if max_scroll > 0 else 0
            pygame.draw.rect(log_surface, self.ui.WHITE, (rect.width - 10, scrollbar_pos, 10, scrollbar_height))

        self.ui.screen.blit(log_surface, rect)


    def render_message(self, message, max_width=370):
        """
        Render textballoon with EXACT design specifications.
        
        STRUCTURE:
        1. Name bar (20px height, TRANSPARENT background)
        2. Text block (variable size, COLORED background)
        3. Arrow (20x20px, RIGHT-ANGLED triangle next to text block)
        
        CRITICAL:
        • Name bar background = TRANSPARENT (no colored rectangle!)
        • Arrow is next to TEXT BLOCK, not name bar
        • Arrow = right-angled triangle (2 points same Y, 3rd below)
        • Text = ALL CAPS
        • Player names & points = BOLD font, #00FF00
        • Message text = 24px font (larger)
        """
        # Design constants
        MIN_WIDTH = 240
        MAX_WIDTH = 370
        MIN_TEXT_BLOCK_HEIGHT = 40  # Min for text block (total min 60px with name bar)
        NAME_BAR_HEIGHT = 20
        ARROW_WIDTH = 20
        ARROW_HEIGHT = 20
        DICE_SIZE = 36
        DICE_SPACING = 10
        
        # Determine type
        is_ref = message.sender == '@G-REF'
        
        if is_ref:
            # REF specification
            BG_COLOR = (255, 0, 0)  # #FF0000
            NAME_COLOR_GREF = (255, 0, 0)  # #FF0000 for @G-REF (FIXED: changed from blue)
            NAME_COLOR_TEXT = (255, 255, 255)  # #FFFFFF for rest
            TEXT_COLOR = (255, 255, 255)  # #FFFFFF
            HIGHLIGHT_COLOR = (0, 255, 0)  # #00FF00
            
            TEXT_PAD_LEFT = 10
            TEXT_PAD_TOP = 10
            TEXT_PAD_RIGHT = 20
            TEXT_PAD_BOTTOM = 10
            NAME_PAD_LEFT = 10
            
            text_align = 'left'
        else:
            # BOT specification  
            BG_COLOR = (0, 0, 170)  # #0000AA
            NAME_COLOR = (0, 255, 0)  # #00FF00
            TEXT_COLOR = (255, 255, 255)  # #FFFFFF
            HIGHLIGHT_COLOR = (0, 255, 0)  # #00FF00
            
            TEXT_PAD_LEFT = 20
            TEXT_PAD_TOP = 10
            TEXT_PAD_RIGHT = 10
            TEXT_PAD_BOTTOM = 10
            NAME_PAD_RIGHT = 10
            
            text_align = 'right'
        
        # Fonts (FIXED: using open-sauce-two font with correct sizes)
        # Name bar: 16px BLACK (same as left panel top bars - textbar_black)
        # Message text: 18px regular (between name bar and old 24px)
        try:
            name_font = self.ui.fonts.get('black', {}).get(16, pygame.font.Font(None, 16))
            text_font = self.ui.fonts.get('regular', {}).get(18, pygame.font.Font(None, 18))
            text_font_bold = self.ui.fonts.get('black', {}).get(18, pygame.font.Font(None, 18))  # BLACK for highlights
        except:
            # Fallback to system font if open-sauce-two not available
            name_font = pygame.font.Font(None, 16)
            text_font = pygame.font.Font(None, 18)
            text_font_bold = pygame.font.Font(None, 18)
            text_font_bold.set_bold(True)
        
        # CRITICAL: Convert to ALL CAPS
        message_content = message.content.upper()
        
        # Parse text
        text_parts = self._parse_for_textballoon(message_content)
        
        # Layout text
        text_width = MAX_WIDTH - TEXT_PAD_LEFT - TEXT_PAD_RIGHT - ARROW_WIDTH
        text_lines = self._layout_for_textballoon(
            text_parts, text_font, text_font_bold, text_width, DICE_SIZE, DICE_SPACING
        )
        
        # Calculate dimensions - FIXED: properly calculate height for each line
        line_height = text_font.get_height()
        
        # CRITICAL FIX: Calculate actual height needed for each line (dice are 36px tall)
        total_text_height = 0
        for line_parts in text_lines:
            has_dice_in_line = any(part[0] == 'dice' for part in line_parts)
            if has_dice_in_line:
                # Line with dice needs dice height (36px) plus some spacing
                total_text_height += max(DICE_SIZE, line_height) + 2
            else:
                # Regular text line
                total_text_height += line_height
        
        text_block_height = total_text_height + TEXT_PAD_TOP + TEXT_PAD_BOTTOM
        text_block_height = max(MIN_TEXT_BLOCK_HEIGHT, text_block_height)
        
        # Calculate width
        max_line_width = 0
        for line_parts in text_lines:
            line_width = 0
            for part_type, part_value in line_parts:
                if part_type == 'dice':
                    line_width += DICE_SIZE + DICE_SPACING
                elif part_type in ['text', 'player', 'points']:
                    font = text_font_bold if part_type in ['player', 'points'] else text_font
                    line_width += font.size(part_value)[0]
            max_line_width = max(max_line_width, line_width)
        
        balloon_width = max(MIN_WIDTH, min(MAX_WIDTH, max_line_width + TEXT_PAD_LEFT + TEXT_PAD_RIGHT + ARROW_WIDTH))
        
        total_height = NAME_BAR_HEIGHT + text_block_height
        total_width = balloon_width
        
        # Create surface
        surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        
        if is_ref:
            # REF LAYOUT
            
            # 1. NAME BAR (transparent background, text only)
            name_x = ARROW_WIDTH + NAME_PAD_LEFT
            name_y = (NAME_BAR_HEIGHT - name_font.get_height()) // 2
            
            gref_surf = name_font.render("@G-REF", True, NAME_COLOR_GREF)
            surface.blit(gref_surf, (name_x, name_y))
            name_x += gref_surf.get_width()
            
            official_surf = name_font.render(" [ GAMEOFFICIAL ]", True, NAME_COLOR_TEXT)
            surface.blit(official_surf, (name_x, name_y))
            
            # 2. TEXT BLOCK (colored background)
            text_block_y = NAME_BAR_HEIGHT
            text_block_width = balloon_width - ARROW_WIDTH
            text_rect = pygame.Rect(ARROW_WIDTH, text_block_y, text_block_width, text_block_height)
            pygame.draw.rect(surface, BG_COLOR, text_rect)
            
            # 3. ARROW (right-angled triangle pointing LEFT)
            arrow_y = text_block_y + 10  # FIXED: moved 10px down
            arrow_pts = [
                (0, arrow_y),
                (ARROW_WIDTH, arrow_y),
                (ARROW_WIDTH, arrow_y + ARROW_HEIGHT)
            ]
            pygame.draw.polygon(surface, BG_COLOR, arrow_pts)
            
            # 4. RENDER TEXT
            self._render_textballoon_lines(
                surface, text_lines, text_font, text_font_bold,
                text_rect.left + TEXT_PAD_LEFT,
                text_rect.top + TEXT_PAD_TOP,
                TEXT_COLOR, HIGHLIGHT_COLOR,
                'left', text_block_width - TEXT_PAD_LEFT - TEXT_PAD_RIGHT,
                DICE_SIZE, DICE_SPACING
            )
            
        else:
            # BOT LAYOUT (right-aligned)
            
            # 1. NAME BAR (transparent background, text only)
            bot_name_surf = name_font.render(message.sender, True, NAME_COLOR)
            name_x = balloon_width - ARROW_WIDTH - bot_name_surf.get_width() - NAME_PAD_RIGHT
            name_y = (NAME_BAR_HEIGHT - name_font.get_height()) // 2
            surface.blit(bot_name_surf, (name_x, name_y))
            
            # 2. TEXT BLOCK (colored background)
            text_block_y = NAME_BAR_HEIGHT
            text_block_width = balloon_width - ARROW_WIDTH
            text_rect = pygame.Rect(0, text_block_y, text_block_width, text_block_height)
            pygame.draw.rect(surface, BG_COLOR, text_rect)
            
            # 3. ARROW (right-angled triangle pointing RIGHT - properly mirrored from G-REF)
            arrow_y = text_block_y + 10  # FIXED: moved 10px down
            arrow_pts = [
                (text_block_width, arrow_y),                    # top-left
                (text_block_width + ARROW_WIDTH, arrow_y),      # top-right
                (text_block_width, arrow_y + ARROW_HEIGHT)      # bottom-left (pointy end!)
            ]
            pygame.draw.polygon(surface, BG_COLOR, arrow_pts)
            
            # 4. RENDER TEXT
            self._render_textballoon_lines(
                surface, text_lines, text_font, text_font_bold,
                text_rect.left + TEXT_PAD_LEFT,
                text_rect.top + TEXT_PAD_TOP,
                TEXT_COLOR, HIGHLIGHT_COLOR,
                'right', text_block_width - TEXT_PAD_LEFT - TEXT_PAD_RIGHT,
                DICE_SIZE, DICE_SPACING
            )
        
        return surface, total_width, total_height, is_ref
    
    def _parse_for_textballoon(self, text):
        """Parse text for player names, points, dice"""
        parts = []
        i = 0
        
        while i < len(text):
            # Check for dice: <DICE>white_2</DICE>
            if text[i:i+6] == '<DICE>':
                end = text.find('</DICE>', i)
                if end != -1:
                    dice_content = text[i+6:end]  # e.g., "white_2"
                    parts.append(('dice', dice_content))
                    i = end + 7
                    continue
            
            # Check for player name
            if text[i] == '@':
                match = re.match(r'@[A-Z]+-[A-Z]+-[A-Z]+-\d+|@[A-Z]+-[A-Z]+-\d+|@G-REF', text[i:])
                if match:
                    parts.append(('player', match.group(0)))
                    i += len(match.group(0))
                    continue
            
            # Check for points (number + POINTS)
            match = re.match(r'\d+\s+POINTS?', text[i:])
            if match:
                parts.append(('points', match.group(0)))
                i += len(match.group(0))
                continue
            
            # Check for game action words (green + BLACK font)
            # Words: ROLLED, ROLLING, ROLLS, STASHED, STASHES, STASHING, BUST, BUSTED
            match = re.match(r'(ROLLED|ROLLING|ROLLS|STASHED|STASHES|STASHING|BUSTED|BUST)', text[i:])
            if match:
                parts.append(('action', match.group(0)))
                i += len(match.group(0))
                continue
            
            # Regular text
            if not parts or parts[-1][0] != 'text':
                parts.append(('text', text[i]))
            else:
                parts[-1] = ('text', parts[-1][1] + text[i])
            i += 1
        
        return parts
    
    def _layout_for_textballoon(self, parts, reg_font, bold_font, max_width, dice_size, dice_spacing):
        """Layout text parts into lines"""
        lines = []
        current_line = []
        current_width = 0
        
        for part_type, part_value in parts:
            if part_type == 'dice':
                dice_width = dice_size + dice_spacing
                if current_width + dice_width > max_width and current_line:
                    lines.append(current_line)
                    current_line = []
                    current_width = 0
                current_line.append((part_type, part_value))
                current_width += dice_width
            else:
                # Use BLACK font for player names, points, and action words
                font = bold_font if part_type in ['player', 'points', 'action'] else reg_font
                words = part_value.split(' ')
                for word in words:
                    if not word:
                        continue
                    word_text = (' ' + word) if current_line else word
                    word_width = font.size(word_text)[0]
                    
                    if current_width + word_width > max_width and current_line:
                        lines.append(current_line)
                        current_line = []
                        current_width = 0
                        word_text = word
                        word_width = font.size(word_text)[0]
                    
                    current_line.append((part_type, word_text))
                    current_width += word_width
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _render_textballoon_lines(self, surface, lines, reg_font, bold_font,
                                   start_x, start_y, text_color, highlight_color,
                                   align, max_width, dice_size, dice_spacing):
        """Render text lines with dice images - FIXED: proper spacing for dice lines"""
        y = start_y
        base_line_height = reg_font.get_height()
        
        for line_parts in lines:
            # CRITICAL FIX: Check if this line has dice for proper height
            has_dice_in_line = any(part[0] == 'dice' for part in line_parts)
            line_height = max(dice_size, base_line_height) + 2 if has_dice_in_line else base_line_height
            
            # Calculate line width
            line_width = 0
            for part_type, part_value in line_parts:
                if part_type == 'dice':
                    line_width += dice_size + dice_spacing
                else:
                    font = bold_font if part_type in ['player', 'points', 'action'] else reg_font
                    line_width += font.size(part_value)[0]
            
            # Starting x based on alignment
            x = start_x if align == 'left' else start_x + max_width - line_width
            
            # Render each part
            for part_type, part_value in line_parts:
                if part_type == 'dice':
                    # CRITICAL: Render as IMAGE
                    try:
                        dice_key = part_value.lower()  # FIXED: lowercase for lookup (e.g., "white_2")
                        dice_surf = self.ui.dice_renderer.dice_surfaces['textballoon'][dice_key]
                        dice_y = y + (line_height - dice_size) // 2
                        surface.blit(dice_surf, (x, dice_y))
                        x += dice_size + dice_spacing
                    except Exception as e:
                        print(f"Error rendering dice {part_value}: {e}")
                        x += dice_size + dice_spacing
                else:
                    # Use BLACK font for player names, points, and action words
                    # Use GREEN color (#00FF00) for player names, points, and action words
                    font = bold_font if part_type in ['player', 'points', 'action'] else reg_font
                    color = highlight_color if part_type in ['player', 'points', 'action'] else text_color
                    text_surf = font.render(part_value, True, color)
                    # Center text vertically in the line
                    text_y = y + (line_height - text_surf.get_height()) // 2
                    surface.blit(text_surf, (x, text_y))
                    x += text_surf.get_width()
            
            y += line_height

    def _parse_message_text(self, text):
        """
        Parse message text to identify:
          • Player names (to highlight in green)
          • Point values (to highlight in green)
          • Dice notation like [1][2][3] (to render as images)
          
        Returns:
            list: Parsed text parts with types
        """
        parts = []
        current = 0
        
        # Patterns (using raw strings for regex)
        player_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'  # Player names
        points_pattern = r'(\d+)\s*(?:points?|pts)'  # Point values
        dice_pattern = r'\[(\d)\]'  # Dice notation [1] through [6]
        
        while current < len(text):
            # Check for dice
            dice_match = re.match(dice_pattern, text[current:])
            if dice_match:
                parts.append(('dice', int(dice_match.group(1))))
                current += dice_match.end()
                continue
            
            # Check for points
            points_match = re.match(points_pattern, text[current:])
            if points_match:
                parts.append(('points', points_match.group(0)))
                current += points_match.end()
                continue
            
            # Check for player names
            player_match = re.match(player_pattern, text[current:])
            if player_match:
                # Verify it's actually a player name (you might want to check against actual player list)
                parts.append(('player', player_match.group(0)))
                current += player_match.end()
                continue
            
            # Regular character
            if not parts or parts[-1][0] != 'text':
                parts.append(('text', text[current]))
            else:
                # Append to last text part
                parts[-1] = ('text', parts[-1][1] + text[current])
            current += 1
        
        return parts
    
    def _layout_text_with_dice(self, text_parts, font, max_width):
        """
        Layout text parts into lines, handling dice images.
        
        Returns:
            tuple: (lines, dice_positions)
                lines: List of text strings or mixed lists
                dice_positions: Dict mapping dice values to (x, y) positions
        """
        lines = []
        dice_positions = {}
        current_line = []
        current_width = 0
        line_height = font.get_height()
        y = 0
        
        DICE_SIZE = 36
        DICE_SPACING = 10
        
        for part_type, part_value in text_parts:
            if part_type == 'dice':
                # Reserve space for dice
                dice_width = DICE_SIZE + DICE_SPACING
                if current_width + dice_width > max_width:
                    # Start new line
                    lines.append(current_line)
                    current_line = []
                    current_width = 0
                    y += line_height
                
                # Record dice position
                dice_positions[part_value] = (current_width, y)
                current_width += dice_width
                
            else:
                # Regular text
                text = part_value
                words = text.split(' ')
                
                for word in words:
                    word_width = font.size(word + ' ')[0]
                    
                    if current_width + word_width > max_width:
                        # Start new line
                        if current_line:
                            lines.append(current_line)
                        current_line = [(part_type, word + ' ')]
                        current_width = word_width
                        y += line_height
                    else:
                        current_line.append((part_type, word + ' '))
                        current_width += word_width
        
        if current_line:
            lines.append(current_line)
        
        return lines, dice_positions
    
    def _load_dice_image(self, value, size):
        """
        Load and scale dice image from assets/dice/
        
        Args:
            value: Dice value (1-6)
            size: Target size in pixels
            
        Returns:
            pygame.Surface
        """
        # Try multiple possible dice image paths
        possible_paths = [
            f"assets/dice/dice_{value}_36px.png",
            f"assets/dice/dice_{value}.png",
            f"assets/dice/die_{value}.png"
        ]
        
        for dice_path in possible_paths:
            try:
                if Path(dice_path).exists():
                    image = pygame.image.load(dice_path)
                    return pygame.transform.scale(image, (size, size))
            except Exception as e:
                continue
        
        # Fallback: create CLEAR, VISIBLE dice representation
        surface = pygame.Surface((size, size))
        surface.fill((255, 255, 255))  # White background
        
        # Black border
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 3)
        
        # Large number in center
        font = pygame.font.Font(None, int(size * 0.7))
        text = font.render(str(value), True, (0, 0, 0))
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        
        return surface

    def get_entry_height(self, entry, max_width):
        """Calculate height needed for a log entry"""
        words = entry.split()
        x = 0
        lines = 1
        for word in words:
            if word.startswith("<DICE>") and word.endswith("</DICE>"):
                word_width = 36
            else:
                word_width = self.ui.fonts['regular'][16].size(word)[0]
            if x + word_width > max_width:
                lines += 1
                x = word_width
            else:
                x += word_width + 5
        return lines * (self.ui.fonts['regular'][16].get_height() + 2) + 10
        
    def render_log_line(self, surface, line, x, y):
        """Render a single log line with formatting"""
        words = line.split()
        start_x = x
        max_width = surface.get_width() - 30
        line_height = self.ui.fonts['regular'][16].get_height() + 5

        for i, word in enumerate(words):
            if word.startswith("<DICE>") and word.endswith("</DICE>"):
                dice_info = word[6:-7]
                dice_width = 36
                if x + dice_width > max_width:
                    x = start_x
                    y += line_height
                x = self.ui.dice_renderer.render_dice_in_log(surface, dice_info, x, y)
            elif word.startswith("<prefix>") and word.endswith("</prefix>"):
                prefix = word[8:-9]
                word_surface = self.ui.fonts['regular'][16].render(prefix, True, self.ui.WHITE)
                word_width = word_surface.get_width()
                prefix_rect = pygame.Rect(x, y, word_width, self.ui.fonts['regular'][16].get_height())
                pygame.draw.rect(surface, self.ui.BLUE, prefix_rect)
                surface.blit(word_surface, (x, y))
                x += word_width + 5
            elif word.startswith("<player>") and word.endswith("</player>") or word.startswith("@GO-BOT-") or word.startswith("@VIDEO-GAMER-"):
                player = word[8:-9] if word.startswith("<player>") else word
                word_surface = self.ui.fonts['bold'][16].render(player, True, self.ui.GREEN)
                word_width = word_surface.get_width()
                surface.blit(word_surface, (x, y))
                x += word_width + 5
            elif word.startswith("<green>") and word.endswith("</green>"):
                green_text = word[7:-8]
                word_surface = self.ui.fonts['regular'][16].render(green_text, True, self.ui.GREEN)
                word_width = word_surface.get_width()
                surface.blit(word_surface, (x, y))
                x += word_width + 5
            else:
                word_surface = self.ui.fonts['regular'][16].render(word, True, self.ui.WHITE)
                word_width = word_surface.get_width()
                if x + word_width > max_width:
                    x = start_x
                    y += line_height
                surface.blit(word_surface, (x, y))
                x += word_width + 5

        return y + line_height

    def draw_end_game_summary(self):
        """Draw end game summary popup"""
        if self.ui.game_state.current_game_state == GameStateEnum.END_GAME_SUMMARY:
            from ui.in_game.button import Button
            
            summary_rect = self.ui.sections["END_GAME_SUMMARY_POPUP"]
            pygame.draw.rect(self.ui.screen, self.ui.BLUE, summary_rect)
            
            winner = self.ui.game_state.get_winner()
            if winner:
                winner_text = f"{winner.user.username} WINS!"
                score_text = f"SCORE: {self.ui.format_number(winner.get_total_score())}"
                
                self.draw_text_with_font(winner_text, summary_rect.centerx - 100, summary_rect.top + 50, self.ui.WHITE, self.ui.fonts['extra_bold'][36])
                self.draw_text_with_font(score_text, summary_rect.centerx - 100, summary_rect.top + 100, self.ui.WHITE, self.ui.fonts['bold'][24])
            
            restart_button = Button(summary_rect.centerx - 100, summary_rect.bottom - 70, 200, 40, "RESTART GAME", self.ui.GREEN, self.ui.BLACK, self.ui.GREEN, self.ui.BLACK)
            restart_button.draw(self.ui.screen)

    def get_virtual_rank(self):
        """Calculate virtual rank if player banks now"""
        current_player = self.ui.game_state.current_player
        virtual_score = self.ui.game_state.referee.calculate_total_score()
        
        all_scores = [player.get_total_score() for player in self.ui.game_state.players]
        all_scores[self.ui.game_state.players.index(current_player)] = virtual_score
        
        sorted_scores = sorted(all_scores, reverse=True)
        
        rank = sorted_scores.index(virtual_score) + 1
        
        return rank

    def draw_dicecup(self):
        """Draw dicecup section"""
        rect = self.ui.sections["DICECUP"]
        remaining_dice = self.ui.game_state.real_time_counters.rollcupdice_var

        if self.ui.show_green_dicecup or self.ui.game_state.current_game_state == GameStateEnum.NEW_STASH:
            bg_color = (0, 187, 0)
            cup_image_name = "dicecup_green.png"
        elif self.ui.show_blue_dicecup:
            bg_color = (0, 0, 255)
            cup_image_name = "dicecup_blue.png"
        else:
            bg_color = (255, 0, 0)
            cup_image_name = "dicecup_red.png"

        pygame.draw.rect(self.ui.screen, bg_color, rect)

        cup_image = pygame.image.load(os.path.join("assets", cup_image_name))
        
        if self.ui.game_state.current_game_state in [GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL, GameStateEnum.NEW_STASH]:
            dice_image = pygame.image.load(os.path.join("assets", "dicecup_6.png"))
        else:
            dice_image = pygame.image.load(os.path.join("assets", f"dicecup_{remaining_dice}.png"))

        self.ui.screen.blit(cup_image, (rect.left, rect.top))
        self.ui.screen.blit(dice_image, (rect.left + 170, rect.top))  # FIXED: Moved 100px left

        self.ui.dicecup_rect.topleft = (rect.left, rect.top)

        mouse_pos = pygame.mouse.get_pos()
        relative_pos = (mouse_pos[0] - self.ui.dicecup_rect.x, mouse_pos[1] - self.ui.dicecup_rect.y)
        if 0 <= relative_pos[0] < self.ui.dicecup_rect.width and 0 <= relative_pos[1] < self.ui.dicecup_rect.height:
            if self.ui.dicecup_mask.get_at(relative_pos) and self.ui.game_state.referee.can_roll():
                self.ui.screen.blit(self.ui.dicecup_hover, (rect.left, rect.top))
                if not self.ui.rotating_image.rotating:
                    self.ui.rotating_image.start_rotation()
            else:
                self.ui.rotating_image.stop_rotation()
        else:
            self.ui.rotating_image.stop_rotation()

        self.ui.rotating_image.update()
        self.ui.rotating_image.draw(self.ui.screen)

    def draw_bust_box(self):
        """Draw bust notification box"""
        if self.ui.game_state.bust_state:
            if not hasattr(self.ui, 'bust_text_box') or self.ui.bust_text_box is None:
                self.create_bust_text_box()

            if self.ui.bust_text_box:
                pygame.draw.rect(self.ui.screen, self.ui.RED, self.ui.bust_text_box)
                busted_player = self.ui.game_state.busted_player
                lost_points = self.ui.game_state.busted_lost_score
                
                prefix = "@G-REF.:"
                prefix_surface = self.ui.fonts['regular'][18].render(prefix, True, self.ui.WHITE)
                prefix_rect = prefix_surface.get_rect(topleft=(self.ui.bust_text_box.left + 10, self.ui.bust_text_box.top + 10))
                pygame.draw.rect(self.ui.screen, self.ui.BLUE, prefix_rect)
                self.ui.screen.blit(prefix_surface, prefix_rect)
                
                bust_text = f" Oh Noo! {busted_player.user.username} That's a BUST!"
                self.draw_text_with_font(bust_text, self.ui.bust_text_box.left + 10 + prefix_rect.width + 5, self.ui.bust_text_box.top + 10, self.ui.WHITE, self.ui.fonts['regular'][28])
                
                points_text = f"{self.ui.format_number(lost_points)} POINTS LOST!"
                self.draw_text_with_font(points_text, self.ui.bust_text_box.left + 10, self.ui.bust_text_box.top + 60, self.ui.WHITE, self.ui.fonts['regular'][20])
                
                self.draw_text_with_font("TURN ENDED", self.ui.bust_text_box.left + 10, self.ui.bust_text_box.top + 90, self.ui.WHITE, self.ui.fonts['regular'][24])

    def create_bust_text_box(self):
        """Create the bust text box"""
        self.ui.bust_text_box = pygame.Rect(self.ui.WINDOW_WIDTH // 4, self.ui.WINDOW_HEIGHT // 3,
                                        self.ui.WINDOW_WIDTH // 2, self.ui.WINDOW_HEIGHT // 3)

    def draw_dice(self):
        """Draw dice in the snaptray"""
        if self.ui.game_state.dice_values:
            stashable_dice = self.ui.game_state.referee.get_stashable_dice(self.ui.game_state.dice_values)
            formatted_dice = [f"{'green' if i in stashable_dice else 'white'}_{value}" for i, value in enumerate(self.ui.game_state.dice_values)]
            # Get hovered dice but don't pass to renderer to avoid green outline effect
            hovered_dice, hovered_combination = UIHelpers.get_hovered_combination(pygame.mouse.get_pos(), self.ui.dice_rects, self.ui.game_state.dice_values)
            
            if len(self.ui.game_board.dice_positions) != len(self.ui.game_state.dice_values):
                self.ui.game_board.generate_dice_positions(len(self.ui.game_state.dice_values))
            
            # Pass empty list for hovered_dice to remove green outline hover effect
            self.ui.dice_rects = self.ui.dice_renderer.render_dice_in_snaptray(
                formatted_dice,
                self.ui.game_board.dice_positions[:len(self.ui.game_state.dice_values)],
                self.ui.game_state.selected_dice,
                [],  # Empty list - removed green outline hover effect
                stashable_dice
            )
        else:
            self.ui.dice_rects = []


    def draw_ready_up_popup(self):
        """Draw Ready Up popup (blue theme)"""
        mouse_pos = pygame.mouse.get_pos()
        popup_rect = self.ui.sections["READY_UP_POPUP"]
        
        # Check if mouse is hovering over entire popup
        is_hovering = popup_rect.collidepoint(mouse_pos)
        self.ui.ready_up_popup_hover = is_hovering
        
        # Top bar (blue background)
        top_bar = pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 40)
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, top_bar)
        
        # Top bar text "READY UP // POPUP"
        text = "READY UP // POPUP"
        self.draw_text_with_font(text, popup_rect.x + 20, popup_rect.y + 10, self.ui.WHITE, self.ui.font_textbar_semibold)
        
        # Main body (dark blue background)
        main_body = pygame.Rect(popup_rect.x, popup_rect.y + 40, popup_rect.width, 240)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_BLUE, main_body)
        
        # Center-aligned text lines
        y = popup_rect.y + 70
        
        # "IT'S YOUR TURN"
        text1 = "IT'S YOUR TURN"
        text1_width = self.ui.font_bigtextbar_black.size(text1)[0]
        self.draw_text_with_font(text1, popup_rect.centerx - text1_width // 2, y, self.ui.WHITE, self.ui.font_bigtextbar_black)
        y += 50
        
        # Player name "@VIDEO-GAMER-1" in green
        player_name = self.ui.game_state.current_player.user.username
        text2_width = self.ui.font_bigtextbar_black.size(player_name)[0]
        self.draw_text_with_font(player_name, popup_rect.centerx - text2_width // 2, y, self.ui.GREEN, self.ui.font_bigtextbar_black)
        y += 50
        
        # "GET READY"
        text3 = "GET READY"
        text3_width = self.ui.font_bigtextbar_black.size(text3)[0]
        self.draw_text_with_font(text3, popup_rect.centerx - text3_width // 2, y, self.ui.WHITE, self.ui.font_bigtextbar_black)
        
        # Button at bottom
        button_rect = pygame.Rect(popup_rect.x + 120, popup_rect.y + 280, 200, 50)
        button_color = self.ui.RED if is_hovering else self.ui.BLUE
        text_color = self.ui.WHITE
        
        pygame.draw.rect(self.ui.screen, button_color, button_rect)
        
        button_text = "CONFIRM"
        button_text_width = self.ui.font_textbar_black.size(button_text)[0]
        self.draw_text_with_font(button_text, button_rect.centerx - button_text_width // 2, button_rect.centery - 8, text_color, self.ui.font_textbar_black)
    
    def draw_turn_bust_popup(self):
        """Draw Turn Bust popup (red theme)"""
        mouse_pos = pygame.mouse.get_pos()
        popup_rect = self.ui.sections["TURN_BUST_POPUP"]
        
        # Check if mouse is hovering over entire popup
        is_hovering = popup_rect.collidepoint(mouse_pos)
        self.ui.turn_bust_popup_hover = is_hovering
        
        # Top bar (red background)
        top_bar = pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 40)
        pygame.draw.rect(self.ui.screen, self.ui.RED, top_bar)
        
        # Top bar text "TURN BUST // POPUP"
        text = "TURN BUST // POPUP"
        self.draw_text_with_font(text, popup_rect.x + 20, popup_rect.y + 10, self.ui.WHITE, self.ui.font_textbar_semibold)
        
        # Main body (dark red background)
        main_body = pygame.Rect(popup_rect.x, popup_rect.y + 40, popup_rect.width, 290)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_RED, main_body)
        
        # Center-aligned text lines
        y = popup_rect.y + 70
        
        # "UNLUCKY!"
        text1 = "UNLUCKY!"
        text1_width = self.ui.font_bigtextbar_black.size(text1)[0]
        self.draw_text_with_font(text1, popup_rect.centerx - text1_width // 2, y, self.ui.WHITE, self.ui.font_bigtextbar_black)
        y += 50
        
        # Player name in green
        player_name = self.ui.game_state.current_player.user.username
        text2_width = self.ui.font_bigtextbar_black.size(player_name)[0]
        self.draw_text_with_font(player_name, popup_rect.centerx - text2_width // 2, y, self.ui.GREEN, self.ui.font_bigtextbar_black)
        y += 50
        
        # "THAT'S A BUST"
        text3 = "THAT'S A BUST"
        text3_width = self.ui.font_bigtextbar_black.size(text3)[0]
        self.draw_text_with_font(text3, popup_rect.centerx - text3_width // 2, y, self.ui.WHITE, self.ui.font_bigtextbar_black)
        y += 50
        
        # "LOSING X POINTS"
        lost_points = self.ui.game_state.referee.calculate_turn_score()
        losing_text = f"LOSING {self.ui.format_number(lost_points)} POINTS"
        losing_text_width = self.ui.font_mediumtextbar_black.size(losing_text)[0]
        self.draw_text_with_font(losing_text, popup_rect.centerx - losing_text_width // 2, y, self.ui.WHITE, self.ui.font_mediumtextbar_black)
        
        # Button at bottom
        button_rect = pygame.Rect(popup_rect.x + 120, popup_rect.y + 330, 200, 50)
        button_color = self.ui.BLUE if is_hovering else self.ui.RED
        text_color = self.ui.WHITE
        
        pygame.draw.rect(self.ui.screen, button_color, button_rect)
        
        button_text = "I SEE"
        button_text_width = self.ui.font_textbar_black.size(button_text)[0]
        self.draw_text_with_font(button_text, button_rect.centerx - button_text_width // 2, button_rect.centery - 8, text_color, self.ui.font_textbar_black)
    
    def draw_banked_points_popup(self):
        """Draw Banked Points popup (green theme)"""
        mouse_pos = pygame.mouse.get_pos()
        popup_rect = self.ui.sections["BANKED_POINTS_POPUP"]
        
        # Check if mouse is hovering over entire popup
        is_hovering = popup_rect.collidepoint(mouse_pos)
        self.ui.banked_points_popup_hover = is_hovering
        
        # Top bar (green background)
        top_bar = pygame.Rect(popup_rect.x, popup_rect.y, popup_rect.width, 40)
        pygame.draw.rect(self.ui.screen, self.ui.GREEN, top_bar)
        
        # Top bar text "BANKED POINTS // POPUP"
        text = "BANKED POINTS // POPUP"
        self.draw_text_with_font(text, popup_rect.x + 20, popup_rect.y + 10, self.ui.WHITE, self.ui.font_textbar_semibold)
        
        # Main body (dark green background)
        main_body = pygame.Rect(popup_rect.x, popup_rect.y + 40, popup_rect.width, 290)
        pygame.draw.rect(self.ui.screen, self.ui.DARK_GREEN, main_body)
        
        # Center-aligned text lines
        y = popup_rect.y + 70
        
        # "NICE GOING!"
        text1 = "NICE GOING!"
        text1_width = self.ui.font_bigtextbar_black.size(text1)[0]
        self.draw_text_with_font(text1, popup_rect.centerx - text1_width // 2, y, self.ui.WHITE, self.ui.font_bigtextbar_black)
        y += 50
        
        # Player name in green
        player_name = self.ui.game_state.current_player.user.username
        text2_width = self.ui.font_bigtextbar_black.size(player_name)[0]
        self.draw_text_with_font(player_name, popup_rect.centerx - text2_width // 2, y, self.ui.GREEN, self.ui.font_bigtextbar_black)
        y += 50
        
        # "BANKED THEIR POINTS"
        text3 = "BANKED THEIR POINTS"
        text3_width = self.ui.font_mediumtextbar_black.size(text3)[0]
        self.draw_text_with_font(text3, popup_rect.centerx - text3_width // 2, y, self.ui.WHITE, self.ui.font_mediumtextbar_black)
        y += 45
        
        # "ADDING X POINTS"
        banked_points = self.ui.game_state.referee.calculate_turn_score()
        adding_text = f"ADDING {self.ui.format_number(banked_points)} POINTS"
        adding_text_width = self.ui.font_mediumtextbar_black.size(adding_text)[0]
        self.draw_text_with_font(adding_text, popup_rect.centerx - adding_text_width // 2, y, self.ui.WHITE, self.ui.font_mediumtextbar_black)
        
        # Button at bottom
        button_rect = pygame.Rect(popup_rect.x + 120, popup_rect.y + 330, 200, 50)
        button_color = self.ui.BLUE if is_hovering else self.ui.GREEN
        text_color = self.ui.WHITE
        
        pygame.draw.rect(self.ui.screen, button_color, button_rect)
        
        button_text = "CONFIRM"
        button_text_width = self.ui.font_textbar_black.size(button_text)[0]
        self.draw_text_with_font(button_text, button_rect.centerx - button_text_width // 2, button_rect.centery - 8, text_color, self.ui.font_textbar_black)

    def draw_x_button(self):
        """Draw X button in upper right corner (40x40px) to return to menu"""
        # X button position: top right corner
        x_button_rect = pygame.Rect(1880, 0, 40, 40)
        self.x_button_rect = x_button_rect  # Store for click detection
        
        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = x_button_rect.collidepoint(mouse_pos)
        
        # Draw button background
        bg_color = self.ui.RED if is_hovering else self.ui.DARK_RED
        pygame.draw.rect(self.ui.screen, bg_color, x_button_rect)
        
        # Draw X in the middle
        text_color = self.ui.WHITE
        x_text = self.ui.fonts['regular'][36].render("X", True, text_color)
        x_text_rect = x_text.get_rect(center=x_button_rect.center)
        self.ui.screen.blit(x_text, x_text_rect)
    
    def draw_bot_chat_bubble(self, bot_name, message):
        """
        Draw bot message in a chat bubble based on bot position.
        
        Args:
            bot_name: Name of bot (e.g., "EASY-GO-BOT-1")
            message: Message to display
        """
        # Determine bot number from name
        bot_number = self._get_bot_number(bot_name)
        if bot_number is None:
            return
        
        # Get bubble position and configuration based on bot number
        bubble_config = self._get_bubble_config(bot_number)
        
        # Draw the chat bubble
        self._draw_chat_bubble(bubble_config, bot_name, message)
    
    def _get_bot_number(self, bot_name):
        """Extract bot number from bot name"""
        # Bot names are like "EASY-GO-BOT-1", "NORMAL-GO-BOT-2", etc.
        if "BOT-1" in bot_name:
            return 1
        elif "BOT-2" in bot_name:
            return 2
        elif "BOT-3" in bot_name:
            return 3
        elif "BOT-4" in bot_name:
            return 4
        return None
    
    def _get_bubble_config(self, bot_number):
        """
        Get chat bubble configuration for each bot position.
        Based on BOT-CHATBUBBLES-LAYOUTDESIGN.png:
        - BOT-1: Top-left (label top, bubble below)
        - BOT-2: Top-right (label top, bubble below)
        - BOT-3: Bottom-left (label bottom, bubble above)
        - BOT-4: Bottom-right (label bottom, bubble above)
        """
        configs = {
            1: {  # Top-left
                "label_pos": (550, 20),
                "bubble_rect": pygame.Rect(380, 30, 230, 70),
                "label_above": True
            },
            2: {  # Top-right
                "label_pos": (1090, 20),
                "bubble_rect": pygame.Rect(850, 30, 230, 70),
                "label_above": True
            },
            3: {  # Bottom-left
                "label_pos": (550, 795),
                "bubble_rect": pygame.Rect(380, 720, 230, 70),
                "label_above": False
            },
            4: {  # Bottom-right
                "label_pos": (1090, 795),
                "bubble_rect": pygame.Rect(850, 720, 230, 70),
                "label_above": False
            }
        }
        return configs.get(bot_number, configs[1])
    
    def _draw_chat_bubble(self, config, bot_name, message):
        """Draw the actual chat bubble with text"""
        # Draw yellow label above or below bubble
        label_color = self.ui.YELLOW
        label_text = bot_name
        label_surface = self.ui.fonts['regular'][16].render(label_text, True, label_color)
        label_rect = label_surface.get_rect(center=config["label_pos"])
        self.ui.screen.blit(label_surface, label_rect)
        
        # Draw blue bubble background
        bubble_rect = config["bubble_rect"]
        pygame.draw.rect(self.ui.screen, self.ui.BLUE, bubble_rect)
        
        # Draw bubble border
        pygame.draw.rect(self.ui.screen, self.ui.WHITE, bubble_rect, 2)
        
        # Split message into lines (max 2 lines)
        words = message.split()
        lines = self._split_message_into_lines(words, bubble_rect.width - 20)
        
        # Draw text inside bubble (centered, white text)
        y_offset = bubble_rect.y + 15
        for line in lines[:2]:  # Max 2 lines
            line_surface = self.ui.fonts['regular'][16].render(line, True, self.ui.WHITE)
            line_rect = line_surface.get_rect(centerx=bubble_rect.centerx, y=y_offset)
            self.ui.screen.blit(line_surface, line_rect)
            y_offset += 20
    
    def _split_message_into_lines(self, words, max_width):
        """Split message into lines that fit within max_width"""
        lines = []
        current_line = []
        font = self.ui.fonts['regular'][16]
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_bot_message(self, message, color):
        """DEPRECATED - Old method replaced by draw_bot_chat_bubble"""
        # This method is deprecated but kept for compatibility
        # Calls are now redirected to draw_bot_chat_bubble
        pass

