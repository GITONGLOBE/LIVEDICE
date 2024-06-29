from dice_game_engine import DiceEngine
from game_engine.generic_game_logic_handler import GenericGameLogicHandler
from core import AuthenticationSystem, FriendSystem

class LiveDice:
    def __init__(self):
        self.auth = AuthenticationSystem()
        self.friend_system = FriendSystem()
        self.game_logic = GenericGameLogicHandler()
        # ... other initializations ...

    def start_game(self):
        # Example usage of authentication and player management
        success, result = self.auth.register("player1", "player1@example.com", "password123")
        if success:
            print("Player registered:", result.username)
        
        success, result = self.auth.login("player1", "password123")
        if success:
            print("Player logged in:", result.username)
            
            while True:
                # Initialize the game with 2 players (you can change this number)
                self.game_logic.initialize_game(2)
                
                # Initialize the DiceEngine
                dice_engine = DiceEngine()
                
                # Game loop
                while not self.game_logic.is_game_over():
                    current_player = self.game_logic.get_current_player()
                    print(f"It's {current_player}'s turn")
                    
                    # Use the DiceEngine to roll the dice
                    input("Press Enter to roll the dice...")
                    roll, total, score = dice_engine.get_roll_result()
                    
                    print(f"{current_player} rolled: {roll}")
                    print(f"Total: {total}")
                    print(f"Score: {score}")
                    
                    self.game_logic.update_score(current_player, score)
                    
                    # Move to next turn
                    self.game_logic.next_turn()
                
                # Game over
                winner = self.game_logic.get_winner()
                print(f"The winner is {winner}!")
                
                # Update player stats after the game
                self.auth.update_player_stats(result.user_id, "win", 100)
                
                # Get updated player info
                updated_player = self.auth.get_player(result.user_id)
                print("Updated player stats:", updated_player.get_profile().game_stats)

                play_again = input("Do you want to play another game? (y/n): ")
                if play_again.lower() != 'y':
                    break

            print("Thanks for playing!")

        else:
            print("Login failed")

    # ... other methods ...

if __name__ == "__main__":
    game = LiveDice()
    game.start_game()