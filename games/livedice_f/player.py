class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def update_score(self, points):
        self.score += points

if __name__ == "__main__":
    print("This is the Player module for LIVEDICE [F]")