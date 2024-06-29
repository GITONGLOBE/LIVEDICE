from .user import User

class PlayerManager:
    def __init__(self):
        self.users = {}  # In-memory storage for demonstration

    def register_player(self, username, email, password):
        if username in self.users:
            return False, "Username already exists"
        
        user_id = len(self.users) + 1
        new_user = User(user_id, username, email)
        self.users[username] = {
            "user": new_user,
            "password": password  # In a real system, store hashed passwords
        }
        return True, new_user

    def login_player(self, username, password):
        if username not in self.users:
            return False, "Invalid username or password"
        
        user_data = self.users[username]
        if user_data["password"] == password:
            user_data["user"].update_last_login()
            return True, user_data["user"]
        else:
            return False, "Invalid username or password"

    def get_player(self, user_id):
        for user_data in self.users.values():
            if user_data["user"].user_id == user_id:
                return user_data["user"]
        return None

    def update_player_stats(self, user_id, game_result, score):
        player = self.get_player(user_id)
        if player:
            player.update_profile_stats(game_result, score)
            return True
        return False