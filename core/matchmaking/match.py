from typing import List
from .player import Player

class Match:
    def __init__(self, players: List[Player]):
        self.players = players