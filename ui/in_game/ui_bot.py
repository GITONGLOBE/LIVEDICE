"""
UI BOT MODULE
Bot AI interaction for LIVEDICE game UI.
Handles bot turn execution, decision display, and game flow for AI players.

UPDATED: Full integration with message_manager personality system
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
        """Handle AI bot turn - uses message_manager for personality-driven messages"""
        # CRITICAL: Only proceed if current player is actually a bot
        if not self.ui.game_state.current_player.is_bot():
            return
        
        # CRITICAL: Double-check player is not human
        if self.ui.game_state.current_player.user.username.startswith("@VIDEO-GAMER"):
            return
        
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
        turn_number = self.ui.game_state.current_player.turn_count + 1
        
        print(f"{bot_name} TURN STARTED")
        
        # G-REF announces turn start
        self.ui.game_state.message_manager.add_gref_turn_start(bot_name, turn_number)
        
        # Bot announces they're starting (personality-driven)
        context = {"turn": turn_number}
        self.ui.game_state.message_manager.add_bot_turn_start_message(bot_name, context)

        # Safety counter to prevent infinite loops
        max_decisions = 50
        decision_count = 0

        while not self.ui.game_state.referee.is_turn_over() and decision_count < max_decisions:
            decision_count += 1
            print(f"Current game state: {self.ui.game_state.current_game_state}")
            print(f"Is turn over? {self.ui.game_state.referee.is_turn_over()}")
            print(f"Decision #{decision_count}")
            
            decision, thinking_msg = go_bot_ai.make_decision()
            
            # Create context for this decision
            context = {
                "turn": turn_number,
                "score": self.ui.game_state.referee.calculate_turn_score(),
                "remaining_dice": len(self.ui.game_state.dice_values),
                "decision_count": decision_count
            }
            
            # Display bot's thinking process (uses personality system)
            if thinking_msg:
                self.ui.display_bot_thinking(thinking_msg)
                bot_delay()
            
            print(f"{bot_name} decision: {decision}")
            
            # Bot explains their decision (personality-driven)
            self.ui.game_state.message_manager.add_bot_strategy_explanation(
                bot_name, 
                decision, 
                f"DECIDING TO {decision.upper()}", 
                context
            )
            bot_delay()

            if decision == "START_TURN":
                self.ui.game_state.current_game_state = GameStateEnum.START_TURN
                self.ui.game_state.turn_started = True
                continue

            if decision == "ROLL":
                if self.ui.game_state.referee.can_roll():
                    # Bot announces roll (personality-driven)
                    self.ui.game_state.message_manager.add_bot_reaction(bot_name, "rolling", context)
                    bot_delay()
                    
                    # Roll the dice (G-REF message now generated inside roll_dice)
                    dice_values = self.ui.game_state.roll_dice()
                    
                    # Get stashable dice indices for proper color coding
                    stashable_indices = self.ui.game_state.current_stashable_dice
                    
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
                    
                    # Check for bust
                    if self.ui.game_state.referee.is_bust():
                        lost_points = self.ui.game_state.referee.calculate_turn_score()
                        
                        # Bot reacts to bust (personality-driven)
                        bust_context = {
                            "turn": turn_number,
                            "lost_points": lost_points,
                            "dice": dice_values
                        }
                        self.ui.game_state.message_manager.add_bot_reaction(bot_name, "bust", bust_context)
                        bot_delay()
                        
                        # REMOVED: Duplicate G-REF bust message
                        # G-REF message is now generated inside game_referee.bust() for ALL players
                        
                        self.ui.game_state.referee.bust()
                        
                        # BOT AUTO-CLICKS BUST POPUP (FIX #6)
                        bot_delay(800)  # Brief pause to show popup
                        # Auto-advance past bust summary (no need to wait for click)
                        break
                    else:
                        # Bot reacts to successful roll (personality-driven)
                        # Simple points estimation (1s and 5s are worth points)
                        points_estimate = dice_values.count(1) * 100 + dice_values.count(5) * 50
                        
                        roll_context = {
                            "turn": turn_number,
                            "points": points_estimate,
                            "dice": dice_values
                        }
                        
                        # Determine if it's a good or bad roll
                        if points_estimate >= 200:
                            self.ui.game_state.message_manager.add_bot_reaction(bot_name, "good_roll", roll_context)
                        else:
                            self.ui.game_state.message_manager.add_bot_reaction(bot_name, "bad_roll", roll_context)
                else:
                    print(f"{bot_name} CAN'T ROLL WITHOUT STASHING FIRST")
                    
                    # G-REF announces the issue
                    self.ui.game_state.message_manager.add_gref_official_statement(
                        f"{bot_name} MUST STASH DICE BEFORE ROLLING AGAIN"
                    )
                    
                    # Bot reacts (personality-driven)
                    self.ui.game_state.message_manager.add_bot_thinking(
                        bot_name, 
                        "CAN'T ROLL WITHOUT STASHING FIRST", 
                        context
                    )
                    bot_delay()
                    continue
          
            elif decision == "STASH":
                # Get smart stash selection
                stash_indices = go_bot_ai.get_stash_indices()
                if stash_indices:
                    stashed_values = [self.ui.game_state.dice_values[i] for i in stash_indices]
                    
                    # Perform the stash (G-REF message now generated inside stash_dice with correct points)
                    self.ui.game_state.stash_dice(stash_indices)
                    
                    # Bot explains stash decision (personality-driven)
                    # Calculate correct points for bot's reaction
                    stash_points = sum([
                        score for name, score in 
                        self.ui.game_state.referee.get_scoring_combinations(stashed_values)
                    ])
                    
                    stash_context = {
                        "turn": turn_number,
                        "points": stash_points,
                        "dice_count": len(stashed_values),
                        "dice": stashed_values
                    }
                    self.ui.game_state.message_manager.add_bot_strategy_explanation(
                        bot_name,
                        "STASH",
                        f"STASHING {len(stashed_values)} DICE",
                        stash_context
                    )
                    bot_delay()
                else:
                    print(f"{bot_name} TRIED TO STASH, BUT NO STASHABLE DICE AVAILABLE")
                    
                    # G-REF announces the issue
                    self.ui.game_state.message_manager.add_gref_official_statement(
                        f"{bot_name} HAS NO STASHABLE DICE AVAILABLE"
                    )
                    
                    # Bot reacts (personality-driven)
                    self.ui.game_state.message_manager.add_bot_frustration(bot_name, context)
                    bot_delay()
                    break
            
            elif decision == "BANK":
                if self.ui.game_state.referee.can_bank():
                    points = self.ui.game_state.referee.calculate_turn_score()
                    
                    # Bot explains bank decision (personality-driven)
                    bank_context = {
                        "turn": turn_number,
                        "points": points,
                        "action": "BANK"
                    }
                    self.ui.game_state.message_manager.add_bot_reaction(bot_name, "banking", bank_context)
                    bot_delay()
                    
                    # Perform the bank (G-REF message now generated inside bank_points)
                    self.ui.game_state.referee.bank_points()
                    
                    # BOT AUTO-CLICKS BANK POPUP (FIX #6)
                    bot_delay(800)  # Brief pause to show popup
                    # Auto-advance past bank summary (no need to wait for click)
                    break
                else:
                    # G-REF announces can't bank
                    self.ui.game_state.message_manager.add_gref_official_statement(
                        f"{bot_name} CANNOT BANK YET"
                    )
                    
                    # Bot reacts (personality-driven)
                    self.ui.game_state.message_manager.add_bot_thinking(
                        bot_name,
                        "CAN'T BANK YET, CONTINUING TURN",
                        context
                    )
                    continue
            
            elif decision == "START_NEW_STASH":
                # Bot announces stashstash (personality-driven)
                self.ui.game_state.message_manager.add_bot_thinking(
                    bot_name,
                    "MY STASH IS FULL - TIME TO START A NEW ONE!",
                    context
                )
                bot_delay()
                
                self.ui.game_state.start_new_stash()
                
                # G-REF announces stashstash
                self.ui.game_state.message_manager.add_gref_official_statement(
                    f"{bot_name} STARTED A NEW STASH (STASHSTASH)"
                )
                bot_delay()
            
            elif decision == "END_TURN":
                # Bot announces end (personality-driven)
                self.ui.game_state.message_manager.add_bot_thinking(
                    bot_name,
                    "NO MORE MOVES AVAILABLE - ENDING MY TURN",
                    context
                )
                bot_delay()
                break
            
            else:
                print(f"UNKNOWN DECISION: {decision}")
                
                # G-REF announces unknown decision
                self.ui.game_state.message_manager.add_gref_official_statement(
                    f"{bot_name} MADE AN UNKNOWN DECISION: {decision.upper()}"
                )
                
                # Bot reacts (personality-driven)
                self.ui.game_state.message_manager.add_bot_thinking(
                    bot_name,
                    f"UNKNOWN DECISION: {decision.upper()}",
                    context
                )
                bot_delay()
                break

            self.ui.draw()
            pygame.display.flip()

        if decision_count >= max_decisions:
            print(f"WARNING: Bot turn ended due to max decision limit!")
            
            # G-REF announces max decisions reached
            self.ui.game_state.message_manager.add_gref_official_statement(
                f"{bot_name} TURN ENDED (MAX DECISIONS REACHED)"
            )

        print(f"{bot_name} TURN ENDED")
        
        # REMOVED: Duplicate G-REF turn_end message
        # G-REF message is now generated inside game_referee.end_turn() for ALL players

        # Set flag to False BEFORE blocking operations
        self.bot_turn_in_progress = False

        # Bot turn complete - auto-advance (FIX #6)
        bot_delay(500)  # Brief pause before next player

        # Call referee.end_turn() which handles next_player() and game state properly
        self.ui.game_state.referee.end_turn()

    def end_game(self):
        """Handle end of game"""
        winner = self.ui.game_state.get_winner()
        if winner:
            # G-REF announces game end
            self.ui.game_state.message_manager.add_gref_game_end(
                winner.user.username, 
                winner.get_total_score()
            )
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
        """Display bot thinking message using personality system"""
        bot_name = self.ui.game_state.current_player.user.username
        context = {
            "turn": self.ui.game_state.current_player.turn_count + 1,
            "score": self.ui.game_state.referee.calculate_turn_score()
        }
        self.ui.game_state.message_manager.add_bot_thinking(bot_name, thought.upper(), context)

    def display_bot_decision(self, decision):
        """Display bot decision message using personality system"""
        bot_name = self.ui.game_state.current_player.user.username
        context = {
            "turn": self.ui.game_state.current_player.turn_count + 1,
            "score": self.ui.game_state.referee.calculate_turn_score()
        }
        self.ui.game_state.message_manager.add_bot_strategy_explanation(bot_name, "DECISION", decision.upper(), context)

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
        
        # G-REF announces scoring reminder request
        self.ui.game_state.message_manager.add_gref_official_statement(
            f"{current_player.user.username} REQUESTED SCORING INFORMATION"
        )
        
        rules = self.ui.game_state.referee.rules
        scoring_info = rules.get_scoring_combinations()
        
        for combo_name, combo_info in scoring_info.items():
            # G-REF announces each scoring rule
            self.ui.game_state.message_manager.add_gref_official_statement(
                f"{combo_name}: {combo_info['points']} POINTS"
            )
