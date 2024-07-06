import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

try:
    from games.livedice_f.game import LiveDiceF

    def main():
        game = LiveDiceF()
        game.start_game()

    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error importing LiveDiceF: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Contents of games/livedice_f:")
    for item in os.listdir(os.path.join(project_root, 'games', 'livedice_f')):
        print(f"  {item}")