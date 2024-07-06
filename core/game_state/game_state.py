import random
from typing import List, Dict
from ..account.user import User
import time

class Player:
    def __init__(self, user: User):
        self.user = user
        self.score = 0
        self.turn_score = 0
        self.stashed_dice = []
        self.is_active = False
        self.turn_count = 0
        self.roll_count = 0
        self.stash_level = "primary"

class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.current_player_index: int = 0
        self.dice_values: List[int] = []
        self.active_task: str = ""
        self.game_chat: List[Dict[str, str]] = []
        self.game_log: List[str] = []
        self.game_over = False
        self.bust_state = False
        self.bot_turn_result = ""
        self.turn_started = False

    def add_player(self, user: User):
        player = Player(user)
        self.players.append(player)

    def roll_dice(self):
        num_dice = 6 - len(self.current_player.stashed_dice)
        self.dice_values = [random.randint(1, 6) for _ in range(num_dice)]
        self.current_player.roll_count += 1
        self.add_log_entry(f"{self.current_player.user.username} rolled: {', '.join(map(str, self.dice_values))}")
        return self.get_scoring_combinations()

    def next_player(self):
        self.players[self.current_player_index].is_active = False
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.players[self.current_player_index].is_active = True
        self.players[self.current_player_index].turn_count += 1
        self.reset_turn()
        self.turn_started = False

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def set_active_task(self, task: str):
        self.active_task = task

    def add_chat_message(self, user: User, message: str):
        self.game_chat.append({"user": user.username, "message": message})

    def add_log_entry(self, entry: str):
        self.game_log.append(entry)

    def get_scoring_combinations(self):
        counts = [self.dice_values.count(i) for i in range(1, 7)]
        combinations = []

        if counts[0] >= 3:
            combinations.append(("TRIPLE 1", 1000))
        for i in range(1, 6):
            if counts[i] >= 3:
                combinations.append((f"TRIPLE {i+1}", (i+1) * 100))
        if counts[5] >= 2:
            combinations.append(("DOUBLE 6", 100))

        # Add single 1s and 5s
        if counts[0] > 0 and counts[0] < 3:
            combinations.append((f"SINGLE 1{'s' if counts[0] > 1 else ''}", counts[0] * 100))
        if counts[4] > 0 and counts[4] < 3:
            combinations.append((f"SINGLE 5{'s' if counts[4] > 1 else ''}", counts[4] * 50))

        return combinations

    def calculate_score(self, dice: List[int]):
        score = 0
        counts = [dice.count(i) for i in range(1, 7)]
        
        if counts[0] >= 3:
            score += 1000
            counts[0] -= 3
        for i in range(1, 6):
            if counts[i] >= 3:
                score += (i+1) * 100
                counts[i] -= 3

        score += counts[0] * 100  # Remaining 1s
        score += counts[4] * 50   # Remaining 5s

        if counts[5] >= 2:
            score += 100

        return score

    def is_scoring_dice(self, dice: List[int]):
        return self.calculate_score(dice) > 0

    def stash_dice(self, indices: List[int]):
        stashed = [self.dice_values[i] for i in sorted(indices, reverse=True)]
        for i in sorted(indices, reverse=True):
            del self.dice_values[i]
        self.current_player.stashed_dice.extend(stashed)
        stash_score = self.calculate_score(stashed)
        self.current_player.turn_score += stash_score
        self.add_log_entry(f"{self.current_player.user.username} stashed dice: {', '.join(map(str, stashed))} for {stash_score} points")
        
        if len(self.current_player.stashed_dice) == 6:
            self.current_player.stash_level = self.get_next_stash_level()
            self.current_player.roll_count = 0
            self.roll_dice()

    def get_next_stash_level(self):
        levels = ["primary", "secondary", "tertiary", "quaternary", "quinary"]
        current_index = levels.index(self.current_player.stash_level)
        return levels[current_index + 1] if current_index + 1 < len(levels) else "further"

    def bank_points(self):
        total_score = self.current_player.turn_score + self.calculate_score(self.dice_values)
        self.current_player.score += total_score
        self.bot_turn_result = f"{self.current_player.user.username} BANKED [ {total_score} PLUS ]"
        self.add_log_entry(f"{self.current_player.user.username} banked {total_score} points. Total: {self.current_player.score}")
        self.next_player()

    def check_game_over(self):
        if any(player.score >= 4000 for player in self.players):
            self.game_over = True
            return True
        return False

    def reset_turn(self):
        self.current_player.turn_score = 0
        self.current_player.stashed_dice = []
        self.current_player.roll_count = 0
        self.current_player.stash_level = "primary"
        self.dice_values = []

    def bust(self):
        lost_score = self.current_player.turn_score
        self.current_player.turn_score = 0
        self.bot_turn_result = f"{self.current_player.user.username} BUSTED [ {lost_score} LOST ]"
        self.add_log_entry(f"{self.current_player.user.username} busted! Lost {lost_score} points.")
        self.bust_state = True
        self.reset_turn()

    def bot_turn(self):
        self.turn_started = True
        while self.current_player.user.username == "Bot" and not self.bust_state:
            time.sleep(2)  # 2-second delay for each bot action
            scoring_combinations = self.roll_dice()
            if not scoring_combinations:
                self.bust()
            else:
                all_scoring_dice = [i for i, die in enumerate(self.dice_values) if self.is_scoring_dice([die])]
                self.stash_dice(all_scoring_dice)
                if random.random() < 0.3:  # 30% chance to bank
                    self.bank_points()
                    break
        self.bust_state = False