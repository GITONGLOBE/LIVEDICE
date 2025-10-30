"""
GAME RUNNER MODULE
Main game loop for LIVEDICE.

MODIFIED: 2025-10-29
CHANGES: Added return_to_menu flag check, removed pygame.quit() call
- Checks ui.return_to_menu flag in game loop
- Exits cleanly when EXIT GAME button clicked
- Does NOT call pygame.quit() so main.py can return to startup menu
WHY: Fix EXIT GAME button to return to menu instead of closing game
TESTING: Click X button, then EXIT GAME - should return to startup menu
"""

import pygame


class GameRunner:
    @staticmethod
    def run_game(ui):
        """
        Main game loop.
        
        Args:
            ui: InGameUI instance
        """
        clock = pygame.time.Clock()
        running = True
        fps = 60

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    ui.handle_event(event)
            
            # Check if user wants to return to menu (EXIT GAME button)
            if hasattr(ui, 'return_to_menu') and ui.return_to_menu:
                print("Returning to startup menu...")
                running = False
                continue

            ui.update()
            ui.draw()
            pygame.display.flip()
            clock.tick(fps)

        # DO NOT call pygame.quit() here - let main.py handle it
        # This allows returning to the startup menu
