"""
MESSAGE MANAGER MODULE
Manages message creation, triggering, and integration with game state.
Central hub for all messaging operations.
"""

from typing import List, Optional, Dict, Any
from .message_system import (
    Message,
    GREFMessage,
    BOTMessage,
    MessageType,
    GREFCategory,
    BOTCategory
)
from .bot_personalities import get_personality_for_bot


class MessageManager:
    """Manages all game messages"""
    
    def __init__(self):
        """Initialize message manager"""
        self.messages: List[Message] = []
        self.bot_personalities = {}  # Cache personalities by bot name
    
    def add_message(self, message: Message):
        """Add a message to the log"""
        self.messages.append(message)
    
    def get_all_messages(self) -> List[Message]:
        """Get all messages"""
        return self.messages
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get recent messages"""
        return self.messages[-count:]
    
    def clear_messages(self):
        """Clear all messages"""
        self.messages.clear()
        self.bot_personalities.clear()
    
    # =========================================================================
    # G-REF MESSAGE CREATION
    # =========================================================================
    
    def add_gref_turn_start(self, player_name: str, turn_number: int):
        """G-REF announces turn start"""
        content = f"IT'S {player_name}'S TURN"
        context = {
            "player": player_name,
            "turn": turn_number
        }
        message = GREFMessage(content, GREFCategory.TURN_START, context)
        self.add_message(message)
        return message
    
    def add_gref_turn_end(self, player_name: str):
        """G-REF announces turn end"""
        content = f"{player_name} ENDED THEIR TURN"
        context = {"player": player_name}
        message = GREFMessage(content, GREFCategory.TURN_END, context)
        self.add_message(message)
        return message
    
    def add_gref_roll_result(self, player_name: str, dice_values: List[int]):
        """G-REF announces roll result"""
        dice_str = " ".join([f"[{val}]" for val in dice_values])
        content = f"{player_name} ROLLED {dice_str}"
        context = {
            "player": player_name,
            "dice": dice_values
        }
        message = GREFMessage(content, GREFCategory.ACTION_REPORT, context)
        self.add_message(message)
        return message
    
    def add_gref_stash_action(self, player_name: str, points: int, dice_count: int):
        """G-REF announces stash action"""
        content = f"{player_name} STASHED {dice_count} DICE FOR {points} POINTS"
        context = {
            "player": player_name,
            "points": points,
            "dice_count": dice_count
        }
        message = GREFMessage(content, GREFCategory.STASH_ACTION, context)
        self.add_message(message)
        return message
    
    def add_gref_bank_action(self, player_name: str, points: int):
        """G-REF announces bank action"""
        content = f"{player_name} BANKED {points} POINTS"
        context = {
            "player": player_name,
            "points": points
        }
        message = GREFMessage(content, GREFCategory.BANK_ACTION, context)
        self.add_message(message)
        return message
    
    def add_gref_bust(self, player_name: str, lost_points: int):
        """G-REF announces bust"""
        content = f"{player_name} BUSTED AND LOST {lost_points} POINTS"
        context = {
            "player": player_name,
            "lost_points": lost_points
        }
        message = GREFMessage(content, GREFCategory.BUST_EVENT, context)
        self.add_message(message)
        return message
    
    def add_gref_game_start(self, player_names: List[str]):
        """G-REF announces game start"""
        players = ", ".join(player_names)
        content = f"GAME START! PLAYERS: {players}"
        context = {"players": player_names}
        message = GREFMessage(content, GREFCategory.GAME_START, context)
        self.add_message(message)
        return message
    
    def add_gref_game_end(self, winner_name: str, winner_score: int):
        """G-REF announces game end"""
        content = f"GAME OVER! {winner_name} WINS WITH {winner_score} POINTS!"
        context = {
            "winner": winner_name,
            "score": winner_score
        }
        message = GREFMessage(content, GREFCategory.GAME_END, context)
        self.add_message(message)
        return message
    
    def add_gref_ready_confirmation(self, player_name: str, turn_number: int):
        """G-REF confirms player is ready"""
        content = f"{player_name} CONFIRMED THEY ARE READY TO START THEIR {self._ordinal(turn_number)} TURN"
        context = {
            "player": player_name,
            "turn": turn_number
        }
        message = GREFMessage(content, GREFCategory.ACTION_REPORT, context)
        self.add_message(message)
        return message
    
    def add_gref_official_statement(self, statement: str, context: Optional[Dict[str, Any]] = None):
        """G-REF makes an official statement"""
        message = GREFMessage(statement, GREFCategory.OFFICIAL, context)
        self.add_message(message)
        return message
    
    # =========================================================================
    # BOT MESSAGE CREATION
    # =========================================================================
    
    def _get_bot_personality(self, bot_name: str):
        """Get or create bot personality"""
        if bot_name not in self.bot_personalities:
            self.bot_personalities[bot_name] = get_personality_for_bot(bot_name)
        return self.bot_personalities[bot_name]
    
    def add_bot_reaction(self, bot_name: str, situation: str, context: Optional[Dict[str, Any]] = None):
        """Bot reacts to a situation"""
        personality = self._get_bot_personality(bot_name)
        content = personality.get_message(situation, context)
        
        if content:  # Only add if personality has a message
            message = BOTMessage(
                bot_name=bot_name,
                content=content,
                category=BOTCategory.REACTION,
                personality_name=personality.name,
                game_context=context
            )
            self.add_message(message)
            return message
        return None
    
    def add_bot_strategy_explanation(self, bot_name: str, action: str, reasoning: str, context: Optional[Dict[str, Any]] = None):
        """Bot explains their strategy"""
        personality = self._get_bot_personality(bot_name)
        
        # Get personality-specific phrasing if available
        situation_key = f"{action.lower()}_decision"
        personality_content = personality.get_message(situation_key, context)
        
        if personality_content:
            content = personality_content
        else:
            content = reasoning  # Fallback to generic reasoning
        
        message = BOTMessage(
            bot_name=bot_name,
            content=content,
            category=BOTCategory.STRATEGY,
            personality_name=personality.name,
            game_context=context
        )
        self.add_message(message)
        return message
    
    def add_bot_thinking(self, bot_name: str, thought: str, context: Optional[Dict[str, Any]] = None):
        """Bot shares their thinking process"""
        personality = self._get_bot_personality(bot_name)
        
        message = BOTMessage(
            bot_name=bot_name,
            content=thought,
            category=BOTCategory.THINKING,
            personality_name=personality.name,
            game_context=context
        )
        self.add_message(message)
        return message
    
    def add_bot_celebration(self, bot_name: str, context: Optional[Dict[str, Any]] = None):
        """Bot celebrates"""
        return self.add_bot_reaction(bot_name, "win", context)
    
    def add_bot_frustration(self, bot_name: str, context: Optional[Dict[str, Any]] = None):
        """Bot expresses frustration"""
        return self.add_bot_reaction(bot_name, "bust", context)
    
    def add_bot_turn_start_message(self, bot_name: str, context: Optional[Dict[str, Any]] = None):
        """Bot announces their turn starting"""
        return self.add_bot_reaction(bot_name, "turn_start", context)
    
    def add_bot_game_start_message(self, bot_name: str, context: Optional[Dict[str, Any]] = None):
        """Bot message at game start"""
        return self.add_bot_reaction(bot_name, "game_start", context)
    
    def add_bot_opponent_roll_reaction(self, bot_name: str, opponent_name: str, is_good_roll: bool, context: Optional[Dict[str, Any]] = None):
        """Bot reacts to opponent's roll"""
        if context is None:
            context = {}
        context["opponent"] = opponent_name
        
        situation = "opponent_good_roll" if is_good_roll else "opponent_bust"
        return self.add_bot_reaction(bot_name, situation, context)
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _ordinal(self, n: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'TH'
        else:
            suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(n % 10, 'TH')
        return f"{n}{suffix}"
    
    def get_messages_by_type(self, msg_type: str) -> List[Message]:
        """Get all messages of a specific type"""
        return [msg for msg in self.messages if msg.type == msg_type]
    
    def get_messages_by_sender(self, sender: str) -> List[Message]:
        """Get all messages from a specific sender"""
        return [msg for msg in self.messages if msg.sender == sender]
    
    def get_gref_messages(self) -> List[GREFMessage]:
        """Get all G-REF messages"""
        return self.get_messages_by_type(MessageType.GREF)
    
    def get_bot_messages(self) -> List[BOTMessage]:
        """Get all BOT messages"""
        return self.get_messages_by_type(MessageType.BOT)
