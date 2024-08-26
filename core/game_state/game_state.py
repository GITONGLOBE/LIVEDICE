from typing import List, Optional
import re
from core.account.user import User
from core.game_engine.game_referee import GameReferee
from core.game_state.real_time_score_counters import RealTimeScoreCounters
from games.livedice_f.livedice_f_rules import LiveDiceFRules, GameStateEnum

class Player:
    def __init__(self, user: User, player_number: int, game_state_manager):
        self.user = user
        self.player_number = player_number
        self.game_state_manager = game_state_manager
        self.turn_scores = {}  # Dictionary to store turn scores
        self.stashed_dice = []
        self.stashed_dice_scores = []  # List to store scores of each stash
        self.stashed_dice_this_roll = False
        self.stash_stash = 0
        self.full_stashes_moved = 0
        self.stashes_this_turn = 0
        self.stash_level = 1
        self.roll_count = 0
        self.turn_count = 0
        self.is_active = False
        self.banked_full_stashes = 0
        self.full_stashes_moved_this_turn = 0
        self.total_full_stashes_banked = 0

        self.bust_state = False
        self.busted_player = None
        self.busted_lost_score = 0

    def record_turn(self, turn_number: int, banked_score: int, rolls: int, full_stashes_moved: int):
        self.turn_scores[turn_number] = {
            "SCORE": banked_score,
            "ROLLS": rolls,
            "STASHES": full_stashes_moved
        }
        self.turn_count += 1
        self.banked_full_stashes += full_stashes_moved
        self.full_stashes_moved_this_turn = 0  # Reset for the next turn

    def get_total_banked_full_stashes(self) -> int:
        return self.banked_full_stashes

    def move_stash_to_stash_stash(self):
        self.full_stashes_moved_this_turn += 1

    def get_total_score(self) -> int:
        return sum(turn["SCORE"] for turn in self.turn_scores.values())

    def add_to_stash(self, dice, score):
        self.stashed_dice.extend(dice)
        self.stashed_dice_scores.append(score)
        self.stashes_this_turn += 1

    def get_full_stashes_moved(self, turn_number: int) -> int:
        return self.turn_scores.get(turn_number, {}).get("STASHES", 0)

    def get_turn_score(self, turn_number: int):
        return self.turn_scores.get(turn_number, {"SCORE": 0, "ROLLS": 0, "STASHES": 0})

    def is_bot(self) -> bool:
        return self.user.username.startswith("@GO-BOT")

    def get_stash_score(self):
        return sum(self.stashed_dice_scores)

    def get_game_scorerecord(self):
        return self.score

    def get_game_rolls(self):
        return sum(turn["ROLLS"] for turn in self.turn_scores.values())

    def get_game_stashes(self):
        return sum(turn["STASHES"] for turn in self.turn_scores.values())

    def reset_turn(self):
        self.stashed_dice = []
        self.stashed_dice_scores = []
        self.stash_stash = 0
        self.full_stashes_moved = 0
        self.stashes_this_turn = 0
        self.stash_level = 1
        self.roll_count = 0
        self.full_stashes_moved_this_turn = 0
        
