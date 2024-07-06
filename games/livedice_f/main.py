from bot import Bot
from player import Player

def main():
    print("LIVEDICE [F] Game")
    player = Player("Human Player")
    bot = Bot("AI Player")
    
    print(f"Created player: {player.name}")
    print(f"Created bot: {bot.name}")

if __name__ == "__main__":
    main()