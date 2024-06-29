from typing import List
from .player import Player
from .match import Match

class MatchmakingSystem:
    def __init__(self):
        self.queue: List[Player] = []

    def add_to_queue(self, player: Player):
        self.queue.append(player)

    def remove_from_queue(self, player: Player):
        self.queue.remove(player)

    def find_match(self) -> Match | None:
        if len(self.queue) < 2:
            return None
        
        # Simple matching: just pair the first two players in the queue
        players = self.queue[:2]
        for player in players:
            self.remove_from_queue(player)
        
        return Match(players)

    def start_matchmaking(self):
        while True:
            match = self.find_match()
            if match:
                self.start_game(match)
            else:
                break

    def start_game(self, match: Match):
        print(f"Starting game with players: {[player.id for player in match.players]}")
        # Here you would implement the logic to actually start the game