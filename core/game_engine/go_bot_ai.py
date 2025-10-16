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
        """
        CRITICAL FIX: Bot must stash dice before it can bank.
        In ROLLRESULT_POSITIVE_STASHOPTIONS state, the bot CANNOT bank yet.
        It must first STASH the dice, which transitions to a state where banking is allowed.
        """
        stashable_dice = self.game_state.referee.get_stashable_dice(self.game_state.dice_values)
        current_score = self.game_state.referee.calculate_table_score()
        virtual_score = self.game_state.referee.calculate_turn_score()
        
        # Safety check: If no stashable dice, we're in trouble
        if not stashable_dice:
            if self.game_state.referee.can_bank():
                print("BotAI: No stashable dice but can bank - banking")
                return "BANK"
            print("BotAI: No stashable dice and can't bank - ending turn")
            return "END_TURN"
        
        # Check if stash is full
        if self.game_state.referee.is_full_stash():
            print("BotAI: Stash is full - starting new stash")
            return "START_NEW_STASH"
        
        # CRITICAL: In ROLLRESULT_POSITIVE_STASHOPTIONS state, we MUST stash first
        # We cannot bank directly from this state
        current_state = self.game_state.current_game_state
        if current_state == GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS:
            print("BotAI: In ROLLRESULT_POSITIVE_STASHOPTIONS - must stash before banking")
            # Always stash in this state - we can decide to bank after stashing
            return "STASH"
        
        # If we have stashed dice this turn, we can consider banking
        has_stashed = len(self.game_state.current_player.stashed_dice) > 0
        
        # Evaluate if we should bank based on score and risk
        if has_stashed and self.should_bank(virtual_score):
            if self.game_state.referee.can_bank():
                print(f"BotAI: Deciding to bank {virtual_score} points")
                return "BANK"
            else:
                print("BotAI: Want to bank but can't - stashing instead")
                return "STASH"
        
        # Aggressive stashing strategies for high-value combinations
        if len(stashable_dice) >= 3 and len(set(self.game_state.dice_values[i] for i in stashable_dice)) == 1:
            print("BotAI: Found triple - stashing")
            return "STASH"
        
        if current_score >= 350:
            print(f"BotAI: High table score ({current_score}) - stashing")
            return "STASH"
        
        if len(stashable_dice) == len(self.game_state.dice_values):
            print("BotAI: All dice are stashable - stashing")
            return "STASH"
        
        # Default: stash the dice
        print("BotAI: Default action - stashing")
        return "STASH"

    def decide_roll_or_bank(self):
        virtual_score = self.game_state.referee.calculate_turn_score()
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        
        print(f"BotAI: decide_roll_or_bank - score: {virtual_score}, remaining dice: {remaining_dice}")
        
        # Risk-based decision making
        if remaining_dice >= 5:
            print("BotAI: 5+ dice remaining - rolling")
            return "ROLL"
        elif remaining_dice == 4:
            decision = "ROLL" if random.random() < 0.8 else "BANK"
            print(f"BotAI: 4 dice remaining - {decision}")
            return decision
        elif remaining_dice == 3:
            decision = "ROLL" if random.random() < 0.6 else "BANK"
            print(f"BotAI: 3 dice remaining - {decision}")
            return decision
        elif remaining_dice == 2:
            decision = "ROLL" if random.random() < 0.4 else "BANK"
            print(f"BotAI: 2 dice remaining - {decision}")
            return decision
        elif remaining_dice == 1:
            decision = "ROLL" if random.random() < 0.2 else "BANK"
            print(f"BotAI: 1 die remaining - {decision}")
            return decision
        
        # Score-based decision
        if self.should_bank(virtual_score):
            print(f"BotAI: Score threshold met ({virtual_score}) - banking")
            return "BANK"
        else:
            if self.game_state.referee.can_roll():
                print("BotAI: Score threshold not met and can roll - rolling")
                return "ROLL"
            else:
                print("BotAI: Can't roll - banking")
                return "BANK"

    def get_stash_indices(self):
        """Return all stashable dice indices"""
        return self.game_state.referee.get_stashable_dice(self.game_state.dice_values)

    def should_bank(self, virtual_score):
        """
        Determine if the bot should bank based on current score,
        game situation, and risk tolerance.
        """
        current_player_score = self.game_state.referee.get_total_score(self.game_state.current_player)
        target_score = LiveDiceFRules.TARGET_SCORE
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        
        # Early game strategy (conservative)
        if current_player_score < 1000:
            threshold = 350
            dice_factor = remaining_dice <= 2 and random.random() < 0.8
            result = virtual_score >= threshold or dice_factor
            if result:
                print(f"BotAI: Early game - score {virtual_score} >= {threshold} or risky dice")
            return result
        
        # Mid game strategy (moderate)
        elif current_player_score < 3000:
            threshold = 500
            dice_factor = remaining_dice <= 3 and random.random() < 0.7
            result = virtual_score >= threshold or dice_factor
            if result:
                print(f"BotAI: Mid game - score {virtual_score} >= {threshold} or risky dice")
            return result
        
        # Late game strategy (aggressive)
        else:
            points_needed = target_score - current_player_score
            dice_factor = remaining_dice <= 4 and random.random() < 0.6
            result = virtual_score >= points_needed or dice_factor
            if result:
                print(f"BotAI: Late game - score {virtual_score} >= {points_needed} needed or risky dice")
            return result

    def format_number(self, number):
        return str(number).replace('0', 'O')

    def evaluate_risk(self):
        """Evaluate risk level based on remaining dice"""
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        if remaining_dice == 1:
            return 0.8  # High risk with only one die
        elif remaining_dice == 2:
            return 0.6  # Moderate risk with two dice
        elif remaining_dice <= 4:
            return 0.4  # Lower risk with 3-4 dice
        else:
            return 0.2  # Low risk with 5-6 dice
