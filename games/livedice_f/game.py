import random
from games.livedice_f.player import Player
from games.livedice_f.bot import Bot
from games.livedice_f.dice import Dice

class LiveDiceF:
    def __init__(self):
        self.current_player = "Player 1"
        self.players = ["Player 1", "Player 2"]
        self.dice_values = [1, 2, 3, 4, 5]
        self.current_bet = None
        self.phase = "betting"
        self.chat_messages = []

    def place_bet(self):
        print("Placing bet")

    def challenge(self):
        print("Challenging")

    def update(self):
        # Update game logic here
        # For now, let's just print a message to show it's being called
        print("Updating game state")

    def start_game(self):
        print("Welcome to LIVEDICE [ F ]!")
        self.determine_starting_player()
        self.play_game()

    def determine_starting_player(self):
        player_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        print(f"{self.player.name} rolled a {player_roll}")
        print(f"{self.bot.name} rolled a {bot_roll}")

        if player_roll > bot_roll:
            self.current_player = self.player
        elif bot_roll > player_roll:
            self.current_player = self.bot
        else:
            print("It's a tie! Rolling again...")
            self.determine_starting_player()

        print(f"{self.current_player.name} goes first!")

    def play_game(self):
        while not self.game_over:
            if self.current_player == self.player:
                self.player_turn()
            else:
                self.bot_turn()

            self.check_winner()
            self.switch_player()

    def player_turn(self):
        print(f"\n{self.player.name}'s turn")
        self.take_turn(self.player)

    def bot_turn(self):
        print(f"\n{self.bot.name}'s turn")
        self.take_turn(self.bot)

    def take_turn(self, player):
        stash = 0
        while True:
            roll = self.dice.roll()
            print(f"{player.name} rolled: {roll}")
            score = self.calculate_score(roll)
            if score == 0:
                print("Bust! Turn over.")
                return

            stash += score
            print(f"Current stash: {stash}")

            if isinstance(player, Bot):
                if player.should_continue(stash):
                    print(f"{player.name} decides to roll again.")
                else:
                    break
            else:
                choice = input("Do you want to roll again? (y/n): ").lower()
                if choice != 'y':
                    break

        player.score += stash
        print(f"{player.name}'s total score: {player.score}")

    def calculate_score(self, roll):
        score = 0
        counts = [roll.count(i) for i in range(1, 7)]

        for i, count in enumerate(counts, 1):
            if count >= 3:
                score += i * 100
            elif i == 1:
                score += count * 100
            elif i == 5:
                score += count * 50

        if counts[5] == 2:  # Double 6
            score += 100

        return score

    def check_winner(self):
        if self.player.score >= 1000 or self.bot.score >= 1000:
            self.game_over = True
            winner = max([self.player, self.bot], key=lambda x: x.score)
            print(f"\nGame Over! {winner.name} wins with a score of {winner.score}!")

    def switch_player(self):
        self.current_player = self.bot if self.current_player == self.player else self.player

if __name__ == "__main__":
    game = LiveDiceF()
    game.start_game()