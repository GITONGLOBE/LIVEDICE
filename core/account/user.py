from .profile import Profile

class User:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password  # In a real application, you'd want to hash this password

    def __str__(self):
        return self.username