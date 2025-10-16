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

        def bot_delay():
            self.ui.draw()
            pygame.display.flip()
            pygame.time.wait(1000)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        go_bot_ai = BotAI(self.ui.game_state)
        
        bot_name = self.ui.game_state.current_player.user.username
        print(f"{bot_name} turn started")
        self.ui.game_state.add_log_entry(f"{bot_name} starts their turn", prefix=bot_name)

        while not self.ui.game_state.referee.is_turn_over():
            print(f"Current game state: {self.ui.game_state.current_game_state}")
            print(f"Is turn over? {self.ui.game_state.referee.is_turn_over()}")
            
            self.ui.display_bot_thinking("What should I do next?")
            bot_delay()
            decision = go_bot_ai.make_decision()
            print(f"{bot_name} decision: {decision}")
            self.ui.game_state.add_log_entry(f"{bot_name} decides to: {decision}", prefix=bot_name)
            bot_delay()

            if decision == "START_TURN":
                self.ui.game_state.current_game_state = GameStateEnum.START_TURN
                self.ui.game_state.turn_started = True
                continue

            if decision == "ROLL":
                if self.ui.game_state.referee.can_roll():
                    self.ui.display_bot_thinking("Time to roll the dice!")
                    bot_delay()
                    dice_values = self.ui.game_state.roll_dice()
                    self.ui.game_board.generate_dice_positions(len(dice_values))
                    self.ui.game_board.update_dice_positions([])
                    self.ui.draw()
                    pygame.display.flip()
                    bot_delay()
                    
                    if self.ui.game_state.referee.is_bust():
                        self.ui.display_bot_thinking("Oh no! I rolled a bust!")
                        bot_delay()
                        self.ui.game_state.bust()
                        break
                else:
                    print(f"{bot_name} can't roll without stashing first")
                    self.ui.game_state.add_log_entry(f"{bot_name} can't roll without stashing first", prefix=bot_name)
                    self.ui.display_bot_decision("Can't roll without stashing. Considering other options.")
                    bot_delay()
                    continue
          
            elif decision == "STASH":
                self.ui.display_bot_thinking("These dice look good. I should stash them.")
                bot_delay()
                stash_indices = go_bot_ai.get_stash_indices()
                if stash_indices:
                    stashed_values = [self.ui.game_state.dice_values[i] for i in stash_indices]
                    formatted_stashed = self.ui.game_state.format_dice(stashed_values)

                    self.ui.game_state.stash_dice(stash_indices)
                    self.ui.game_state.add_log_entry(f"{bot_name} stashed dice: {formatted_stashed}", prefix=bot_name)
                    bot_delay()
                else:
                    print(f"{bot_name} tried to stash, but no stashable dice available")
                    self.ui.game_state.add_log_entry(f"{bot_name} tried to stash, but no stashable dice available", prefix=bot_name)
                    self.ui.display_bot_decision("No stashable dice available. Ending turn.")
                    bot_delay()
                    break
            
            elif decision == "BANK":
                self.ui.display_bot_thinking("I've got a good score. Time to bank!")
                bot_delay()
                if self.ui.game_state.referee.can_bank():
                    points = self.ui.game_state.referee.calculate_turn_score()
                    self.ui.game_state.bank_points()
                    self.ui.update_leaderboard()
                    self.ui.game_state.add_log_entry(f"{bot_name} banked {points} points", prefix=bot_name)
                    bot_delay()
                    break
                else:
                    self.ui.game_state.add_log_entry(f"{bot_name} couldn't bank, continuing turn", prefix=bot_name)
                    continue
            
            elif decision == "START_NEW_STASH":
                self.ui.display_bot_thinking("My stash is full. Let's start a new one!")
                bot_delay()
                self.ui.game_state.start_new_stash()
                self.ui.game_state.add_log_entry(f"{bot_name} started a new stash", prefix=bot_name)
                bot_delay()
            
            elif decision == "END_TURN":
                self.ui.display_bot_thinking("I can't do anything else. Ending my turn.")
                bot_delay()
                break

            self.ui.draw()
            pygame.display.flip()

        print(f"{bot_name} turn ended")
        self.ui.game_state.add_log_entry(f"{bot_name} ended their turn", prefix=bot_name)

        self.ui.display_bot_decision(f"{bot_name} turn ended. Click to continue.")
        self.ui.draw()
        pygame.display.flip()
        self.ui.wait_for_click()

        self.ui.game_state.next_player()
        self.ui.bot_turn_in_progress = False

    def end_game(self):
        """Handle end of game"""
        winner = self.ui.game_state.get_winner()
        if winner:
            self.ui.game_state.add_log_entry(f"GAME OVER! {winner.user.username} wins with {winner.get_total_score()} points!")
        self.ui.game_state.set_active_task("GAME OVER")
        
    def display_bot_thinking(self, thought):
        """Display bot thinking message"""
        bot_name = self.ui.game_state.current_player.user.username
        self.ui.bot_thinking_message = f"{bot_name} is thinking: {thought}"
        self.ui.game_state.add_log_entry(f"{bot_name} is thinking: {thought}", prefix=bot_name)

    def display_bot_decision(self, decision):
        """Display bot decision message"""
        bot_name = self.ui.game_state.current_player.user.username
        self.ui.bot_decision_message = f"{bot_name} decision: {decision}"
        self.ui.game_state.add_log_entry(decision, prefix=bot_name)

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
        
        self.ui.game_state.add_log_entry(scoring_info, prefix="@G-REF.")

    def change_snaptray_color(self, color):
        """Change snaptray overlay color"""
        print(f"Changing snaptray color to: {color}")
        self.ui.snaptray_color = color
        self.ui.snaptray_overlay = self.ui.snaptray_images[color]
        self.ui.force_redraw()

    def force_redraw(self):
        """Force screen redraw"""
        self.ui.draw()
        pygame.display.flip()


