import hashlib

class Authentication:
    def __init__(self):
        self.users = {}  # In a real application, this would be a database

    def register(self, username, email, password):
        if username in self.users:
            return False, "Username already exists"
        hashed_password = self._hash_password(password)
        self.users[username] = {"email": email, "password": hashed_password}
        return True, "User registered successfully"

    def login(self, username, password):
        if username not in self.users:
            return False, "User not found"
        if self.users[username]["password"] == self._hash_password(password):
            return True, "Login successful"
        return False, "Incorrect password"

    def _hash_password(self, password):
        # This is a simple hash function. In a real application, use a more secure method
        return hashlib.sha256(password.encode()).hexdigest()