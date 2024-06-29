from typing import List
from .models import Message, Gift
from ..inventory.system import InventorySystem

class MessagingSystem:
    def __init__(self, inventory_system: InventorySystem):
        self.messages: List[Message] = []
        self.inventory_system = inventory_system

    def send_message(self, sender_id: int, receiver_id: int, content: str) -> None:
        message = Message(sender_id, receiver_id, content)
        self.messages.append(message)

    def send_system_notification(self, receiver_id: int, content: str) -> None:
        message = Message(sender_id=0, receiver_id=receiver_id, content=content, message_type="system")
        self.messages.append(message)

    def get_user_messages(self, user_id: int) -> List[Message]:
        return [msg for msg in self.messages if msg.receiver_id == user_id]

    def mark_as_read(self, message_id: int) -> None:
        for message in self.messages:
            if id(message) == message_id:
                message.is_read = True
                break

    def send_gift(self, sender_id: int, receiver_id: int, gift: Gift) -> None:
        content = f"You received a gift: {gift.quantity}x Item#{gift.item_id}"
        self.send_system_notification(receiver_id, content)
        self.inventory_system.add_item(receiver_id, gift.item_id, gift.quantity)