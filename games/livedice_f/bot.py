from games.livedice_f.player import Player

class Bot(Player):
    def __init__(self, name):
        super().__init__(name)
        self.difficulty = "normal"

    def make_decision(self, game_state):
        # Implement bot decision-making logic here
        pass

if __name__ == "__main__":
    print("This is the Bot module for LIVEDICE [F]")