"""
UI SECTIONS MODULE
Defines all UI section rectangles and color mappings for LIVEDICE game.
This module provides the foundational layout structure used by all UI components.
"""

import pygame
from typing import Dict


class UISections:
    """Manages UI section definitions and color mappings"""
    
    def __init__(self):
        """Initialize section rectangles and colors"""
        self.sections = self._create_sections()
        self.colors = self._create_colors()
        self.section_colors = self._create_section_colors()
    
    def _create_sections(self) -> Dict[str, pygame.Rect]:
        """
        Setup all UI sections with exact dimensions from design specification.
        
        Returns:
            Dictionary mapping section names to pygame.Rect objects
        """
        return {
            # Background Panels
            "LEFTPANEL": pygame.Rect(0, 0, 480, 1080),
            "CENTRALPANEL": pygame.Rect(480, 0, 960, 1080),
            "RIGHTPANEL": pygame.Rect(1440, 0, 480, 1080),
            
            # Left Panel Sections (NEW DESIGN)
            "GAME_INFO": pygame.Rect(20, 0, 160, 180),
            "LEADERBOARD_STANDING": pygame.Rect(180, 0, 280, 180),
            "NOW_PLAYING_PLAYER": pygame.Rect(20, 180, 520, 40),  # Overlaps to X:540
            "RT_STATS": pygame.Rect(20, 220, 160, 340),
            "LEADERBOARD_SCORE": pygame.Rect(180, 220, 320, 340),
            "BANK_BUTTON": pygame.Rect(20, 560, 520, 80),  # Overlaps to X:540
            "STASH": pygame.Rect(20, 640, 480, 440),
            
            # Central Panel
            "SNAPTRAY": pygame.Rect(480, 0, 960, 1080),
            
            # Right Panel Sections
            "DICECUP": pygame.Rect(1460, 20, 440, 400),
            "GAME_DATA_LOG_FRAME": pygame.Rect(1460, 440, 440, 620),
            "GAME_DATA_LOG": pygame.Rect(1460, 440, 440, 620),
            
            # Popup Sections (centered in middle panel)
            "READY_UP_POPUP": pygame.Rect(740, 365, 440, 350),  # Blue themed popup
            "TURN_BUST_POPUP": pygame.Rect(740, 340, 440, 400),  # Red themed popup (slightly taller for 4 lines)
            "BANKED_POINTS_POPUP": pygame.Rect(740, 340, 440, 400),  # Green themed popup (slightly taller for 4 lines)
            "END_GAME_SUMMARY_POPUP": pygame.Rect(660, 290, 600, 500),  # End game rankings popup
            "EXIT_GAME_CONFIRMATION_POPUP": pygame.Rect(740, 290, 440, 340),  # Exit confirmation (20px top bar + 160px text + 80px+80px buttons)
        }
    
    def _create_colors(self) -> Dict[str, tuple]:
        """
        Setup all colors used in the UI following design specification.
        
        Returns:
            Dictionary mapping color names to RGB tuples
        """
        return {
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255),
            "RED": (255, 0, 0),  # #FF0000
            "DARK_RED": (204, 0, 0),  # #CC0000 - Left panel background
            "GREEN": (0, 255, 0),  # #00FF00
            "MEDIUM_GREEN": (0, 187, 0),  # #00BB00
            "DARK_GREEN": (0, 136, 0),  # #008800
            "DARKER_GREEN": (0, 136, 0),  # #008800
            "BLUE": (0, 0, 255),  # #0000FF
            "DARK_BLUE": (0, 0, 170),  # #0000AA
            "DARKER_RED": (170, 0, 0),  # #AA0000 - For red sidebars
            "CYAN": (0, 255, 255),  # #00FFFF
            "YELLOW": (255, 255, 0),
            "MAGENTA": (255, 0, 255),
            "ORANGE": (255, 165, 0),
            "PURPLE": (128, 0, 128),
            "GRAY": (128, 128, 128),
        }
    
    def _create_section_colors(self) -> Dict[str, str]:
        """
        Map section names to their background colors.
        
        Returns:
            Dictionary mapping section names to color names
        """
        return {
            # Main panels
            "LEFTPANEL": "DARK_RED",
            "CENTRALPANEL": "WHITE",
            "RIGHTPANEL": "DARK_RED",
            
            # Right panel sections
            "GAME_DATA_LOG_FRAME": "DARK_BLUE",
            "GAME_DATA_LOG": "BLUE",
        }
    
    def get_section(self, name: str) -> pygame.Rect:
        """
        Get a section rectangle by name.
        
        Args:
            name: Section name (e.g., "LEFTPANEL")
            
        Returns:
            pygame.Rect object for the section
            
        Raises:
            KeyError: If section name doesn't exist
        """
        return self.sections[name]
    
    def get_color(self, name: str) -> tuple:
        """
        Get a color tuple by name.
        
        Args:
            name: Color name (e.g., "RED")
            
        Returns:
            RGB tuple (r, g, b)
            
        Raises:
            KeyError: If color name doesn't exist
        """
        return self.colors[name]
    
    def get_section_color(self, section_name: str) -> tuple:
        """
        Get the background color for a section.
        
        Args:
            section_name: Section name (e.g., "LEFTPANEL")
            
        Returns:
            RGB tuple (r, g, b)
            
        Raises:
            KeyError: If section or its color doesn't exist
        """
        color_name = self.section_colors.get(section_name)
        if color_name:
            return self.colors[color_name]
        return None
