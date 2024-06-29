from .account.player_manager import PlayerManager

class AuthenticationSystem:
    def __init__(self):
        self.player_manager = PlayerManager()

    def register(self, username, email, password):
        return self.player_manager.register_player(username, email, password)

    def login(self, username, password):
        return self.player_manager.login_player(username, password)

    def get_player(self, user_id):
        return self.player_manager.get_player(user_id)

    def update_player_stats(self, user_id, game_result, score):
        return self.player_manager.update_player_stats(user_id, game_result, score)