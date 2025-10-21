from typing import List, Tuple, Dict, Union
from enum import Enum, auto
import random

class GameStateEnum(Enum):
    START_TURN = auto()
    ROLLRESULT_POSITIVE_STASHOPTIONS = auto()
    ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED = auto()
    ROLLRESULT_POSITIVE_STASHSELECTION_FULL = auto()
    ROLLRESULT_POSITIVE_STASHSELECTION_PARTIAL = auto()
    STASHCHOICE_STASHED_ALL = auto()
    STASHCHOICE_STASHED_FULL = auto()
    STASHCHOICE_STASHED_PARTIAL = auto()
    STASHCHOICE_STASHED_FULL_READY_TO_ROLL = auto()
    BANKED_TURN_SUMMARY = auto()
    BUST_TURN_SUMMARY = auto()
    NEXTUP_READYUP = auto()
    NEW_STASH = auto()
    ROLLRESULT_POSITIVE_STASHOPTIONS_NOSTASH = auto()
    ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED_CURRENTROLL = auto()
    END_GAME_SUMMARY = auto()

class LiveDiceFRules:
    TARGET_SCORE = 4000  # This will be displayed as 4OOO in the UI
    MAX_DICE = 6

    @staticmethod
    def roll_die() -> int:
        return random.randint(1, 6)

    @staticmethod
    def get_scoring_rules() -> List[Dict[str, int]]:
        return [
            {"TRIPLE 1": 1000},
            {"TRIPLE 2": 200},
            {"TRIPLE 3": 300},
            {"TRIPLE 4": 400},
            {"TRIPLE 5": 500},
            {"TRIPLE 6": 600},
            {"SINGLE 1": 100},
            {"SINGLE 5": 50},
            {"DOUBLE 6": 100}
        ]

    @staticmethod
    def calculate_score(dice_values: Union[List[int], int], stashed_together: bool = False, ruleset: str = "STANDARD") -> int:
        """
        Calculate score for given dice values.
        
        Args:
            dice_values: Single die or list of dice values
            stashed_together: If True, assumes dice are being stashed as a group
            ruleset: Game ruleset - "SIMPLE", "STANDARD", or "ADVANCED"
            
        Returns:
            Total score
        """
        if isinstance(dice_values, int):
            dice_values = [dice_values]
        
        score = 0
        counts = [dice_values.count(i) for i in range(1, 7)]
        
        # SIMPLE MODE: Only 1s and 5s score points
        if ruleset == "SIMPLE":
            score += counts[0] * 100  # 1s
            score += counts[4] * 50   # 5s
            return score
        
        # STANDARD and ADVANCED modes: Full scoring rules
        # Check for triples
        for i, count in enumerate(counts):
            if count >= 3:
                score += 1000 if i == 0 else (i + 1) * 100
                counts[i] -= 3
                if stashed_together:
                    return score  # Return immediately for triples when stashed together
        
        # Check for double 6
        if counts[5] >= 2:
            score += 100
            counts[5] -= 2
            if stashed_together:
                return score  # Return immediately for double 6 when stashed together
        
        # Add remaining 1s and 5s
        score += counts[0] * 100  # Remaining 1s
        score += counts[4] * 50   # Remaining 5s
        
        return score

    @staticmethod
    def get_scoring_combinations(dice_values: List[int], ruleset: str = "STANDARD") -> List[Tuple[str, int]]:
        """
        Get all scoring combinations in the dice.
        
        Args:
            dice_values: List of dice values
            ruleset: Game ruleset - "SIMPLE", "STANDARD", or "ADVANCED"
            
        Returns:
            List of tuples (combination_name, score)
        """
        counts = [dice_values.count(i) for i in range(1, 7)]
        combinations = []

        # SIMPLE MODE: Only 1s and 5s
        if ruleset == "SIMPLE":
            if counts[0] > 0:
                combinations.append((f"SINGLE 1{'s' if counts[0] > 1 else ''}", counts[0] * 100))
            if counts[4] > 0:
                combinations.append((f"SINGLE 5{'s' if counts[4] > 1 else ''}", counts[4] * 50))
            return combinations

        # STANDARD and ADVANCED modes: Full scoring
        # Check for triples
        for i, count in enumerate(counts):
            if count >= 3:
                combinations.append((f"TRIPLE {i+1}", 1000 if i == 0 else (i+1) * 100))

        # Check for double 6
        if counts[5] >= 2:
            combinations.append(("DOUBLE 6", 100))

        # Check for single 1s and 5s
        if counts[0] > 0:
            combinations.append((f"SINGLE 1{'s' if counts[0] > 1 else ''}", counts[0] * 100))
        if counts[4] > 0:
            combinations.append((f"SINGLE 5{'s' if counts[4] > 1 else ''}", counts[4] * 50))

        return combinations

    @staticmethod
    def get_stashable_dice(dice_values: List[int], ruleset: str = "STANDARD") -> List[int]:
        """
        Get indices of stashable dice.
        
        Args:
            dice_values: List of dice values
            ruleset: Game ruleset - "SIMPLE", "STANDARD", or "ADVANCED"
            
        Returns:
            List of indices of stashable dice
        """
        stashable = []
        counts = [dice_values.count(i) for i in range(1, 7)]
        
        # SIMPLE MODE: Only 1s and 5s are stashable
        if ruleset == "SIMPLE":
            # Only add 1s and 5s
            stashable.extend([j for j, v in enumerate(dice_values) if v == 1])  # 1's
            stashable.extend([j for j, v in enumerate(dice_values) if v == 5])  # 5's
            return sorted(list(set(stashable)))
        
        # STANDARD and ADVANCED modes: Full stashing rules
        for i, count in enumerate(counts):
            if count >= 3:
                stashable.extend([j for j, v in enumerate(dice_values) if v == i + 1][:3])
            elif i == 0 or i == 4:  # 1's and 5's
                stashable.extend([j for j, v in enumerate(dice_values) if v == i + 1])
            elif i == 5 and count >= 2:  # Double 6
                stashable.extend([j for j, v in enumerate(dice_values) if v == 6][:2])
        
        return sorted(list(set(stashable)))  # Remove duplicates and sort

    @staticmethod
    def is_scoring_dice(dice: List[int]) -> bool:
        if len(dice) == 1:
            return dice[0] in [1, 5]
        elif len(dice) == 2:
            return dice[0] == dice[1] == 6
        elif len(dice) == 3:
            return len(set(dice)) == 1
        return False

    @staticmethod
    def describe_stash(stashed: List[int]) -> str:
        counts = [stashed.count(i) for i in range(1, 7)]
        descriptions = []
        
        for i in range(6):
            if counts[i] >= 3:
                descriptions.append(f"Triple {i+1}")
                counts[i] -= 3
        
        if counts[5] >= 2:
            descriptions.append("Double 6")
            counts[5] -= 2
        
        for i in [0, 4]:  # Check for remaining 1s and 5s
            if counts[i] > 0:
                descriptions.append(f"{counts[i]} {i+1}{'s' if counts[i] > 1 else ''}")
        
        return " and ".join(descriptions)

    @staticmethod
    def get_stash_number(stash_level: int) -> str:
        if stash_level == 1:
            return "1st"
        elif stash_level == 2:
            return "2nd"
        elif stash_level == 3:
            return "3rd"
        else:
            return f"{stash_level}th"

    @staticmethod
    def can_roll_again(has_stashed_this_turn: bool) -> bool:
        return has_stashed_this_turn

    @staticmethod
    def is_bust(dice_values: List[int], ruleset: str = "STANDARD") -> bool:
        """Check if dice roll is a bust (no scoring dice)"""
        return len(LiveDiceFRules.get_stashable_dice(dice_values, ruleset)) == 0

    @staticmethod
    def can_bank(has_stashed_this_turn: bool, virtual_score: int) -> bool:
        return has_stashed_this_turn and virtual_score > 0

    @staticmethod
    def can_stash(selected_dice: List[int]) -> bool:
        return len(selected_dice) > 0

    @staticmethod
    def is_full_stash(stashed_dice: List[int]) -> bool:
        return len(stashed_dice) == LiveDiceFRules.MAX_DICE

    @staticmethod
    def is_turn_over(is_bust: bool, is_banked: bool) -> bool:
        return is_bust or is_banked

    @staticmethod
    def should_start_new_turn(dice_values: List[int], stashed_dice: List[int], turn_started: bool) -> bool:
        return not turn_started or (len(dice_values) == 0 and len(stashed_dice) == 0)

    @staticmethod
    def is_game_over(player_scores: List[int], endgoal: int = 4000) -> bool:
        """Check if game is over (any player reached endgoal)"""
        return any(score >= endgoal for score in player_scores)

    @staticmethod
    def get_dice_for_combination(dice_values: List[int], combination_name: str) -> List[int]:
        if combination_name.startswith("TRIPLE"):
            value = int(combination_name.split()[-1])
            return [value] * 3
        elif combination_name == "DOUBLE 6":
            return [6, 6]
        elif combination_name.startswith("SINGLE"):
            value = int(combination_name.split()[-1].rstrip('s'))
            count = dice_values.count(value)
            return [value] * count
        return []
    
    @staticmethod
    def can_roll_without_stashing(game_state) -> bool:
        return (
            not game_state.turn_started or  # First roll of the turn
            (game_state.current_game_state == GameStateEnum.NEW_STASH and 
            len(game_state.current_player.stashed_dice) == 0)  # Just moved a full stash to stash stash
        )

    @staticmethod
    def can_roll(game_state) -> bool:
        return (
            LiveDiceFRules.can_roll_without_stashing(game_state) or
            (len(game_state.current_player.stashed_dice) > 0 and 
            len(game_state.dice_values) == 0 and
            game_state.current_game_state in [
                GameStateEnum.STASHCHOICE_STASHED_ALL,
                GameStateEnum.STASHCHOICE_STASHED_PARTIAL,
                GameStateEnum.ROLLRESULT_POSITIVE_STASHOPTIONS_HAVESTASHED
            ])
        )

    @staticmethod
    def can_roll_six_dice(turn_started: bool, stashed_dice: List[int], roll_count: int) -> bool:
        return (not turn_started and roll_count == 0) or (len(stashed_dice) == 0 and roll_count == 0)
