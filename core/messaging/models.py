from datetime import datetime

class Message:
    def __init__(self, sender_id: int, receiver_id: int, content: str, message_type: str = "user"):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.timestamp = datetime.now()
        self.message_type = message_type  # "user" or "system"
        self.is_read = False

class Gift:
    def __init__(self, item_id: int, quantity: int):
        self.item_id = item_id
        self.quantity = quantity