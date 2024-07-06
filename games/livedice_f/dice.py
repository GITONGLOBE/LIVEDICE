import random

class Dice:
    def __init__(self):
        self.num_dice = 6

    def roll(self):
        return [random.randint(1, 6) for _ in range(self.num_dice)]