from typing import List, Tuple, Optional
from games.livedice_f.livedice_f_rules import LiveDiceFRules, GameStateEnum

class GameReferee:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

    def update_game_state(self):
        """
        CRITICAL: Check game state and transitions
        Priority order:
        1. Check for FINAL_TURNS trigger (someone reached endgoal)
        2. Check for END_GAME_SUMMARY (all final turns complete)
        3. Normal game state transitions
        """
        # CRITICAL: Don't check final turns if already triggered
        if not self.game_state_manager.final_turns_triggered:
            if self.check_final_turns_trigger():
                # Don't proceed to other checks - final turns just triggered
                return
        
        # CRITICAL: Check if final turns are complete
        if self.game_state_manager.final_turns_triggered:
            if self.check_final_turns_complete():
                self.set_game_state(GameStateEnum.END_GAME_SUMMARY)
                return
        
        # Normal game state logic
        state_conditions = [
            (lambda: self.bust_state, GameStateEnum.BUST_TURN_SUMMARY),
            (lambda: self.turn_banked, GameStateEnum.BANKED_TURN_SUMMARY),
            (self.referee.is_full_stash, GameStateEnum.STASHCHOICE_STASHED_FULL),
            (lambda: len(self.dice_values) == 0 and self.referee.has_stashed_dice(), GameStateEnum.STASHCHOICE_STASHED_ALL),
            (lambda: self.referee.get_stashable_dice(self.dice_values) and self.referee.has_stashed_dice(), GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED),
            (lambda: self.referee.get_stashable_dice(self.dice_values), GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS),
            (lambda: True, GameStateEnum.STASHCHOICE_STASHED_PARTIAL)
        ]

        for condition, state in state_conditions:
            if condition():
                self.referee.set_game_state(state)
                break

        self.real_time_counters.update_counters(self)

    def calculate_total_score(self) -> int:
        current_state = self.game_state_manager.current_game_state
        if current_state in [GameStateEnum.BANKED_TURN_SUMMARY, GameStateEnum.BUST_TURN_SUMMARY]:
            return self.game_state_manager.current_player.get_total_score()
        else:
            return (self.game_state_manager.current_player.get_total_score() +
                    self.calculate_turn_score())

    def calculate_virtual_score(self) -> int:
        return self.calculate_turn_score()
    
    def calculate_table_score(self) -> int:
        return LiveDiceFRules.calculate_score(self.game_state_manager.dice_values, False, self.game_state_manager.ruleset)

    def calculate_stash_score(self) -> int:
        return self.game_state_manager.current_player.get_stash_score()

    def calculate_stash_stash_score(self) -> int:
        return self.game_state_manager.current_player.stash_stash

    def calculate_turn_score(self) -> int:
        return (self.calculate_table_score() +
                self.calculate_stash_score() +
                self.calculate_stash_stash_score())

    def get_total_score(self, player) -> int:
        return sum(turn["SCORE"] for turn in player.turn_scores.values())

    def is_bust(self) -> bool:
        return LiveDiceFRules.is_bust(self.game_state_manager.dice_values, self.game_state_manager.ruleset)

    def can_stash(self) -> bool:
        return LiveDiceFRules.can_stash(self.game_state_manager.selected_dice)

    def is_full_stash(self) -> bool:
        return LiveDiceFRules.is_full_stash(self.game_state_manager.current_player.stashed_dice)

    def get_stashable_dice(self, dice_values: List[int]) -> List[int]:
        return LiveDiceFRules.get_stashable_dice(dice_values, self.game_state_manager.ruleset)

    def get_scoring_combinations(self, dice_values: List[int]) -> List[Tuple[str, int]]:
        return LiveDiceFRules.get_scoring_combinations(dice_values, self.game_state_manager.ruleset)

    def get_stash_number(self) -> str:
        return LiveDiceFRules.get_stash_number(self.game_state_manager.current_player.stash_level)

    def get_next_stash_number(self) -> str:
        return LiveDiceFRules.get_stash_number(self.game_state_manager.current_player.stash_level + 1)

    def get_stash_stash_info(self) -> Tuple[int, int]:
        stash_stash_points = self.game_state_manager.current_player.stash_stash
        full_stashes_moved = self.game_state_manager.current_player.full_stashes_moved_this_turn
        return stash_stash_points, full_stashes_moved

    def is_scoring_dice(self, dice: List[int]) -> bool:
        return LiveDiceFRules.is_scoring_dice(dice)

    def can_roll(self) -> bool:
        current_state = self.game_state_manager.current_game_state
        has_stashed_this_turn = self.game_state_manager.current_player.stashed_dice_this_roll
        
        if current_state in [GameStateEnum.BUST_TURN_SUMMARY, 
                             GameStateEnum.BANKED_TURN_SUMMARY, 
                             GameStateEnum.END_GAME_SUMMARY]:
            return False
        
        if current_state in [GameStateEnum.START_TURN, GameStateEnum.NEW_STASH]:
            return True
        
        if self.game_state_manager.can_roll_once:
            return True
        
        return (LiveDiceFRules.can_roll_again(has_stashed_this_turn) and
                (LiveDiceFRules.can_roll_six_dice(
                    self.game_state_manager.turn_started,
                    self.game_state_manager.current_player.stashed_dice,
                    self.game_state_manager.current_player.roll_count
                ) or
                (has_stashed_this_turn and len(self.game_state_manager.dice_values) > 0) or
                current_state == GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED_CURRENTROLL or
                current_state == GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL) and
                current_state != GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH)

    def can_roll_six_dice(self, turn_started: bool, stashed_dice: List[int], roll_count: int) -> bool:
        return LiveDiceFRules.can_roll_six_dice(turn_started, stashed_dice, roll_count)

    def get_roll_button_text(self) -> str:
        remaining_dice = LiveDiceFRules.MAX_DICE - len(self.game_state_manager.current_player.stashed_dice)
        stash_level = self.game_state_manager.current_player.stash_level
        if remaining_dice == LiveDiceFRules.MAX_DICE and self.game_state_manager.current_player.roll_count == 0:
            return f"ROLL ALL 6 DICE\nSTART {LiveDiceFRules.get_stash_number(stash_level)} STASH"
        elif remaining_dice > 0:
            return f"ROLL {remaining_dice} DICE AGAIN"
        else:
            return "CANNOT ROLL"  # This button should be disabled when there are no dice to roll

    def can_bank(self) -> bool:
        current_state = self.game_state_manager.current_game_state
        has_stashed_this_turn = self.game_state_manager.current_player.stashed_dice_this_roll
        virtual_score = self.calculate_virtual_score()
        
        # CRITICAL FIX: BANK not allowed when player has unstashed green dice
        # Added ROLLRESULT_POSITIVE_STASHOPTIONS to exclusion list
        # Player must make stashing decision (stash or skip) before banking
        return (LiveDiceFRules.can_bank(has_stashed_this_turn, virtual_score) and
                current_state not in [GameStateEnum.BUST_TURN_SUMMARY, 
                                      GameStateEnum.BANKED_TURN_SUMMARY, 
                                      GameStateEnum.END_GAME_SUMMARY,
                                      GameStateEnum.START_TURN,
                                      GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS,
                                      GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH])

    def get_stash_button_text(self) -> str:
        stash_points = LiveDiceFRules.calculate_score([self.game_state_manager.dice_values[i] for i in self.game_state_manager.selected_dice])
        total_stash_points = self.game_state_manager.real_time_counters.stashplusselection_vscore
        stash_stash_points = self.game_state_manager.real_time_counters.stashstash_vscore
        full_stashes_moved = self.game_state_manager.current_player.full_stashes_moved
        return f"STASH {self.game_state_manager.format_number(stash_points)} POINTS\nTOTAL STASH: {self.game_state_manager.format_number(total_stash_points)} POINTS\nSTASH STASH: {self.game_state_manager.format_number(stash_stash_points)} POINTS ({self.game_state_manager.format_number(full_stashes_moved)} STASHES)"

    def get_bank_button_text(self) -> str:
        virtual_score = self.calculate_virtual_score()
        return f"BANK {self.game_state_manager.format_number(virtual_score)} POINTS\n" \
            f"TABLE: {self.game_state_manager.format_number(self.game_state_manager.real_time_counters.table_vscore)} / " \
            f"STASH: {self.game_state_manager.format_number(self.game_state_manager.real_time_counters.stash_vscore)} / " \
            f"STASH STASH: {self.game_state_manager.format_number(self.game_state_manager.real_time_counters.stashstash_vscore)}"

    def get_full_stash_button_text(self) -> str:
        stash_points = self.game_state_manager.real_time_counters.stash_vscore
        return f"FULL STASH\nMOVE {self.game_state_manager.format_number(stash_points)} POINTS TO STASH STASH\nSTART {self.get_next_stash_number()} STASH"

    def can_select_dice(self, dice_index: Optional[int] = None) -> bool:
        current_state = self.game_state_manager.current_game_state
        if current_state in [GameStateEnum.BUST_TURN_SUMMARY, GameStateEnum.BANKED_TURN_SUMMARY, GameStateEnum.END_GAME_SUMMARY]:
            return False
        if dice_index is not None:
            return dice_index in self.get_stashable_dice(self.game_state_manager.dice_values)
        return True

    def is_turn_over(self) -> bool:
        return self.game_state_manager.bust_state or self.game_state_manager.turn_banked
    
    def should_start_new_turn(self) -> bool:
        return LiveDiceFRules.should_start_new_turn(
            self.game_state_manager.dice_values,
            self.game_state_manager.current_player.stashed_dice,
            self.game_state_manager.turn_started
        )


    def check_final_turns_trigger(self) -> bool:
        """Check if any player reached endgoal and trigger FINAL_TURNS state"""
        # Only trigger once
        if hasattr(self.game_state_manager, 'final_turns_triggered'):
            return False
        
        # Check if any player reached endgoal
        for player in self.game_state_manager.players:
            if player.get_total_score() >= self.game_state_manager.endgoal:
                # Mark final turns triggered
                self.game_state_manager.final_turns_triggered = True
                self.game_state_manager.final_turns_player = player
                self.game_state_manager.final_turns_turn_number = player.turn_count
                self.game_state_manager.final_turns_score = player.get_total_score()
                
                # Add G-REF message
                self.game_state_manager.message_manager.add_gref_official_statement(
                    f"FINAL TURNS! {player.user.username} HAS REACHED THE ENDGOAL!"
                )
                
                return True
        
        return False
    def is_game_over(self) -> bool:
        player_scores = [player.get_total_score() for player in self.game_state_manager.players]
        # CRITICAL FIX: Game ends when ANY player reaches goal AND all players had equal turns
        any_won = any(score >= self.game_state_manager.endgoal for score in player_scores)
        if not any_won:
            return False
        
        # Check if all players have had equal number of turns
        turn_counts = [player.turn_count for player in self.game_state_manager.players]
        all_equal_turns = len(set(turn_counts)) == 1
        return all_equal_turns

    def calculate_score(self, dice_values: List[int], stashed_together: bool = False) -> int:
        return LiveDiceFRules.calculate_score(dice_values, stashed_together, self.game_state_manager.ruleset)

    def describe_stash(self, stashed: List[int]) -> str:
        return LiveDiceFRules.describe_stash(stashed)
    
    def get_dice_for_combination(self, dice_values: List[int], combination_name: str) -> List[int]:
        return LiveDiceFRules.get_dice_for_combination(dice_values, combination_name)

    def set_game_state(self, new_state: GameStateEnum):
        self.game_state_manager.current_game_state = new_state

    def has_stashed_dice(self) -> bool:
        return len(self.game_state_manager.current_player.stashed_dice) > 0
    
    def validate_action(self, action: str) -> bool:
        valid_actions = {
            "ROLL": self.can_roll,
            "STASH": self.can_stash,
            "BANK": self.can_bank,
            "START_NEW_STASH": self.is_full_stash,
            "END_TURN": lambda: True  # Always allow ending turn
        }
        return valid_actions.get(action, lambda: False)()

    def perform_action(self, action: str):
        if not self.validate_action(action):
            raise ValueError(f"Invalid action: {action} in game state: {self.game_state_manager.current_game_state}")

        # CRITICAL FIX: Wrap roll_dice to include animation
        if action == "ROLL":
            # Roll the dice
            self.game_state_manager.roll_dice()
            # CRITICAL: Trigger animation after rolling
            if hasattr(self.game_state_manager, 'ui') and self.game_state_manager.ui:
                self.game_state_manager.ui.animate_dice_roll()
            return

        action_methods = {
            "STASH": lambda: self.game_state_manager.stash_dice(self.game_state_manager.selected_dice),
            "BANK": self.bank_points,
            "START_NEW_STASH": self.start_new_stash,
            "END_TURN": self.end_turn
        }
        return action_methods[action]()
        
    def start_turn(self):
        self.game_state_manager.turn_started = True
        self.game_state_manager.current_player.roll_count = 0
        self.game_state_manager.current_player.stashed_dice_this_roll = False
        self.set_game_state(GameStateEnum.START_TURN)
        
        # CRITICAL: G-REF announces turn start for ALL players (human and bot)
        # This is the CORRECT place - in the official turn start method
        player_name = self.game_state_manager.current_player.user.username
        turn_number = self.game_state_manager.current_turn_number
        self.game_state_manager.message_manager.add_gref_turn_start(player_name, turn_number)

    def end_turn(self):
        # G-REF announces turn end for ALL players
        player_name = self.game_state_manager.current_player.user.username
        self.game_state_manager.message_manager.add_gref_turn_end(player_name)
        
        self.game_state_manager.next_player()
        self.set_game_state(GameStateEnum.NEXTUP_READYUP)

    def start_new_stash(self):
        current_player = self.game_state_manager.current_player
        current_player.stash_stash += sum(current_player.stashed_dice_scores)
        current_player.move_stash_to_stash_stash()
        current_player.stashed_dice = []
        current_player.stashed_dice_scores = []
        current_player.stashes_this_turn = 0
        current_player.stash_level += 1
        self.set_game_state(GameStateEnum.NEW_STASH)

    def bust(self):
        self.game_state_manager.bust_state = True
        self.game_state_manager.busted_player = self.game_state_manager.current_player
        self.game_state_manager.busted_lost_score = self.calculate_turn_score()
        self.game_state_manager.current_player.record_turn(
            self.game_state_manager.current_player.turn_count + 1, 0, 
            self.game_state_manager.current_player.roll_count, 0
        )
        
        # CRITICAL: G-REF announces bust for ALL players (human and bot)
        player_name = self.game_state_manager.current_player.user.username
        lost_points = self.game_state_manager.busted_lost_score
        self.game_state_manager.message_manager.add_gref_bust(
            player_name=player_name,
            lost_points=lost_points
        )
        
        self.set_game_state(GameStateEnum.BUST_TURN_SUMMARY)

    def bank_points(self):
        """
        Bank points and check if player reached endgoal.
        CRITICAL: This is where FINAL_TURNS gets triggered!
        """
        current_player = self.game_state_manager.current_player
        total_score = self.calculate_turn_score()
        current_player.record_turn(
            current_player.turn_count + 1, total_score, 
            current_player.roll_count, current_player.full_stashes_moved_this_turn
        )
        self.game_state_manager.turn_banked = True
        
        # CRITICAL: G-REF announces bank for ALL players (human and bot)
        player_name = current_player.user.username
        self.game_state_manager.message_manager.add_gref_bank_action(
            player_name=player_name,
            points=total_score
        )
        
        # CRITICAL: Check if player reached endgoal and trigger FINAL_TURNS
        # This must happen AFTER banking so the score is updated
        if current_player.get_total_score() >= self.game_state_manager.endgoal:
            if not self.game_state_manager.final_turns_triggered:
                # First player to reach endgoal - trigger FINAL_TURNS
                self.game_state_manager.final_turns_triggered = True
                self.game_state_manager.final_turns_player = current_player
                self.game_state_manager.final_turns_turn_number = current_player.turn_count
                self.game_state_manager.final_turns_score = current_player.get_total_score()
                
                # Transition to FINAL_TURNS state
                self.set_game_state(GameStateEnum.FINAL_TURNS)
                
                # G-REF announces FINAL TURNS
                self.game_state_manager.message_manager.add_gref_official_statement(
                    f"{player_name} HAS REACHED THE ENDGOAL! FINAL TURNS BEGINNING!"
                )
                return
        
        self.set_game_state(GameStateEnum.BANKED_TURN_SUMMARY)
        current_player.stash_stash = 0
