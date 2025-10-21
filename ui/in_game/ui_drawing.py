"""
UI DRAWING MODULE
All drawing methods for LIVEDICE game UI.
Handles rendering of all visual elements including panels, scores, dice, and game state.
"""

import pygame
import sys
import os
import time
from typing import List, Tuple, Optional
from ui.in_game.ui_helpers import UIHelpers
from games.livedice_f.livedice_f_rules import GameStateEnum


class UIDrawing:
    """Handles all UI drawing operations"""
    
    def __init__(self, ui_instance):
        """
        Initialize drawing module with reference to main UI instance.
        
        Args:
            ui_instance: Reference to InGameUI instance for accessing game state and resources
        """
        self.ui = ui_instance
    
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

    def draw_scrollable_log(self, rect: pygame.Rect):
        """Draw scrollable game log"""
        MAX_LOG_ENTRIES = 100
        log_surface = pygame.Surface((rect.width, rect.height))
        log_surface.fill(self.ui.BLUE)

        formatted_log = [self.ui.format_log_entry(entry) for entry in self.ui.game_state.game_log[-MAX_LOG_ENTRIES:]]

        y = 0
        entry_heights = []
        for entry in formatted_log:
            entry_height = self.get_entry_height(entry, rect.width - 20)
            entry_heights.append(entry_height)
            y += entry_height

        total_height = sum(entry_heights)
        visible_height = rect.height
        max_scroll = max(0, total_height - visible_height)

        self.ui.log_scroll_y = min(max_scroll, self.ui.log_scroll_y)

        y = -self.ui.log_scroll_y
        for entry, height in zip(formatted_log, entry_heights):
            if y + height > 0 and y < visible_height:
                self.render_log_line(log_surface, entry, 10, y)
            y += height

        if total_height > visible_height:
            scrollbar_height = (visible_height / total_height) * visible_height
            scrollbar_pos = (self.ui.log_scroll_y / max_scroll) * (visible_height - scrollbar_height)
            pygame.draw.rect(log_surface, self.ui.WHITE, (rect.width - 10, scrollbar_pos, 10, scrollbar_height))

        self.ui.screen.blit(log_surface, rect)

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

