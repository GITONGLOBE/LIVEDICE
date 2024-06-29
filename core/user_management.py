import uuid
from typing import Dict, Optional

class User:
    def __init__(self, username: str, email: str, password: str):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password = password  # In a real application, this should be hashed

class UserManager:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def create_user(self, username: str, email: str, password: str) -> User:
        if username in self.users:
            raise ValueError("Username already exists")
        user = User(username, email, password)
        self.users[user.id] = user
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return user
        return None

    def delete_user(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

user_manager = UserManager()