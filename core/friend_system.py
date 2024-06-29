# friend_system.py

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class UserProfile:
    user_id: str
    username: str
    status: str = "offline"

class FriendSystem:
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self.friend_lists: Dict[str, List[str]] = {}

    def add_user(self, user_id: str, username: str) -> None:
        self.users[user_id] = UserProfile(user_id, username)
        self.friend_lists[user_id] = []

    def send_friend_request(self, sender_id: str, receiver_id: str) -> bool:
        # Implement friend request logic
        pass

    def accept_friend_request(self, sender_id: str, receiver_id: str) -> bool:
        # Implement friend request acceptance logic
        pass

    def get_friend_list(self, user_id: str) -> List[UserProfile]:
        # Retrieve and return friend list
        pass

    def update_user_status(self, user_id: str, status: str) -> None:
        # Update user status
        pass

    def search_friends(self, user_id: str, query: str) -> List[UserProfile]:
        # Implement friend search functionality
        pass

# friend_system.py (continued)

    def send_friend_request(self, sender_id: str, receiver_id: str) -> bool:
        if sender_id not in self.users or receiver_id not in self.users:
            return False
        if receiver_id in self.friend_lists[sender_id]:
            return False
        # In a real implementation, you'd store pending requests separately
        self.friend_lists[sender_id].append(receiver_id)
        return True

    def accept_friend_request(self, sender_id: str, receiver_id: str) -> bool:
        if sender_id not in self.users or receiver_id not in self.users:
            return False
        if sender_id not in self.friend_lists[receiver_id]:
            self.friend_lists[receiver_id].append(sender_id)
        if receiver_id not in self.friend_lists[sender_id]:
            self.friend_lists[sender_id].append(receiver_id)
        return True

    def get_friend_list(self, user_id: str) -> List[UserProfile]:
        if user_id not in self.friend_lists:
            return []
        return [self.users[friend_id] for friend_id in self.friend_lists[user_id]]

    def update_user_status(self, user_id: str, status: str) -> None:
        if user_id in self.users:
            self.users[user_id].status = status

    def search_friends(self, user_id: str, query: str) -> List[UserProfile]:
        if user_id not in self.friend_lists:
            return []
        return [
            self.users[friend_id]
            for friend_id in self.friend_lists[user_id]
            if query.lower() in self.users[friend_id].username.lower()
        ]