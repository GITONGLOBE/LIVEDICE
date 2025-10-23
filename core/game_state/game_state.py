from typing import List, Optional
import re
from core.account.user import User
from core.game_engine.game_referee import GameReferee
from core.messaging import MessageManager
from core.game_state.real_time_score_counters import RealTimeScoreCounters
from games.livedice_f.livedice_f_rules import LiveDiceFRules, GameStateEnum

class Player:
    def __init__(self, user: User, player_number: int, game_state_manager):
        self.user = user
        self.player_number = player_number
        self.game_state_manager = game_state_manager
        self.turn_scores = {}
        self.stashed_dice = []
        self.stashed_dice_scores = []
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

    def record_turn(self, turn_number: int, banked_score: int, rolls: int, full_stashes_moved: int):
        # FIXED: Use player's own turn_count + 1 for recording
        player_turn = self.turn_count + 1
        self.turn_scores[player_turn] = {
            "SCORE": banked_score,
            "ROLLS": rolls,
            "STASHES": full_stashes_moved
        }
        self.turn_count += 1
        self.banked_full_stashes += full_stashes_moved
        self.full_stashes_moved_this_turn = 0
        self.game_state_manager.add_log_entry(f"{self.user.username} recorded turn {self.game_state_manager.format_number(player_turn)}: Score: {self.game_state_manager.format_number(banked_score)}, Rolls: {self.game_state_manager.format_number(rolls)}, Stashes: {self.game_state_manager.format_number(full_stashes_moved)}")

    def get_total_banked_full_stashes(self) -> int:
        return self.banked_full_stashes

    def move_stash_to_stash_stash(self):
        self.full_stashes_moved_this_turn += 1

    def get_total_score(self) -> int:
        return sum(turn["SCORE"] for turn in self.turn_scores.values())

    def get_stash_score(self) -> int:
        return sum(self.stashed_dice_scores)

    def add_to_stash(self, dice, score):
        self.stashed_dice.extend(dice)
        self.stashed_dice_scores.append(score)
        self.stashes_this_turn += 1

    def get_turn_score(self, turn_number: int):
        return self.turn_scores.get(turn_number, {"SCORE": 0, "ROLLS": 0, "STASHES": 0})

    def is_bot(self) -> bool:
        # FIXED: Check for new bot naming format with difficulty prefix
        # Supports: EASY-GO-BOT-1, NORMAL-GO-BOT-2, HARD-GO-BOT-3, etc.
        return "GO-BOT" in self.user.username or self.user.username.startswith("@")

    def reset_turn(self):
        self.stashed_dice = []
        self.stashed_dice_scores = []
        self.stash_stash = 0
        self.full_stashes_moved = 0
        self.stashes_this_turn = 0
        self.stash_level = 1
        self.roll_count = 0
        self.full_stashes_moved_this_turn = 0
        self.stashed_dice_this_roll = False
        
