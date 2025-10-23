"""
MESSAGE SYSTEM MODULE
Core message classes for LIVEDICE messaging system.
Defines message types, categories, and base message structure.
"""

import time
from typing import Optional, Dict, Any


class MessageType:
    """Message type constants"""
    GREF = "game_referee"
    BOT = "bot_player"


class GREFCategory:
    """Game Referee message categories"""
    ACTION_REPORT = "action_report"    # "Player rolled 4-2"
    GAME_STATE = "game_state"          # "Round 3 begins"
    OFFICIAL = "official"              # "Player 2 wins!"
    TURN_START = "turn_start"          # "It's Player's turn"
    TURN_END = "turn_end"              # "Player ended their turn"
    STASH_ACTION = "stash_action"      # "Player stashed dice"
    BANK_ACTION = "bank_action"        # "Player banked points"
    BUST_EVENT = "bust_event"          # "Player busted"
    GAME_START = "game_start"          # "Game begins!"
    GAME_END = "game_end"              # "Game over!"


class BOTCategory:
    """Bot player message categories"""
    REACTION = "reaction"              # "Nice roll!"
    STRATEGY = "strategy"              # "Banking to secure position"
    PERSONALITY = "personality"        # Comic relief, emotions
    TAUNT = "taunt"                    # Competitive banter
    CELEBRATION = "celebration"        # Happy reactions
    FRUSTRATION = "frustration"        # Upset reactions
    THINKING = "thinking"              # Decision-making process


class Message:
    """Base message class for all game messages"""
    
    def __init__(
        self,
        msg_type: str,
        sender: str,
        content: str,
        category: str,
        game_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a message.
        
        Args:
            msg_type: Type of message (MessageType.GREF or MessageType.BOT)
            sender: Name of the sender
            content: Message text content
            category: Message category (GREFCategory or BOTCategory)
            game_context: Optional dict with game state info
        """
        self.type = msg_type
        self.sender = sender
        self.content = content
        self.category = category
        self.timestamp = time.time()
        self.game_context = game_context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for storage/serialization"""
        return {
            "type": self.type,
            "sender": self.sender,
            "content": self.content,
            "category": self.category,
            "timestamp": self.timestamp,
            "game_context": self.game_context
        }
    
    def __str__(self) -> str:
        """String representation of message"""
        return f"{self.sender}: {self.content}"


class GREFMessage(Message):
    """Game Referee message - official game announcements"""
    
    def __init__(
        self,
        content: str,
        category: str,
        game_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Game Referee message.
        
        Args:
            content: Message text content
            category: GREFCategory constant
            game_context: Optional dict with game state info
        """
        super().__init__(
            msg_type=MessageType.GREF,
            sender="@G-REF",
            content=content,
            category=category,
            game_context=game_context
        )
    
    def get_display_sender(self) -> str:
        """Get formatted sender name for display"""
        return "@G-REF [ GAMEOFFICIAL ]"


class BOTMessage(Message):
    """Bot player message - personality-driven bot communication"""
    
    def __init__(
        self,
        bot_name: str,
        content: str,
        category: str,
        personality_name: str,
        game_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Bot message.
        
        Args:
            bot_name: Name of the bot (e.g., "@EASY-GO-BOT-1")
            content: Message text content
            category: BOTCategory constant
            personality_name: Name of the bot's personality
            game_context: Optional dict with game state info
        """
        super().__init__(
            msg_type=MessageType.BOT,
            sender=bot_name,
            content=content,
            category=category,
            game_context=game_context
        )
        self.personality_name = personality_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bot message to dictionary"""
        data = super().to_dict()
        data["personality_name"] = self.personality_name
        return data
    
    def get_display_sender(self) -> str:
        """Get formatted sender name for display"""
        return self.sender
