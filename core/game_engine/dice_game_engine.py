import random
from games.livedice_f.livedice_f_rules import LiveDiceFRules

class DiceGameEngine:
    def __init__(self, num_dice):
        self.num_dice = num_dice

    def roll_dice(self):
        return [random.randint(1, 6) for _ in range(self.num_dice)]

    def calculate_score(self, dice_values):
        return LiveDiceFRules.calculate_score(dice_values)

    def get_scoring_combinations(self, dice_values):
        return LiveDiceFRules.get_scoring_combinations(dice_values)

    def get_stashable_dice(self, dice_values):
        return LiveDiceFRules.get_stashable_dice(dice_values)

    def is_bust(self, dice_values):
        return LiveDiceFRules.is_bust(dice_values)

    def is_game_over(self, player_scores):
        return LiveDiceFRules.is_game_over(player_scores)