class GameStateManager:
    def __init__(self, ui, human_players, ai_players, endgoal=4000, ruleset="STANDARD", bot_difficulty="NORMAL"):
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
        
        # Initialize messaging system
        self.message_manager = MessageManager()
        
        # Store game configuration (ensure endgoal is integer)
        self.endgoal = int(endgoal) if endgoal else 4000
        self.ruleset = ruleset if ruleset else "STANDARD"
        self.bot_difficulty = bot_difficulty if bot_difficulty else "NORMAL"
        
        self.referee = GameReferee(self)
        self.real_time_counters = RealTimeScoreCounters()
        self.current_game_state = GameStateEnum.START_TURN
        self.current_stashable_dice = []
        self.current_stashable_combinations = []
        self.current_turn_number = 1
        self.ui_needs_update = False
        self.can_roll_once = False

        # Add human players
        for i in range(human_players):
            self.add_player(User(f"@VIDEO-GAMER-{i+1}", f"videogamer{i+1}@example.com", "password"))

        # FIXED: Add AI players with difficulty prefix
        for i in range(ai_players):
            # Bot names now include difficulty: EASY-GO-BOT-1, NORMAL-GO-BOT-2, HARD-GO-BOT-3
            username = f"@{self.bot_difficulty.upper()}-GO-BOT-{i+1}"
            self.add_player(User(username, f"gobot{i+1}@example.com", "password"))

        self.determine_starting_player()
        self.set_active_task("Click START TURN to begin your turn")

    def determine_starting_player(self):
        # Start with the first human player, if any
        human_players = [p for p in self.players if not p.is_bot()]
        bot_players = [p for p in self.players if p.is_bot()]
        
        if human_players:
            self.current_player_index = self.players.index(human_players[0])
        else:
            self.current_player_index = 0

        self.current_player.is_active = True

    def add_player(self, user: User):
        player = Player(user, len(self.players) + 1, self)
        self.players.append(player)

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def next_player(self):
        self.current_player.is_active = False
        self.current_player.reset_turn()
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player.is_active = True
        self.current_turn_number += 1
        self.turn_started = False
        self.turn_banked = False
        self.bust_state = False
        self.busted_player = None
        self.busted_lost_score = 0
        self.can_roll_once = False
        # FIXED: Update counters so new player's turn number shows immediately
        self.real_time_counters.update_counters(self)

    def set_active_task(self, task: str):
        self.active_task = task

    def format_dice_for_log(self, dice_str: str) -> str:
        import re
        pattern = r'\[(\d+)([gw])\]'
        def replace(match):
            value = match.group(1)
            color = 'green' if match.group(2) == 'g' else 'white'
            return f'<DICE>{color}_{value}</DICE>'
        return re.sub(pattern, replace, dice_str)

    def add_log_entry(self, entry: str, prefix: str = None):
        """Legacy method - kept for backward compatibility. New code should use message_manager."""
        if prefix:
            formatted_entry = f"{prefix}: {entry}"
        else:
            formatted_entry = entry
        formatted_entry = self.format_dice_for_log(formatted_entry)
        self.game_log.append(formatted_entry)
        
        # ALSO add to message_manager for new system
        if prefix and "GO-BOT" in prefix:
            # Bot message
            self.message_manager.add_bot_thinking(prefix, entry)
        elif prefix == "@G-REF." or prefix == "@G-REF":
            # G-REF message
            self.message_manager.add_gref_official_statement(entry)
        else:
            # Generic message - add as G-REF
            self.message_manager.add_gref_official_statement(formatted_entry)
        
        if self.ui:
            self.ui.events.scroll_log_to_bottom()

    def format_number(self, number: int) -> str:
        return str(number).replace('0', 'O')

    def format_dice(self, dice_values: List[int]) -> str:
        formatted = []
        for value in dice_values:
            formatted.append(f'<DICE>green_{value}</DICE>')
        return ' '.join(formatted)

    def reset_full_stashes_moved(self):
        self.current_player.full_stashes_moved = 0
        self.current_player.full_stashes_moved_this_turn = 0

    def bust(self):
        self.bust_state = True
        self.busted_player = self.current_player
        self.busted_lost_score = self.referee.calculate_turn_score()
        self.current_player.record_turn(self.current_player.turn_count + 1, 0, self.current_player.roll_count, 0)
        self.add_log_entry(f"{self.current_player.user.username} busted and lost {self.format_number(self.busted_lost_score)} points")
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
        
        # CRITICAL: Pass ruleset to get_scoring_combinations and get_stashable_dice
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

    def format_dice_for_snaptray(self, dice_values):
        formatted_dice = []
        for i, value in enumerate(dice_values):
            is_stashable = False
            for comb, _ in self.current_stashable_combinations:
                if comb.startswith("TRIPLE") and dice_values.count(value) >= 3:
                    is_stashable = True
                    break
                elif comb == "DOUBLE 6" and value == 6:
                    is_stashable = True
                    break
                elif comb.startswith("SINGLE 1") and value == 1:
                    is_stashable = True
                    break
                elif comb.startswith("SINGLE 5") and value == 5:
                    is_stashable = True
                    break
            
            color = "green" if is_stashable else "white"
            formatted_dice.append(f"{color}_{value}")
        
        return formatted_dice
