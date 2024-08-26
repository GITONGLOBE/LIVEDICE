import random
from games.livedice_f.livedice_f_rules import GameStateEnum, LiveDiceFRules

class BotAI:
    def __init__(self, game_state):
        self.game_state = game_state

    def make_decision(self):
        current_state = self.game_state.current_game_state
        print(f"BotAI: Current game state is {current_state}")

        if current_state == GameStateEnum.START_TURN or current_state == GameStateEnum.NEXTUP_READYUP:
            return "ROLL"
        elif current_state in [GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS, 
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED,
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL, 
                            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_FULL]:
            return self.decide_stash_or_bank()
        elif current_state in [GameStateEnum.STASHCHOICE_STASHED_ALL, 
                            GameStateEnum.STASHCHOICE_STASHED_PARTIAL]:
            if self.game_state.referee.can_roll():
                return self.decide_roll_or_bank()
            else:
                return "BANK"
        elif current_state == GameStateEnum.STASHCHOICE_STASHED_FULL:
            return "START_NEW_STASH"
        elif current_state == GameStateEnum.NEW_STASH:
            return "ROLL"
        elif current_state in [GameStateEnum.BANKED_TURN_SUMMARY, GameStateEnum.BUST_TURN_SUMMARY]:
            return "END_TURN"
        else:
            print(f"BotAI: Unexpected game state: {current_state}")
            return "BANK"  # Default to banking if we're in an unexpected state

    def decide_stash_or_bank(self):
        stashable_dice = self.get_stash_indices()
        current_score = self.game_state.real_time_counters.table_vscore
        virtual_score = self.game_state.referee.calculate_virtual_score()
        
        if not stashable_dice:
            return "BANK" if self.game_state.referee.can_bank() else "END_TURN"
        
        if len(stashable_dice) >= 3 and len(set(self.game_state.dice_values[i] for i in stashable_dice)) == 1:
            return "STASH"
        elif current_score >= 350:
            return "STASH"
        elif len(stashable_dice) == len(self.game_state.dice_values):
            return "STASH"
        elif self.should_bank(virtual_score):
            return "BANK"
        else:
            return "STASH"  # Always stash before considering rolling again

    def decide_roll_or_bank(self):
        virtual_score = self.game_state.referee.calculate_virtual_score()
        
        if self.should_bank(virtual_score):
            return "BANK"
        else:
            return "ROLL" if self.game_state.referee.can_roll() else "BANK"

    def get_stash_indices(self):
        stashable_indices = self.game_state.referee.get_stashable_dice(self.game_state.dice_values)
        print(f"BotAI: Stashable indices: {stashable_indices}")
        print(f"BotAI: Current dice values: {self.game_state.dice_values}")
        return [i for i in stashable_indices if i < len(self.game_state.dice_values)]

    def should_bank(self, virtual_score):
        current_player_score = self.game_state.current_player.get_total_score()
        target_score = LiveDiceFRules.TARGET_SCORE
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        
        # Early game strategy
        if current_player_score < 1000:
            return virtual_score >= 350 or (remaining_dice <= 2 and random.random() < 0.8)
        
        # Mid game strategy
        elif current_player_score < 3000:
            return virtual_score >= 500 or (remaining_dice <= 3 and random.random() < 0.7)
        
        # Late game strategy
        else:
            points_needed = target_score - current_player_score
            return virtual_score >= points_needed or (remaining_dice <= 4 and random.random() < 0.6)

    def evaluate_risk(self):
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        if remaining_dice == 1:
            return 0.8  # High risk with only one die
        elif remaining_dice == 2:
            return 0.6  # Moderate risk with two dice
        elif remaining_dice <= 4:
            return 0.4  # Lower risk with 3-4 dice
        else:
            return 0.2  # Low risk with 5-6 dice