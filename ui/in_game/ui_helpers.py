"""
UI HELPERS MODULE
Utility functions for LIVEDICE game UI.
Provides formatting, calculation, and helper methods used throughout the UI.
"""

import pygame
from typing import List, Tuple, Optional


class UIHelpers:
    """Collection of UI helper functions"""
    
    @staticmethod
    def format_number(number: int) -> str:
        """
        Format numbers replacing 0 with O.
        
        Args:
            number: Number to format
            
        Returns:
            Formatted string with 0 replaced by O
            
        Example:
            >>> format_number(1000)
            '1OOO'
        """
        return str(number).replace('0', 'O')
    
    @staticmethod
    def format_log_entry(entry: str) -> str:
        """
        Format log entry with dice markup.
        
        Converts dice notation like [1g] into <DICE>green_1</DICE> format.
        
        Args:
            entry: Raw log entry text
            
        Returns:
            Formatted entry with dice markup
            
        Example:
            >>> format_log_entry("Rolled [1g] [5]")
            'Rolled <DICE>green_1</DICE> <DICE>_5</DICE>'
        """
        words = entry.split()
        formatted_words = []
        
        for word in words:
            if word.startswith("[") and word.endswith("]"):
                dice_value = word[1:-2]
                if dice_value.isdigit() and 1 <= int(dice_value) <= 6:
                    color = "olgreen" if word.endswith("g]") else ""
                    formatted_words.append(f"<DICE>{color}_{dice_value}</DICE>")
                else:
                    formatted_words.append(word)
            else:
                formatted_words.append(word)
        
        return " ".join(formatted_words)
    
    @staticmethod
    def draw_text_with_font(screen: pygame.Surface, text: str, x: int, y: int, 
                          color: Tuple[int, int, int], font: pygame.font.Font) -> None:
        """
        Helper function to draw text with a specific font.
        
        Args:
            screen: Pygame surface to draw on
            text: Text to render
            x: X coordinate
            y: Y coordinate
            color: RGB color tuple
            font: Pygame font object
        """
        text_surface = font.render(str(text), True, color)
        screen.blit(text_surface, (x, y))
    
    @staticmethod
    def get_entry_height(entry: str, max_width: int, font: pygame.font.Font) -> int:
        """
        Calculate height needed for a log entry.
        
        Takes word wrapping into account based on max_width.
        
        Args:
            entry: Log entry text (possibly with markup)
            max_width: Maximum width in pixels
            font: Font being used
            
        Returns:
            Height in pixels needed to display the entry
        """
        words = entry.split()
        x = 0
        lines = 1
        
        for word in words:
            if word.startswith("<DICE>") and word.endswith("</DICE>"):
                word_width = 36  # Dice image width
            else:
                word_width = font.size(word)[0]
            
            if x + word_width > max_width:
                lines += 1
                x = word_width
            else:
                x += word_width + 5
        
        return lines * (font.get_height() + 2) + 10
    
    @staticmethod
    def get_virtual_rank(game_state, current_player) -> int:
        """
        Calculate virtual rank if player banks now.
        
        Args:
            game_state: GameStateManager instance
            current_player: Current Player instance
            
        Returns:
            Rank (1-based) if player banks current score
        """
        virtual_score = game_state.referee.calculate_total_score()
        
        all_scores = [player.get_total_score() for player in game_state.players]
        all_scores[game_state.players.index(current_player)] = virtual_score
        
        sorted_scores = sorted(all_scores, reverse=True)
        rank = sorted_scores.index(virtual_score) + 1
        
        return rank
    
    @staticmethod
    def get_dice_collection(dice_values: List[int], dice_index: int) -> List[int]:
        """
        Get collection of dice that should be selected together.
        
        Groups triples and double-sixes.
        
        Args:
            dice_values: List of current dice values
            dice_index: Index of clicked die
            
        Returns:
            List of dice indices that should be selected together
        """
        if dice_index >= len(dice_values):
            return []
        
        dice_value = dice_values[dice_index]
        collection = [i for i, v in enumerate(dice_values) if v == dice_value]
        
        # Triple takes priority
        if len(collection) >= 3:
            return collection[:3]
        # Double six
        elif len(collection) == 2 and dice_value == 6:
            return collection
        # Single die
        return [dice_index]
    
    @staticmethod
    def get_clicked_dice(pos: Tuple[int, int], dice_rects: List[pygame.Rect]) -> Optional[int]:
        """
        Get the index of the clicked dice.
        
        Args:
            pos: Mouse position (x, y)
            dice_rects: List of dice rectangles
            
        Returns:
            Index of clicked die, or None if no die clicked
        """
        for i, dice_rect in enumerate(dice_rects):
            if dice_rect.collidepoint(pos):
                return i
        return None
    
    @staticmethod
    def get_hovered_combination(mouse_pos: Tuple[int, int], dice_rects: List[pygame.Rect], 
                               dice_values: List[int]) -> Tuple[List[int], List[int]]:
        """
        Get which dice are currently being hovered over.
        
        Args:
            mouse_pos: Current mouse position
            dice_rects: List of dice rectangles
            dice_values: List of dice values
            
        Returns:
            Tuple of (hovered_dice, hovered_combination)
        """
        hovered_dice = []
        hovered_combination = []

        if dice_rects and dice_values:
            for i, dice_rect in enumerate(dice_rects):
                if dice_rect.collidepoint(mouse_pos):
                    if i < len(dice_values):
                        hovered_dice = UIHelpers.get_dice_collection(dice_values, i)
                        hovered_combination = hovered_dice
                    break

        return hovered_dice, hovered_combination
    
    @staticmethod
    def should_draw_popup(popup_name: str, game_state) -> bool:
        """
        Check if popup should be drawn.
        
        Args:
            popup_name: Name of popup to check
            game_state: GameStateManager instance
            
        Returns:
            True if popup should be drawn
        """
        from games.livedice_f.livedice_f_rules import GameStateEnum
        
        if popup_name == "READY_UP_POPUP":
            return game_state.current_game_state == GameStateEnum.NEXTUP_READYUP
        elif popup_name == "TURN_BUST_POPUP":
            return game_state.current_game_state == GameStateEnum.BUST_TURN_SUMMARY
        elif popup_name == "END_GAME_SUMMARY_POPUP":
            return game_state.check_game_over()
        return False
