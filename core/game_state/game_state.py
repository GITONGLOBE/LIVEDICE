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
        self.stash_level = 1
        self.stash_house = 0
        self.stash_house_count = 0

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
        self.total_turns = 0

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
        self.total_turns += 1
        self.reset_turn()
        self.turn_started = False

    def start_new_stash(self):
        self.current_player.stash_level += 1
        self.current_player.roll_count = 0
        self.current_player.stashed_dice = []
        self.add_log_entry(f"Starting {self.get_next_stash_number()} stash for {self.current_player.user.username}")

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def set_active_task(self, task: str):
        self.active_task = task

    def add_chat_message(self, user: User, message: str):
        self.game_chat.append({"user": user.username, "message": message})

    def add_log_entry(self, entry: str):
        self.game_log.append(entry)
        if len(self.game_log) > 1000:  # Limit the number of entries to prevent excessive memory usage
            self.game_log = self.game_log[-1000:]

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
        if len(dice) == 1:
            return dice[0] in [1, 5]
        elif len(dice) == 2:
            return dice[0] == dice[1] == 6
        elif len(dice) == 3:
            return len(set(dice)) == 1
        return False

    def stash_dice(self, indices: List[int]):
        stashed = [self.dice_values[i] for i in sorted(indices, reverse=True)]
        for i in sorted(indices, reverse=True):
            del self.dice_values[i]
        self.current_player.stashed_dice.extend(stashed)
        stash_score = self.calculate_score(stashed)
        self.current_player.turn_score += stash_score
        self.add_log_entry(f"{self.current_player.user.username} stashed dice: {', '.join(map(str, stashed))} for {stash_score} points")
        
        if len(self.current_player.stashed_dice) == 6:
            self.current_player.roll_count = 0
            self.dice_values = []  # Clear dice values to prepare for next roll
            self.add_log_entry(f"Stash is full. Player can start a new stash.")

    def get_next_stash_level(self):
        return self.current_player.stash_level + 1

    def get_next_stash_number(self):
        next_stash = self.current_player.stash_level + 1
        if next_stash == 1:
            return "1st"
        elif next_stash == 2:
            return "2nd"
        elif next_stash == 3:
            return "3rd"
        else:
            return f"{next_stash}th"
        
    def move_stash_to_stash_house(self):
        stash_score = self.calculate_score(self.current_player.stashed_dice)
        self.current_player.stash_house += stash_score
        self.current_player.stash_house_count += 1
        self.current_player.stashed_dice = []
        self.current_player.stash_level = self.get_next_stash_level()
        self.add_log_entry(f"{self.current_player.user.username} moved {stash_score} points to stash house. Total in stash house: {self.current_player.stash_house}")

    def bank_points(self):
        total_score = self.current_player.turn_score + self.current_player.stash_house + self.calculate_score(self.dice_values)
        self.current_player.score += total_score
        self.add_log_entry(f"{self.current_player.user.username} banked {total_score} points. Total: {self.current_player.score}")
        self.current_player.turn_score = 0
        self.current_player.stash_house = 0
        self.current_player.stash_house_count = 0
        self.current_player.stashed_dice = []
        self.current_player.stash_level = 1
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
        self.current_player.stash_level = 1
        self.dice_values = []

    def bust(self):
        lost_score = self.current_player.turn_score + self.current_player.stash_house
        self.current_player.turn_score = 0
        self.current_player.stash_house = 0
        self.current_player.stash_house_count = 0
        self.add_log_entry(f"{self.current_player.user.username} busted! Lost {lost_score} points.")
        self.next_player()

    def bot_turn(self):
        self.turn_started = True
        self.bot_turn_result = "BOT_TURN_START"
        return self.bot_turn_result

    def bot_action(self, action):
        if action == "ROLL":
            scoring_combinations = self.roll_dice()
            if not scoring_combinations:
                self.bust()
                self.bot_turn_result = "BOT_BUST"
            else:
                self.bot_turn_result = "BOT_ROLLED"
        elif action == "STASH":
            all_scoring_dice = [i for i, die in enumerate(self.dice_values) if self.is_scoring_dice([die])]
            self.stash_dice(all_scoring_dice)
            self.bot_turn_result = "BOT_STASHED"
        elif action == "BANK":
            self.bank_points()
            self.bot_turn_result = "BOT_BANKED"
        
        self.add_log_entry(f"Bot action: {action}")
        return self.bot_turn_result