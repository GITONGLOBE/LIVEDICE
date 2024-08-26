from typing import List, Tuple
from games.livedice_f.livedice_f_rules import LiveDiceFRules, GameStateEnum

class GameReferee:
    def __init__(self, game_state_manager):
        self.game_state_manager = game_state_manager

    def update_game_state(self):
        self.game_state_manager.real_time_counters.update_counters(self.game_state_manager)

    def calculate_total_score(self) -> int:
        return (self.game_state_manager.current_player.score +
                self.calculate_turn_score())

    def calculate_virtual_score(self) -> int:
        return self.calculate_turn_score()
            
    def calculate_stash_score(self) -> int:
        return sum(self.game_state_manager.current_player.stashed_dice_scores)
    
    def get_stash_number(self) -> str:
        return LiveDiceFRules.get_stash_number(self.game_state_manager.current_player.stash_level)

    def get_next_stash_number(self) -> str:
        return LiveDiceFRules.get_stash_number(self.game_state_manager.current_player.stash_level + 1)

    def get_stash_stash_info(self) -> Tuple[int, int]:
        stash_stash_points = self.game_state_manager.current_player.stash_stash
        full_stashes_moved = self.game_state_manager.current_player.full_stashes_moved_this_turn
        return stash_stash_points, full_stashes_moved

    def calculate_turn_score(self) -> int:
        return (self.calculate_score(self.game_state_manager.dice_values) +
                self.calculate_stash_score() +
                self.game_state_manager.current_player.stash_stash)

    def is_bust(self) -> bool:
        return LiveDiceFRules.is_bust(self.game_state_manager.dice_values)

    def is_scoring_dice(self, dice: List[int]) -> bool:
        return LiveDiceFRules.is_scoring_dice(dice)

    def can_roll(self) -> bool:
        if self.game_state_manager.can_roll_once:
            return True
        return (
            LiveDiceFRules.can_roll_six_dice(
                self.game_state_manager.turn_started,
                self.game_state_manager.current_player.stashed_dice,
                self.game_state_manager.current_player.roll_count
            ) or
            (self.game_state_manager.current_player.stashed_dice_this_roll and 
            len(self.game_state_manager.dice_values) > 0) or
            self.game_state_manager.current_game_state == GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED_CURRENTROLL or
            self.game_state_manager.current_game_state == GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL or
            self.game_state_manager.current_game_state == GameStateEnum.NEW_STASH
        ) and self.game_state_manager.current_game_state != GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH
    
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

    def can_stash(self) -> bool:
        return LiveDiceFRules.can_stash(self.game_state_manager.selected_dice)

    def can_bank(self) -> bool:
        return LiveDiceFRules.can_bank(self.game_state_manager.turn_started, self.calculate_virtual_score())

    def is_full_stash(self) -> bool:
        return LiveDiceFRules.is_full_stash(self.game_state_manager.current_player.stashed_dice)

    def get_stash_button_text(self) -> str:
        stash_points = self.calculate_score([self.game_state_manager.dice_values[i] for i in self.game_state_manager.selected_dice])
        total_stash_points = self.game_state_manager.real_time_counters.stashplusselection_vscore
        stash_stash_points = self.game_state_manager.real_time_counters.stashstash_vscore
        full_stashes_moved = self.game_state_manager.current_player.full_stashes_moved
        return f"STASH {stash_points} POINTS\nTOTAL STASH: {total_stash_points} POINTS\nSTASH STASH: {stash_stash_points} POINTS ({full_stashes_moved} STASHES)"

    def get_bank_button_text(self) -> str:
        virtual_score = self.calculate_virtual_score()
        return f"BANK {virtual_score} POINTS\n" \
            f"TABLE: {self.game_state_manager.real_time_counters.table_vscore} / " \
            f"STASH: {self.game_state_manager.real_time_counters.stash_vscore} / " \
            f"STASH STASH: {self.game_state_manager.real_time_counters.stashstash_vscore}"

    def get_full_stash_button_text(self) -> str:
        stash_points = self.game_state_manager.real_time_counters.stash_vscore
        return f"FULL STASH\nMOVE {stash_points} POINTS TO STASH STASH\nSTART {self.get_next_stash_number()} STASH"

    def can_select_dice(self, dice_index: int) -> bool:
        stashable_dice = self.get_stashable_dice(self.game_state_manager.dice_values)
        return dice_index in stashable_dice

    def is_turn_over(self) -> bool:
        return self.game_state_manager.bust_state or self.game_state_manager.turn_banked

    def should_start_new_turn(self) -> bool:
        return LiveDiceFRules.should_start_new_turn(
            self.game_state_manager.dice_values,
            self.game_state_manager.current_player.stashed_dice,
            self.game_state_manager.turn_started
        )

    def is_game_over(self) -> bool:
        player_scores = [player.get_total_score() for player in self.game_state_manager.players]
        return LiveDiceFRules.is_game_over(player_scores)

    def get_stashable_dice(self, dice_values: List[int]) -> List[int]:
        return LiveDiceFRules.get_stashable_dice(dice_values)

    def calculate_score(self, dice_values: List[int], stashed_together: bool = False) -> int:
        return LiveDiceFRules.calculate_score(dice_values, stashed_together)

    def get_scoring_combinations(self, dice_values: List[int]) -> List[Tuple[str, int]]:
        return LiveDiceFRules.get_scoring_combinations(dice_values)

    def describe_stash(self, stashed: List[int]) -> str:
        return LiveDiceFRules.describe_stash(stashed)
    
    def get_dice_for_combination(self, dice_values: List[int], combination_name: str) -> List[int]:
        return LiveDiceFRules.get_dice_for_combination(dice_values, combination_name)

    def set_game_state(self, new_state: GameStateEnum):
        self.game_state_manager.current_game_state = new_state

    def has_stashed_dice(self) -> bool:
        return len(self.game_state_manager.current_player.stashed_dice) > 0