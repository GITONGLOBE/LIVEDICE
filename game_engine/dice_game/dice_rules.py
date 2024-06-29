class DiceRules:
    @staticmethod
    def check_for_doubles(roll):
        return len(set(roll)) < len(roll)

    @staticmethod
    def check_for_straight(roll):
        return sorted(roll) == list(range(min(roll), max(roll) + 1))

    @staticmethod
    def calculate_score(roll, total):
        score = total
        if DiceRules.check_for_doubles(roll):
            score *= 2
        if DiceRules.check_for_straight(roll):
            score *= 3
        return score