from datetime import datetime

class Profile:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.creation_date = datetime.now()
        self.last_login = None
        self.game_stats = {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "total_score": 0
        }

    def update_stats(self, game_result, score):
        self.game_stats["games_played"] += 1
        self.game_stats["total_score"] += score
        if game_result == "win":
            self.game_stats["wins"] += 1
        else:
            self.game_stats["losses"] += 1

    def update_last_login(self):
        self.last_login = datetime.now()