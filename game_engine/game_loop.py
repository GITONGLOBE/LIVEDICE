from .dice_engine import DiceEngine

def run_game():
    dice_engine = DiceEngine()
    
    while True:
        input("Press Enter to roll the dice...")
        roll, total, score = dice_engine.get_roll_result()
        
        print(f"You rolled: {roll}")
        print(f"Total: {total}")
        print(f"Score: {score}")
        
        play_again = input("Do you want to play again? (y/n): ")
        if play_again.lower() != 'y':
            break

    print("Thanks for playing!")

if __name__ == "__main__":
    run_game()