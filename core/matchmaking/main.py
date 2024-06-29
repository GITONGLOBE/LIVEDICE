import random
from .player import Player
from .matchmaking_system import MatchmakingSystem

def run_matchmaking_example():
    matchmaking = MatchmakingSystem()
    
    # Add some players to the queue
    players = [
        Player(f"Player{i}", random.randint(1, 10)) for i in range(1, 5)
    ]
    
    for player in players:
        matchmaking.add_to_queue(player)
    
    matchmaking.start_matchmaking()

if __name__ == "__main__":
    run_matchmaking_example()