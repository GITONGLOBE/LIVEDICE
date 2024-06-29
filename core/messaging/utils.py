from typing import List
from .models import Message

def format_message(message: Message) -> str:
    sender = "System" if message.message_type == "system" else f"User {message.sender_id}"
    return f"[{message.timestamp}] {sender}: {message.content}"

def display_messages(messages: List[Message]) -> None:
    for message in messages:
        print(format_message(message))