class GameStateManager:
    def __init__(self, ui, human_players, ai_players):
        self.ui = ui
        self.players: List[Player] = []
        self.current_player_index = 0
        self.dice_values: List[int] = []
        self.selected_dice: List[int] = []
        self.turn_started = False
        self.turn_banked = False
        self.bust_state = False
        self.busted_player: Optional[Player] = None
        self.busted_lost_score = 0
        self.total_turns = 0
        self.game_log: List[str] = []
        self.active_task = ""
        self.referee = GameReferee(self)
        self.real_time_counters = RealTimeScoreCounters()
        self.current_game_state = GameStateEnum.START_TURN
        self.current_stashable_dice = []
        self.current_stashable_combinations = []
        self.current_turn_number = 1
        self.ui_needs_update = False

        # Add human players
        for i in range(human_players):
            self.add_player(User(f"@VIDEO-GAMER-{i+1}", f"videogamer{i+1}@example.com", "password"))

        # Add AI players
        for i in range(ai_players):
            self.add_player(User(f"@GO-BOT-{i+1}", f"gobot{i+1}@example.com", "password"))

        self.determine_starting_player()
        self.set_active_task("Click START TURN to begin your turn")

    def determine_starting_player(self):
        # Start with the first human player, if any
        human_players = [p for p in self.players if not p.is_bot()]
        bot_players = [p for p in self.players if p.is_bot()]
        
        if human_players:
            self.current_player_index = self.players.index(human_players[0])
        elif bot_players:
            self.current_player_index = self.players.index(bot_players[0])
        else:
            raise ValueError("No players in the game")
        
        self.players[self.current_player_index].is_active = True
        # We'll add this log entry later, after UI is fully initialized
        # self.add_log_entry(f"{self.players[self.current_player_index].user.username} starts the game")

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def can_roll_once(self):
        return self.current_game_state in [
            GameStateEnum.STASHCHOICE_STASHED_ALL,
            GameStateEnum.STASHCHOICE_STASHED_PARTIAL
        ]

    def add_player(self, user: User):
        player_number = len(self.players) + 1
        new_player = Player(user, player_number, self)
        self.players.append(new_player)
        if user.username == "@VIDEO-GAMER":
            self.players[0] = new_player  # Ensure @VIDEO-GAMER is always P1
        elif user.username == "@GO-BOT":
            self.players[1] = new_player  # Ensure @GO-BOT is always P2

    def next_player(self):
        print(f"Before next_player: current_turn_number = {self.current_turn_number}, current_player_index = {self.current_player_index}")
        self.current_player.is_active = False
        
        # Determine the next player based on the specified order
        human_players = [i for i, p in enumerate(self.players) if not p.is_bot()]
        bot_players = [i for i, p in enumerate(self.players) if p.is_bot()]
        all_players = human_players + bot_players
        
        current_index = all_players.index(self.current_player_index)
        next_index = (current_index + 1) % len(all_players)
        self.current_player_index = all_players[next_index]
        
        self.current_player.is_active = True
        
        if next_index < current_index:  # We've gone through all players
            self.increment_turn()
        
        self.reset_turn_state()
        self.referee.set_game_state(GameStateEnum.NEXTUP_READYUP)
        print(f"After next_player: current_turn_number = {self.current_turn_number}, current_player_index = {self.current_player_index}")

    def increment_turn(self):
        print(f"Before increment_turn: current_turn_number = {self.current_turn_number}")
        self.current_turn_number += 1
        for player in self.players:
            if self.current_turn_number - 1 not in player.turn_scores:
                player.record_turn(self.current_turn_number - 1, 0, 0, 0)  # Record an empty turn if not already recorded
        print(f"After increment_turn: current_turn_number = {self.current_turn_number}")

    def reset_turn_state(self):
        self.turn_started = False
        self.turn_banked = False
        self.bust_state = False
        self.busted_player = None
        self.busted_lost_score = 0
        self.dice_values = []
        self.selected_dice = []
        self.current_player.reset_turn()
        self.total_turns += 1
        self.real_time_counters.reset()
        self.ui.use_start_turn_button = True

    def reset_full_stashes_moved(self):
        self.current_player.full_stashes_moved = 0

    def bank_points(self):
        total_score = self.referee.calculate_turn_score()
        stash_stash_points, full_stashes_moved = self.referee.get_stash_stash_info()
        self.current_player.record_turn(self.current_turn_number, total_score, self.current_player.roll_count, self.current_player.full_stashes_moved_this_turn)
        self.add_log_entry(f"{self.current_player.user.username} BANKED {total_score} POINTS (Stash Stash: {stash_stash_points}, Full stashes: {self.current_player.full_stashes_moved_this_turn})")
        self.turn_banked = True
        self.referee.set_game_state(GameStateEnum.BANKED_TURN_SUMMARY)
        self.real_time_counters.update_counters(self)
        self.current_player.stash_stash = 0  # Reset stash_stash after banking
        
    def bust(self):
        self.bust_state = True
        self.busted_player = self.current_player
        self.busted_lost_score = self.referee.calculate_turn_score()
        self.current_player.record_turn(self.current_turn_number, 0, self.current_player.roll_count, 0)
        self.add_log_entry(f"{self.current_player.user.username} busted and lost {self.busted_lost_score} points")
        self.referee.set_game_state(GameStateEnum.BUST_TURN_SUMMARY)
        self.reset_full_stashes_moved()  # Add this line
        self.real_time_counters.update_counters(self)

    def roll_dice(self):
        self.turn_started = True
        self.current_player.roll_count += 1
        self.current_player.stashed_dice_this_roll = False  # Reset this flag on each new roll
        
        if self.current_game_state == GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL:
            remaining_dice = LiveDiceFRules.MAX_DICE
        else:
            remaining_dice = LiveDiceFRules.MAX_DICE - len(self.current_player.stashed_dice)
        
        self.dice_values = [LiveDiceFRules.roll_die() for _ in range(remaining_dice)]
        
        self.selected_dice = []
        
        self.current_stashable_combinations = self.referee.get_scoring_combinations(self.dice_values)
        self.current_stashable_dice = self.referee.get_stashable_dice(self.dice_values)
        
        formatted_dice = self.format_dice_for_log(' '.join([f'[{v}{"g" if i in self.current_stashable_dice else "w"}]' for i, v in enumerate(self.dice_values)]))
        self.add_log_entry(f"{self.current_player.user.username} ROLLED: {formatted_dice}")
        
        if self.current_stashable_dice:
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS)
        else:
            self.bust()
        
        self.real_time_counters.update_counters(self)

        return self.dice_values

    def select_dice(self, dice_index: int):
        if self.referee.can_select_dice(dice_index):
            if dice_index in self.selected_dice:
                self.selected_dice.remove(dice_index)
            else:
                self.selected_dice.append(dice_index)
        self.real_time_counters.update_counters(self)
        self.update_selection_state()

    def update_selection_state(self):
        stashable_dice = self.referee.get_stashable_dice(self.dice_values)
        if len(self.selected_dice) == len(stashable_dice):
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_FULL)
        elif self.selected_dice:
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL)
        else:
            if self.current_player.stashed_dice_this_roll:
                self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED_CURRENTROLL)
            elif self.current_player.stashed_dice:
                self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED)
            else:
                self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH)

    def stash_dice(self, dice_indices: List[int]):
        if not dice_indices:
            return

        stashed_values = [self.dice_values[i] for i in dice_indices]
        
        dice_indices.sort(reverse=True)
        
        total_stash_score = 0
        stashed_combinations = []

        while stashed_values:
            best_combination = max(self.referee.get_scoring_combinations(stashed_values), key=lambda x: x[1])
            combination_name, combination_score = best_combination
            
            combination_dice = self.referee.get_dice_for_combination(stashed_values, combination_name)
            
            self.current_player.add_to_stash(combination_dice, combination_score)
            total_stash_score += combination_score
            stashed_combinations.append((combination_name, combination_score))
            
            for die in combination_dice:
                stashed_values.remove(die)

        for index in sorted(dice_indices, reverse=True):
            del self.dice_values[index]

        self.selected_dice = []
        
        stash_log = " ".join([f"{name} for {score} POINTS" for name, score in stashed_combinations])
        formatted_stashed = self.format_dice_for_log(' '.join([f'[{v}g]' for v in stashed_values]))
        self.add_log_entry(f"{self.current_player.user.username} STASHED: {formatted_stashed}. {stash_log}. TOTAL: {total_stash_score} POINTS")
        
        self.current_player.stashed_dice_this_roll = True
        self.real_time_counters.update_counters(self)
        self.update_stash_state()
        self.ui.game_board.update_dice_positions(dice_indices)

        if self.ui.use_start_turn_button:
            self.ui.use_start_turn_button = False
           
    def update_stash_state(self):
        stashable_dice = self.referee.get_stashable_dice(self.dice_values)
        if not stashable_dice:
            if self.dice_values:
                self.referee.set_game_state(GameStateEnum.STASHCHOICE_STASHED_ALL)
            else:
                self.referee.set_game_state(GameStateEnum.STASHCHOICE_STASHED_FULL)
        elif len(stashable_dice) == len(self.dice_values):
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_FULL)
        elif self.selected_dice:
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL)
        elif self.current_player.stashed_dice:
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED)
        else:
            self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS)

    def start_new_stash(self):
        stash_points = self.referee.calculate_stash_score()
        self.current_player.stash_stash += stash_points
        self.current_player.full_stashes_moved_this_turn += 1
        self.current_player.stashed_dice = []
        self.current_player.stashed_dice_scores = []
        self.current_player.stashes_this_turn = 0
        self.current_player.stash_level += 1
        self.add_log_entry(f"{self.current_player.user.username} started a new stash, moving {stash_points} points to stash stash")
        self.referee.set_game_state(GameStateEnum.STASHCHOICE_STASHED_FULL_READY_TO_ROLL)
        self.real_time_counters.update_counters(self)

    def set_active_task(self, task: str):
        self.active_task = task

    def check_game_over(self) -> bool:
        return self.referee.is_game_over()

    def check_ui_update(self):
        if self.ui_needs_update:
            self.ui_needs_update = False
            return True
        return False

    def get_winner(self) -> Optional[Player]:
        if self.check_game_over():
            return max(self.players, key=lambda p: p.get_total_score())
        return None

    def get_game_turns(self):
        return max(player.turn_count for player in self.players) if self.players else 0

    def calculate_table_score(self) -> int:
        return self.referee.calculate_score(self.dice_values)

    def format_dice_for_snaptray(self, dice_values):
        formatted_dice = []
        for i, value in enumerate(dice_values):
            is_stashable = False
            for comb, _ in self.current_stashable_combinations:
                if comb.startswith("TRIPLE") and dice_values.count(value) >= 3:
                    is_stashable = True
                    break
                elif comb == "DOUBLE 6" and value == 6 and dice_values.count(6) >= 2:
                    is_stashable = True
                    break
                elif comb.startswith("SINGLE") and value in [1, 5]:
                    is_stashable = True
                    break
            formatted_dice.append(self.format_single_die(value, is_stashable))
        return formatted_dice

    def format_dice_for_stash(self, dice_values):
        return [self.format_single_die(value, True) for value in dice_values]

    def format_dice_for_log(self, entry):
        words = entry.split()
        formatted_words = []
        for word in words:
            if word.startswith("[") and word.endswith("]"):
                dice_value = word[1:-2]  # Remove the last character (g or w)
                if dice_value.isdigit() and 1 <= int(dice_value) <= 6:
                    is_stashable = word.endswith("g]")
                    formatted_words.append(self.format_single_die(int(dice_value), is_stashable))
                else:
                    formatted_words.append(word)
            else:
                formatted_words.append(word)
        return " ".join(formatted_words)

    def format_single_die(self, value, is_stashable):
        color = "green" if is_stashable else "white"
        return f"<dice>{color}_{value}</dice>"

    def add_log_entry(self, entry: str, prefix=None):
        if not entry.strip():  # Skip empty entries
            return

        if prefix is None:
            prefix = "@G-REF."
        
        formatted_entry = entry.upper()
        lines = formatted_entry.split('\n')
        
        for i, line in enumerate(lines):
            if i == 0:
                player_name = line.split()[0] if line.split() and line.split()[0].startswith("@") else ""
                if prefix != "@G-REF.":
                    log_entry = f'<prefix>{prefix}</prefix> {line}'
                elif player_name:
                    log_entry = f'<prefix>{prefix}</prefix> <player>{player_name}</player> {" ".join(line.split()[1:])}'
                else:
                    log_entry = f'<prefix>{prefix}</prefix> {line}'
            else:
                log_entry = line
            
            log_entry = log_entry.replace("<green>", "<greentext>").replace("</green>", "</greentext>")
            log_entry = log_entry.replace("<dice>", "<DICE>").replace("</dice>", "</DICE>")
            
            self.game_log.append(log_entry)
        
        if len(self.game_log) > 100:
            self.game_log = self.game_log[-100:]
        self.ui_needs_update = True
        if hasattr(self, 'ui') and self.ui:
            self.ui.scroll_log_to_bottom()

    def format_dice(self, dice_values):
        stashable_dice = self.referee.get_stashable_dice(dice_values)
        return ' '.join([f'<dice>{"green" if i in stashable_dice else "white"}_{v}</dice>' for i, v in enumerate(dice_values)])
    
    def handle_error(self, error_message: str):
        print(f"Error: {error_message}")
        self.add_log_entry(f"ERROR: {error_message}")
        # You might want to implement additional error handling logic here

    def validate_action(self, action: str) -> bool:
        if action == "ROLL":
            return self.referee.can_roll()
        elif action == "STASH":
            return self.referee.can_stash()
        elif action == "BANK":
            return self.referee.can_bank()
        elif action == "START_NEW_STASH":
            return self.referee.is_full_stash()
        else:
            return False

    def perform_action(self, action: str):
        if not self.validate_action(action):
            self.handle_error(f"Invalid action: {action}")
            return

        if action == "ROLL":
            self.roll_dice()
        elif action == "STASH":
            self.stash_dice(self.selected_dice)
        elif action == "BANK":
            self.bank_points()
        elif action == "START_NEW_STASH":
            self.start_new_stash()
        else:
            self.handle_error(f"Unknown action: {action}")

    def update_game_state(self):
        if self.is_game_over():
            self.referee.set_game_state(GameStateEnum.GAME_OVER)
        elif self.bust_state:
            self.referee.set_game_state(GameStateEnum.BUST_TURN_SUMMARY)
        elif self.turn_banked:
            self.referee.set_game_state(GameStateEnum.BANKED_TURN_SUMMARY)
        elif self.referee.is_full_stash():
            self.referee.set_game_state(GameStateEnum.STASHCHOICE_STASHED_FULL)
        elif len(self.dice_values) == 0 and self.referee.has_stashed_dice():
            self.referee.set_game_state(GameStateEnum.STASHCHOICE_STASHED_ALL)
        elif self.referee.get_stashable_dice(self.dice_values):
            if self.referee.has_stashed_dice():
                self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED)
            else:
                self.referee.set_game_state(GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS)
        else:
            self.referee.set_game_state(GameStateEnum.STASHCHOICE_STASHED_PARTIAL)

        self.real_time_counters.update_counters(self)

    def is_game_over(self) -> bool:
        return self.referee.is_game_over()