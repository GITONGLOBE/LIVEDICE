import random
from games.livedice_f.livedice_f_rules import GameStateEnum, LiveDiceFRules

class BotAI:
    def __init__(self, game_state):
        self.game_state = game_state

    def make_decision(self):
        current_state = self.game_state.current_game_state
        print(f"BotAI: Current game state is {current_state}")

        state_decisions = {
            GameStateEnum.NEXTUP_READYUP: "START_TURN",
            GameStateEnum.START_TURN: "ROLL",
            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS: self.decide_stash_or_bank,
            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED: self.decide_stash_or_bank,
            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL: self.decide_stash_or_bank,
            GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_FULL: self.decide_stash_or_bank,
            GameStateEnum.STASHCHOICE_STASHED_ALL: self.decide_roll_or_bank,
            GameStateEnum.STASHCHOICE_STASHED_PARTIAL: self.decide_roll_or_bank,
            GameStateEnum.STASHCHOICE_STASHED_FULL: "START_NEW_STASH",
            GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL: "ROLL",
            GameStateEnum.NEW_STASH: "ROLL",
            GameStateEnum.BANKED_TURN_SUMMARY: "END_TURN",
            GameStateEnum.BUST_TURN_SUMMARY: "END_TURN"
        }

        decision = state_decisions.get(current_state, lambda: "BANK")
        if callable(decision):
            decision = decision()

        # Always try to bank before ending turn
        if decision == "END_TURN" and self.game_state.referee.can_bank():
            decision = "BANK"

        print(f"BotAI decision: {decision}")
        return decision

    def decide_stash_or_bank(self):
        stashable_dice = self.game_state.referee.get_stashable_dice(self.game_state.dice_values)
        current_score = self.game_state.referee.calculate_table_score()
        virtual_score = self.game_state.referee.calculate_turn_score()
        
        if not stashable_dice:
            return "BANK" if self.game_state.referee.can_bank() else "END_TURN"
        
        if self.game_state.referee.is_full_stash():
            return "START_NEW_STASH"
        elif len(stashable_dice) >= 3 and len(set(self.game_state.dice_values[i] for i in stashable_dice)) == 1:
            return "STASH"
        elif current_score >= 350:
            return "STASH"
        elif len(stashable_dice) == len(self.game_state.dice_values):
            return "STASH"
        elif self.should_bank(virtual_score):
            return "BANK"
        else:
            return "STASH"

    def decide_roll_or_bank(self):
        virtual_score = self.game_state.referee.calculate_turn_score()
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        
        if remaining_dice >= 5:
            return "ROLL"
        elif remaining_dice == 4:
            return "ROLL" if random.random() < 0.8 else "BANK"
        elif remaining_dice == 3:
            return "ROLL" if random.random() < 0.6 else "BANK"
        elif remaining_dice == 2:
            return "ROLL" if random.random() < 0.4 else "BANK"
        elif remaining_dice == 1:
            return "ROLL" if random.random() < 0.2 else "BANK"
        
        if self.should_bank(virtual_score):
            return "BANK"
        else:
            return "ROLL" if self.game_state.referee.can_roll() else "BANK"

    def get_stash_indices(self):
        return self.game_state.referee.get_stashable_dice(self.game_state.dice_values)

    def should_bank(self, virtual_score):
        current_player_score = self.game_state.referee.get_total_score(self.game_state.current_player)
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

    def format_number(self, number):
        return str(number).replace('0', 'O')

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