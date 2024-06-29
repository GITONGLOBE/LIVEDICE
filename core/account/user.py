from .profile import Profile

class User:
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.profile = Profile(user_id, username)

    def get_profile(self):
        return self.profile

    def update_profile_stats(self, game_result, score):
        self.profile.update_stats(game_result, score)

    def update_last_login(self):
        self.profile.update_last_login()