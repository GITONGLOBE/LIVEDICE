"""
UI BOT MODULE
Bot AI interaction for LIVEDICE game UI.
Handles bot turn execution, decision display, and game flow for AI players.
"""

import pygame
import sys
import time
from core.game_engine.go_bot_ai import BotAI
from games.livedice_f.livedice_f_rules import GameStateEnum


class UIBot:
    """Handles bot AI interactions and display"""
    
    def __init__(self, ui_instance):
        """
        Initialize bot module with reference to main UI instance.
        
        Args:
            ui_instance: Reference to InGameUI instance
        """
        self.ui = ui_instance
        self.bot_turn_in_progress = False
    
    def bot_turn(self):
        """Handle AI bot turn"""
        pygame.event.pump()

        def bot_delay(duration_ms=1000):
            """Delay with screen updates and event handling"""
            self.ui.draw()
            pygame.display.flip()
            pygame.time.wait(duration_ms)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        go_bot_ai = BotAI(self.ui.game_state)
        
        bot_name = self.ui.game_state.current_player.user.username
        print(f"{bot_name} TURN STARTED")
        self.ui.game_state.add_log_entry(f"{bot_name} STARTS THEIR TURN", prefix=bot_name)

        # Safety counter to prevent infinite loops
        max_decisions = 50
        decision_count = 0

        while not self.ui.game_state.referee.is_turn_over() and decision_count < max_decisions:
            decision_count += 1
            print(f"Current game state: {self.ui.game_state.current_game_state}")
            print(f"Is turn over? {self.ui.game_state.referee.is_turn_over()}")
            print(f"Decision #{decision_count}")
            
            decision, thinking_msg = go_bot_ai.make_decision()
            
            # Display bot's thinking process
            if thinking_msg:
                self.ui.display_bot_thinking(thinking_msg)
                bot_delay()
            
            print(f"{bot_name} decision: {decision}")
            self.ui.game_state.add_log_entry(f"{bot_name} DECIDES TO: {decision.upper()}", prefix=bot_name)
            bot_delay()

            if decision == "START_TURN":
                self.ui.game_state.current_game_state = GameStateEnum.START_TURN
                self.ui.game_state.turn_started = True
                continue

            if decision == "ROLL":
                if self.ui.game_state.referee.can_roll():
                    self.ui.display_bot_thinking("TIME TO ROLL THE DICE!")
                    bot_delay()
                    
                    # Roll the dice
                    dice_values = self.ui.game_state.roll_dice()
                    
                    # Generate new random positions
                    self.ui.game_board.generate_dice_positions(len(dice_values))
                    
                    # Reset physics for animation
                    self.ui.game_board.update_dice_positions([])
                    
                    # Animate dice rolling for 2 seconds
                    animation_start = time.time()
                    animation_duration = 2.0
                    
                    while time.time() - animation_start < animation_duration:
                        dt = 1/60.0
                        self.ui.game_board.update(dt)
                        self.ui.draw()
                        pygame.display.flip()
                        pygame.time.wait(16)
                        
                        # Handle events during animation
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                    
                    bot_delay()
                    
                    if self.ui.game_state.referee.is_bust():
                        self.ui.display_bot_thinking("OH NO! I ROLLED A BUST!")
                        bot_delay()
                        self.ui.game_state.referee.bust()
                        break
                else:
                    print(f"{bot_name} CAN'T ROLL WITHOUT STASHING FIRST")
                    self.ui.game_state.add_log_entry(f"{bot_name} CAN'T ROLL WITHOUT STASHING FIRST", prefix=bot_name)
                    self.ui.display_bot_decision("CAN'T ROLL WITHOUT STASHING. CONSIDERING OTHER OPTIONS.")
                    bot_delay()
                    continue
          
            elif decision == "STASH":
                # Get smart stash selection
                stash_indices = go_bot_ai.get_stash_indices()
                if stash_indices:
                    stashed_values = [self.ui.game_state.dice_values[i] for i in stash_indices]
                    formatted_stashed = self.ui.game_state.format_dice(stashed_values)

                    self.ui.game_state.stash_dice(stash_indices)
                    self.ui.game_state.add_log_entry(f"{bot_name} STASHED DICE: {formatted_stashed}", prefix=bot_name)
                    bot_delay()
                else:
                    print(f"{bot_name} TRIED TO STASH, BUT NO STASHABLE DICE AVAILABLE")
                    self.ui.game_state.add_log_entry(f"{bot_name} TRIED TO STASH, BUT NO STASHABLE DICE AVAILABLE", prefix=bot_name)
                    self.ui.display_bot_decision("NO STASHABLE DICE AVAILABLE. ENDING TURN.")
                    bot_delay()
                    break
            
            elif decision == "BANK":
                if self.ui.game_state.referee.can_bank():
                    points = self.ui.game_state.referee.calculate_turn_score()
                    self.ui.game_state.referee.bank_points()
                    # Removed: bank_points() already records turn
                    self.ui.game_state.add_log_entry(f"{bot_name} BANKED {points} POINTS", prefix=bot_name)
                    bot_delay()
                    break
                else:
                    self.ui.game_state.add_log_entry(f"{bot_name} COULDN'T BANK, CONTINUING TURN", prefix=bot_name)
                    continue
            
            elif decision == "START_NEW_STASH":
                self.ui.display_bot_thinking("MY STASH IS FULL. LET'S START A NEW ONE!")
                bot_delay()
                self.ui.game_state.start_new_stash()
                self.ui.game_state.add_log_entry(f"{bot_name} STARTED A NEW STASH", prefix=bot_name)
                bot_delay()
            
            elif decision == "END_TURN":
                self.ui.display_bot_thinking("I CAN'T DO ANYTHING ELSE. ENDING MY TURN.")
                bot_delay()
                break
            
            else:
                print(f"UNKNOWN DECISION: {decision}")
                self.ui.game_state.add_log_entry(f"{bot_name} MADE AN UNKNOWN DECISION: {decision.upper()}", prefix=bot_name)
                bot_delay()
                break

            self.ui.draw()
            pygame.display.flip()

        if decision_count >= max_decisions:
            print(f"WARNING: Bot turn ended due to max decision limit!")
            self.ui.game_state.add_log_entry(f"{bot_name} TURN ENDED (MAX DECISIONS REACHED)", prefix="SYSTEM")

        print(f"{bot_name} TURN ENDED")
        self.ui.game_state.add_log_entry(f"{bot_name} ENDED THEIR TURN", prefix=bot_name)

        # Set flag to False BEFORE blocking operations
        self.bot_turn_in_progress = False

        # Show end message and wait for click
        self.ui.display_bot_decision(f"{bot_name} TURN ENDED. CLICK TO CONTINUE.")
        self.ui.draw()
        pygame.display.flip()
        self.ui.wait_for_click()

        # Call referee.end_turn() which handles next_player() and game state properly
        self.ui.game_state.referee.end_turn()

    def end_game(self):
        """Handle end of game"""
        winner = self.ui.game_state.get_winner()
        if winner:
            self.ui.game_state.add_log_entry(f"GAME OVER! {winner.user.username} WINS WITH {winner.get_total_score()} POINTS!")
        self.ui.game_state.set_active_task("GAME OVER")
    
    def change_snaptray_color(self, color):
        """Change the color of the snaptray overlay"""
        overlay = pygame.Surface(self.ui.snaptray_overlay.get_size(), pygame.SRCALPHA)
        overlay.fill((*color, 128))
        self.ui.snaptray_overlay = overlay
    
    def force_redraw(self):
        """Force a screen redraw"""
        self.ui.draw()
        pygame.display.flip()
        
    def display_bot_thinking(self, thought):
        """Display bot thinking message"""
        bot_name = self.ui.game_state.current_player.user.username
        self.ui.bot_thinking_message = f"{bot_name} IS THINKING: {thought.upper()}"
        self.ui.game_state.add_log_entry(f"{bot_name} IS THINKING: {thought.upper()}", prefix=bot_name)

    def display_bot_decision(self, decision):
        """Display bot decision message"""
        bot_name = self.ui.game_state.current_player.user.username
        self.ui.bot_decision_message = f"{bot_name} DECISION: {decision.upper()}"
        self.ui.game_state.add_log_entry(decision.upper(), prefix=bot_name)

    def wait_for_click(self):
        """Wait for user to click"""
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.delay(100)

    def show_scoring_info(self):
        """Show scoring information in log"""
        current_player = self.ui.game_state.current_player
        self.ui.game_state.add_log_entry(f"{current_player.user.username} REQUESTED A REMINDER", prefix="@G-REF.")
        
        rules = self.ui.game_state.referee.rules
        scoring_info = rules.get_scoring_combinations()
        
        for combo_name, combo_info in scoring_info.items():
            self.ui.game_state.add_log_entry(f"{combo_name}: {combo_info['points']} POINTS", prefix="@G-REF.")
