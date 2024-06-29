from .dice_rules import DiceRules
import random

class DiceEngine:
    def __init__(self, num_dice=2, num_sides=6):
        self.num_dice = num_dice
        self.num_sides = num_sides

    def roll_dice(self):
        return [random.randint(1, self.num_sides) for _ in range(self.num_dice)]

    def calculate_total(self, roll):
        return sum(roll)

    def get_roll_result(self):
        roll = self.roll_dice()
        total = self.calculate_total(roll)
        score = DiceRules.calculate_score(roll, total)
        return roll, total, score