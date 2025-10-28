"""
POPUP MESSAGES MODULE
Generates dynamic, situational popup messages with variations.
Provides rich context-aware messaging for game popups.
"""

import random
from typing import List, Tuple, Optional, Dict


class PopupMessageGenerator:
    """Generates popup messages with variations based on game situation"""
    
    def __init__(self, game_state):
        """
        Initialize message generator.
        
        Args:
            game_state: GameStateManager instance
        """
        self.game_state = game_state
    
    def _format_number(self, number: int) -> str:
        """Format number with O instead of 0"""
        return str(number).replace('0', 'O')
    
    def _get_ordinal(self, n: int) -> str:
        """Convert number to ordinal (1ST, 2ND, 3RD, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'TH'
        else:
            suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(n % 10, 'TH')
        return f"{n}{suffix}"
    
    def get_leaderboard_info(self) -> Dict:
        """
        Get comprehensive leaderboard information.
        
        Returns:
            Dict with ranking, scores, and position info
        """
        current_player = self.game_state.current_player
        current_score = current_player.get_total_score()
        virtual_score = self.game_state.referee.calculate_total_score()
        
        # Get all player scores
        player_scores = []
        for player in self.game_state.players:
            if player == current_player:
                # Use virtual score for current player
                player_scores.append((player, virtual_score))
            else:
                player_scores.append((player, player.get_total_score()))
        
        # Sort by score (highest first)
        player_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Find current player's position
        current_position = next(i for i, (p, s) in enumerate(player_scores) if p == current_player) + 1
        
        # Find who's ahead (if anyone)
        ahead_player = None
        points_behind = 0
        if current_position > 1:
            ahead_player, ahead_score = player_scores[current_position - 2]
            points_behind = ahead_score - virtual_score
        
        # Find who's behind (if anyone)
        behind_player = None
        points_ahead_of_behind = 0
        if current_position < len(player_scores):
            behind_player, behind_score = player_scores[current_position]
            points_ahead_of_behind = virtual_score - behind_score
        
        # Distance to goal
        points_to_goal = self.game_state.endgoal - virtual_score
        
        return {
            "position": current_position,
            "total_players": len(player_scores),
            "current_score": current_score,
            "virtual_score": virtual_score,
            "ahead_player": ahead_player,
            "points_behind": points_behind,
            "behind_player": behind_player,
            "points_ahead_of_behind": points_ahead_of_behind,
            "points_to_goal": points_to_goal,
            "in_first": current_position == 1,
            "in_last": current_position == len(player_scores)
        }
    
    def generate_ready_up_messages(self) -> List[str]:
        """
        Generate ready up popup messages with variations.
        
        Returns:
            List of message lines (player name will be handled separately)
        """
        info = self.get_leaderboard_info()
        player_name = self.game_state.current_player.user.username
        
        messages = []
        
        # Line 1: "GET READY @PLAYERNAME" or "IT'S YOUR TURN"
        greetings = [
            f"GET READY {player_name}",
            f"IT'S YOUR TURN",
            f"YOUR TURN {player_name}",
            f"TIME TO ROLL {player_name}"
        ]
        messages.append(random.choice(greetings))
        
        # Line 2: Always show position
        position_text = f"YOU ARE CURRENTLY PLACED {self._get_ordinal(info['position'])}"
        messages.append(position_text)
        
        # Line 3: Situational message
        situational = self._get_ready_up_situational_message(info, player_name)
        if situational:
            messages.append(situational)
        
        # Line 4: Encouragement
        encouragement = self._get_ready_up_encouragement(info)
        messages.append(encouragement)
        
        return messages
    
    def _get_ready_up_situational_message(self, info: Dict, player_name: str) -> Optional[str]:
        """Generate situational message for ready up popup"""
        # Close to winning (less than 500 points away)
        if 0 < info["points_to_goal"] < 500:
            variations = [
                f"ONLY {self._format_number(info['points_to_goal'])} POINTS FROM VICTORY!",
                f"SO CLOSE! JUST {self._format_number(info['points_to_goal'])} POINTS TO WIN!",
                f"ALMOST THERE! {self._format_number(info['points_to_goal'])} POINTS NEEDED!"
            ]
            return random.choice(variations)
        
        # Not in first place - show points needed to move up
        if not info["in_first"] and info["points_behind"] > 0:
            ahead_name = info["ahead_player"].user.username if info["ahead_player"] else "LEADER"
            variations = [
                f"BANK {self._format_number(info['points_behind'] + 1)} POINTS TO TAKE {self._get_ordinal(info['position'] - 1)} PLACE",
                f"{self._format_number(info['points_behind'] + 1)} POINTS NEEDED TO MOVE UP TO {self._get_ordinal(info['position'] - 1)}",
                f"PASS {ahead_name} WITH {self._format_number(info['points_behind'] + 1)} POINTS"
            ]
            return random.choice(variations)
        
        # In first but someone close behind (less than 200 points)
        if info["in_first"] and info["behind_player"] and info["points_ahead_of_behind"] < 200:
            behind_name = info["behind_player"].user.username
            variations = [
                f"HEADS UP! {behind_name} IS ONLY {self._format_number(info['points_ahead_of_behind'])} POINTS BEHIND",
                f"WATCH OUT FOR {behind_name}! ONLY {self._format_number(info['points_ahead_of_behind'])} POINTS BACK",
                f"{behind_name} IS BREATHING DOWN YOUR NECK AT {self._format_number(info['points_ahead_of_behind'])} POINTS BEHIND"
            ]
            return random.choice(variations)
        
        return None
    
    def _get_ready_up_encouragement(self, info: Dict) -> str:
        """Generate encouragement message for ready up popup"""
        if info["in_first"]:
            messages = [
                "GO FOR IT! STAY IN THE LEAD!",
                "KEEP YOUR LEAD! YOU GOT THIS!",
                "MAINTAIN YOUR POSITION!",
                "DON'T LET THEM CATCH UP!"
            ]
        elif info["position"] == 2:
            messages = [
                "GO FOR IT! TAKE THE LEAD!",
                "TIME TO TAKE 1ST PLACE!",
                "TAKE DOWN THE LEADER!",
                "GO FOR THE TOP SPOT!"
            ]
        else:
            messages = [
                "GO FOR IT! MOVE UP THE RANKS!",
                "TIME TO CLIMB THE LEADERBOARD!",
                "PUSH FORWARD! YOU CAN DO IT!",
                "MAKE YOUR MOVE!"
            ]
        
        return random.choice(messages)
    
    def generate_banked_messages(self) -> List[str]:
        """
        Generate banked popup messages with variations.
        
        Returns:
            List of message lines
        """
        info = self.get_leaderboard_info()
        player_name = self.game_state.current_player.user.username
        banked_points = self.game_state.referee.calculate_turn_score()
        
        messages = []
        
        # Line 1: Celebration
        celebrations = [
            "NICE GOING!",
            "WELL DONE!",
            "GREAT SCORE!",
            "EXCELLENT!",
            "NICE ONE!"
        ]
        messages.append(random.choice(celebrations))
        
        # Line 2: Player name
        messages.append(player_name)
        
        # Line 3: Banking action with position
        position_text = f"BANKED {self._format_number(banked_points)} POINTS IN {self._get_ordinal(info['position'])} PLACE"
        messages.append(position_text)
        
        # Line 4: Total points variation
        total_variations = [
            f"TOTALLING {self._format_number(info['virtual_score'])} POINTS",
            f"GETTING THEIR TOTAL UP TO {self._format_number(info['virtual_score'])} POINTS",
            f"RESULTING IN A TOTAL OF {self._format_number(info['virtual_score'])} POINTS",
            f"NOW AT {self._format_number(info['virtual_score'])} POINTS TOTAL",
            f"BRINGING TOTAL TO {self._format_number(info['virtual_score'])} POINTS"
        ]
        messages.append(random.choice(total_variations))
        
        # Line 5: Situational message (if moved up or other significant event)
        situational = self._get_banked_situational_message(info, banked_points)
        if situational:
            messages.append(situational)
        
        return messages
    
    def _get_banked_situational_message(self, info: Dict, banked_points: int) -> Optional[str]:
        """Generate situational message for banked popup"""
        # Check if player moved up in ranking
        old_score = info["current_score"]
        new_score = info["virtual_score"]
        
        # Calculate old position
        old_player_scores = []
        for player in self.game_state.players:
            if player == self.game_state.current_player:
                old_player_scores.append((player, old_score))
            else:
                old_player_scores.append((player, player.get_total_score()))
        
        old_player_scores.sort(key=lambda x: x[1], reverse=True)
        old_position = next(i for i, (p, s) in enumerate(old_player_scores) 
                           if p == self.game_state.current_player) + 1
        
        # Moved up in ranking
        if old_position > info["position"]:
            positions_moved = old_position - info["position"]
            if positions_moved == 1:
                variations = [
                    f"MOVED UP TO {self._get_ordinal(info['position'])} PLACE!",
                    f"CLIMBED TO {self._get_ordinal(info['position'])} POSITION!",
                    f"JUMPED TO {self._get_ordinal(info['position'])} PLACE!"
                ]
            else:
                variations = [
                    f"MOVED UP {positions_moved} PLACES TO {self._get_ordinal(info['position'])}!",
                    f"CLIMBED {positions_moved} POSITIONS TO {self._get_ordinal(info['position'])}!",
                    f"JUMPED {positions_moved} SPOTS TO {self._get_ordinal(info['position'])}!"
                ]
            return random.choice(variations)
        
        # Close to winning
        if 0 < info["points_to_goal"] < 500:
            variations = [
                f"ONLY {self._format_number(info['points_to_goal'])} POINTS FROM VICTORY!",
                f"SO CLOSE TO WINNING! {self._format_number(info['points_to_goal'])} POINTS LEFT!",
                f"ALMOST AT {self._format_number(self.game_state.endgoal)}! JUST {self._format_number(info['points_to_goal'])} MORE!"
            ]
            return random.choice(variations)
        
        return None
    
    def generate_bust_messages(self) -> List[str]:
        """
        Generate bust popup messages.
        
        Returns:
            List of message lines
        """
        player_name = self.game_state.current_player.user.username
        lost_points = self.game_state.referee.calculate_turn_score()
        
        messages = []
        
        # Line 1: Sympathy
        sympathies = [
            "UNLUCKY!",
            "TOO BAD!",
            "OH NO!",
            "TOUGH BREAK!",
            "THAT'S ROUGH!"
        ]
        messages.append(random.choice(sympathies))
        
        # Line 2: Player name
        messages.append(player_name)
        
        # Line 3: Bust announcement
        messages.append("THAT'S A BUST")
        
        # Line 4: Points lost
        messages.append(f"LOSING {self._format_number(lost_points)} POINTS")
        
        return messages
