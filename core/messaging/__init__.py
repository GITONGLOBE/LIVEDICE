"""
LIVEDICE MESSAGING SYSTEM
Core messaging module for game referee and bot player messages.
Provides structured message system with rich data objects.
"""

from .message_system import (
    MessageType,
    GREFCategory,
    BOTCategory,
    Message,
    GREFMessage,
    BOTMessage
)

from .bot_personalities import (
    BotPersonality,
    SportsmanshipPersonality,
    SarcasticPersonality,
    OverlyEnthusiasticPersonality,
    BraggartPersonality,
    DullardPersonality,
    HotheadPersonality,
    StonePersonality,
    PoetPersonality,
    DadJokePersonality,
    RastaPersonality,
    PiratePersonality,
    CynicPersonality,
    get_personality_for_bot
)

from .message_manager import MessageManager

__all__ = [
    "MessageType",
    "GREFCategory",
    "BOTCategory",
    "Message",
    "GREFMessage",
    "BOTMessage",
    "BotPersonality",
    "SportsmanshipPersonality",
    "SarcasticPersonality",
    "OverlyEnthusiasticPersonality",
    "BraggartPersonality",
    "DullardPersonality",
    "HotheadPersonality",
    "StonePersonality",
    "PoetPersonality",
    "DadJokePersonality",
    "RastaPersonality",
    "PiratePersonality",
    "CynicPersonality",
    "get_personality_for_bot",
    "MessageManager"
]