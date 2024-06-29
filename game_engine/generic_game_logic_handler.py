class GenericGameLogicHandler:
    def __init__(self):
        self.game_state = {}
        self.players = []
        self.current_player = None

    def initialize_game(self, player_count):
        self.players = [f"Player {i+1}" for i in range(player_count)]
        self.current_player = self.players[0]
        self.game_state = {
            "round": 1,
            "turn": 1,
            "scores": {player: 0 for player in self.players}
        }

    def next_turn(self):
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]
        self.game_state["turn"] += 1

        if self.current_player == self.players[0]:
            self.game_state["round"] += 1

    def update_score(self, player, points):
        self.game_state["scores"][player] += points

    def get_winner(self):
        return max(self.game_state["scores"], key=self.game_state["scores"].get)

    def is_game_over(self):
        # Implement your game-over condition here
        # For example, you can check if a certain number of rounds have been played
        return self.game_state["round"] > 10

    def get_game_state(self):
        return self.game_state

    def get_current_player(self):
        return self.current_player