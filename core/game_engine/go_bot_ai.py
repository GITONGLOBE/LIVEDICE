import random
from games.livedice_f.livedice_f_rules import GameStateEnum, LiveDiceFRules

class BotAI:
    def __init__(self, game_state):
        self.game_state = game_state
        self.thinking_message = ""

    def make_decision(self):
        current_state = self.game_state.current_game_state
        print(f"BotAI: Current game state is {current_state}")

        state_decisions = {
            GameStateEnum.NEXTUP_READYUP: "START_TURN",
            GameStateEnum.START_TURN: "ROLL",
            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS: self.decide_stash_or_bank,
            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED: self.decide_stash_or_bank,
            GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED_CURRENTROLL: self.decide_roll_or_bank,
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

        print(f"BotAI decision: {decision}")
        return decision, self.thinking_message

    def decide_stash_or_bank(self):
        """Smart stashing decision with value-per-dice calculation"""
        stashable_dice = self.game_state.referee.get_stashable_dice(self.game_state.dice_values)
        
        if not stashable_dice:
            self.thinking_message = "NO SCORING DICE AVAILABLE"
            return "END_TURN"
        
        # Must stash in ROLLRESULT_POSITIVE_STASHOPTIONS state
        if self.game_state.current_game_state == GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS:
            return self.smart_stash_selection()
        
        # After initial stash, decide whether to bank
        return self.decide_roll_or_bank()

    def smart_stash_selection(self):
        """Intelligently select which dice to stash based on value-per-dice"""
        dice_values = self.game_state.dice_values
        stashable = self.game_state.referee.get_stashable_dice(dice_values)
        
        # Analyze dice values
        ones = [i for i in stashable if dice_values[i] == 1]
        fives = [i for i in stashable if dice_values[i] == 5]
        
        # Find triples
        triples = []
        for value in [2, 3, 4, 5, 6]:
            indices = [i for i in stashable if dice_values[i] == value]
            if len(indices) >= 3:
                triples.append((value, indices[:3]))
        
        # Strategy: ALWAYS stash ones (100pts each)
        # Stash triples if good value
        # Avoid stashing fives unless necessary
        
        to_stash = []
        
        # Always stash 1s
        to_stash.extend(ones)
        
        # Stash high-value triples
        for value, indices in triples:
            if value >= 2:  # Triple 2s = 200pts (66/dice), worth it
                to_stash.extend(indices)
        
        # Check if stashing everything fills the stash
        if len(to_stash) + len(self.game_state.current_player.stashed_dice) == 6:
            # Fill stash to trigger stash stash
            to_stash = stashable.copy()
            self.thinking_message = "FILLING STASH TO MOVE TO STASH STASH - MAXIMIZING POINTS"
        elif len(to_stash) == 0:
            # No good dice, stash everything available
            to_stash = stashable.copy()
            self.thinking_message = "STASHING ALL AVAILABLE DICE"
        elif len(to_stash) < len(stashable):
            # We're being selective
            remaining_dice = 6 - len(self.game_state.current_player.stashed_dice) - len(to_stash)
            self.thinking_message = f"STASHING ONLY HIGH-VALUE DICE - KEEPING {remaining_dice} DICE FOR BETTER ROLLS"
        else:
            self.thinking_message = "STASHING ALL SCORING DICE"
        
        # Store the smart selection
        self.game_state.selected_dice = to_stash
        return "STASH"

    def decide_roll_or_bank(self):
        """Advanced decision-making considering game state, risk, and strategy"""
        virtual_score = self.game_state.referee.calculate_turn_score()
        remaining_dice = self.game_state.real_time_counters.rollcupdice_var
        current_score = self.game_state.referee.get_total_score(self.game_state.current_player)
        target_score = self.game_state.endgoal
        
        # Check if we can win by banking now
        if current_score + virtual_score >= target_score:
            return self.evaluate_winning_position(current_score, virtual_score, remaining_dice)
        
        # Evaluate our position relative to other players
        my_position = self.get_position_analysis()
        
        # Risk assessment based on remaining dice
        bust_risk = self.calculate_bust_risk(remaining_dice)
        
        # Adjust strategy based on position
        if my_position["leading"]:
            # We're in the lead - play more conservatively
            return self.conservative_decision(virtual_score, remaining_dice, bust_risk)
        elif my_position["close_race"]:
            # Close race - balanced risk
            return self.balanced_decision(virtual_score, remaining_dice, bust_risk)
        else:
            # Behind - need to take risks
            return self.aggressive_decision(virtual_score, remaining_dice, bust_risk)

    def evaluate_winning_position(self, current_score, virtual_score, remaining_dice):
        """Decide whether to bank for win or push for more points"""
        target_score = self.game_state.endgoal
        total_if_banked = current_score + virtual_score
        
        # Check if other players are close
        other_players_close = False
        for player in self.game_state.players:
            if player != self.game_state.current_player:
                if player.get_total_score() >= target_score * 0.85:  # Within 15% of win
                    other_players_close = True
                    break
        
        if remaining_dice >= 4 and other_players_close and virtual_score >= 500:
            # High dice count and opponents close - go for more points
            self.thinking_message = "OPPONENTS ARE CLOSE - PUSHING FOR MORE POINTS DESPITE HAVING WINNING SCORE"
            return "ROLL"
        elif remaining_dice <= 2:
            # Low dice - too risky
            self.thinking_message = f"BANKING TO WIN WITH {total_if_banked} POINTS - TOO RISKY TO CONTINUE WITH {remaining_dice} DICE"
            return "BANK"
        else:
            # Safe to bank for win
            self.thinking_message = f"BANKING FOR THE WIN WITH {total_if_banked} POINTS"
            return "BANK"

    def get_position_analysis(self):
        """Analyze our position relative to other players"""
        my_score = self.game_state.referee.get_total_score(self.game_state.current_player)
        other_scores = [self.game_state.referee.get_total_score(p) for p in self.game_state.players 
                       if p != self.game_state.current_player]
        
        if not other_scores:
            return {"leading": False, "close_race": False, "lead_amount": 0}
        
        max_other = max(other_scores)
        min_other = min(other_scores)
        avg_other = sum(other_scores) / len(other_scores)
        
        lead_amount = my_score - max_other
        leading = lead_amount > 0
        close_race = abs(lead_amount) < 500  # Within 500 points
        
        return {
            "leading": leading,
            "close_race": close_race,
            "lead_amount": lead_amount,
            "max_opponent": max_other
        }

    def calculate_bust_risk(self, remaining_dice):
        """Calculate probability of busting based on remaining dice"""
        if remaining_dice >= 5:
            return 0.1  # Very low risk
        elif remaining_dice == 4:
            return 0.25  # Low risk
        elif remaining_dice == 3:
            return 0.45  # Moderate risk
        elif remaining_dice == 2:
            return 0.70  # High risk
        else:  # 1 die
            return 0.85  # Very high risk

    def conservative_decision(self, virtual_score, remaining_dice, bust_risk):
        """Conservative strategy when leading"""
        if virtual_score >= 600:
            self.thinking_message = f"LEADING THE GAME - BANKING {virtual_score} POINTS TO PROTECT MY LEAD"
            return "BANK"
        elif remaining_dice >= 5:
            self.thinking_message = "SAFE TO ROLL WITH MANY DICE"
            return "ROLL"
        elif remaining_dice >= 3 and virtual_score < 400:
            self.thinking_message = "SCORE TOO LOW - ONE MORE ROLL"
            return "ROLL"
        elif bust_risk > 0.5:
            self.thinking_message = f"BANKING {virtual_score} POINTS - TOO RISKY TO CONTINUE"
            return "BANK"
        else:
            self.thinking_message = "ONE MORE CALCULATED ROLL"
            return "ROLL" if random.random() > 0.6 else "BANK"

    def balanced_decision(self, virtual_score, remaining_dice, bust_risk):
        """Balanced strategy in close race"""
        if virtual_score >= 500:
            if bust_risk > 0.6:
                self.thinking_message = f"BANKING {virtual_score} POINTS IN CLOSE RACE"
                return "BANK"
            else:
                self.thinking_message = "PUSHING FOR MORE IN CLOSE RACE"
                return "ROLL" if random.random() > 0.5 else "BANK"
        elif remaining_dice >= 4:
            self.thinking_message = f"ROLLING AGAIN WITH {remaining_dice} DICE"
            return "ROLL"
        elif remaining_dice >= 2:
            roll_chance = 0.7 if virtual_score < 350 else 0.4
            decision = "ROLL" if random.random() < roll_chance else "BANK"
            self.thinking_message = f"{'ROLLING' if decision == 'ROLL' else 'BANKING'} WITH {remaining_dice} DICE AND {virtual_score} POINTS"
            return decision
        else:
            self.thinking_message = f"BANKING {virtual_score} POINTS - ONE DIE TOO RISKY"
            return "BANK"

    def aggressive_decision(self, virtual_score, remaining_dice, bust_risk):
        """Aggressive strategy when behind"""
        position = self.get_position_analysis()
        points_behind = abs(position["lead_amount"])
        
        if virtual_score >= 700:
            self.thinking_message = f"GREAT SCORE OF {virtual_score} - BANKING TO CATCH UP"
            return "BANK"
        elif remaining_dice >= 3:
            self.thinking_message = f"BEHIND BY {points_behind} - TAKING RISKS TO CATCH UP"
            return "ROLL"
        elif remaining_dice == 2:
            if virtual_score < 400:
                self.thinking_message = "NEED MORE POINTS - ROLLING WITH 2 DICE"
                return "ROLL" if random.random() < 0.6 else "BANK"
            else:
                self.thinking_message = f"BANKING {virtual_score} POINTS"
                return "BANK"
        else:
            if virtual_score < 300 and points_behind > 1000:
                self.thinking_message = "DESPERATE SITUATION - RISKING ONE DIE ROLL"
                return "ROLL" if random.random() < 0.3 else "BANK"
            else:
                self.thinking_message = f"BANKING {virtual_score} POINTS"
                return "BANK"

    def get_stash_indices(self):
        """Return smartly selected stash indices"""
        return self.game_state.selected_dice if self.game_state.selected_dice else self.game_state.referee.get_stashable_dice(self.game_state.dice_values)

    def format_number(self, number):
        return str(number).replace('0', 'O')
