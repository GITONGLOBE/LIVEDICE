import random
from dice_game_engine.dice_rules import DiceRules

class BotPlayer:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty

    def make_decision(self, game_state):
        if self.difficulty == 'easy':
            return self.easy_decision(game_state)
        elif self.difficulty == 'medium':
            return self.medium_decision(game_state)
        elif self.difficulty == 'hard':
            return self.hard_decision(game_state)

    def easy_decision(self, game_state):
        # Simple random decision
        return random.choice(DiceRules.get_valid_actions(game_state))

    def medium_decision(self, game_state):
        # Basic strategy: prefer actions that increase score
        valid_actions = DiceRules.get_valid_actions(game_state)
        scored_actions = [(action, self.evaluate_action(action, game_state)) for action in valid_actions]
        return max(scored_actions, key=lambda x: x[1])[0]

    def hard_decision(self, game_state):
        # Advanced strategy: consider opponent's state and game progression
        valid_actions = DiceRules.get_valid_actions(game_state)
        scored_actions = [(action, self.evaluate_action(action, game_state, consider_opponent=True)) 
                          for action in valid_actions]
        return max(scored_actions, key=lambda x: x[1])[0]

    def evaluate_action(self, action, game_state, consider_opponent=False):
        # Placeholder for action evaluation logic
        # This should be implemented based on your specific game rules
        score = 0
        # Add score based on action type, potential points, risk, etc.
        # If consider_opponent is True, also factor in opponent's state
        return score