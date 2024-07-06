import pygame
import sys
import os
import random

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from core.game_state.game_state import GameState
from core.account.user import User

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Draw outline if mouse is over the button
        if self.is_mouse_over():
            pygame.draw.rect(screen, self.text_color, self.rect, 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def is_mouse_over(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

class InGameUI:
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("•LIVEDICE [ F ] - In-Game UI")

        self.game_state = GameState()
        self.setup_game()

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.CYAN = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)
        self.ORANGE = (255, 165, 0)
        self.PURPLE = (128, 0, 128)

        # UI sections
        self.sections = {
            "GAME SETTINGS": pygame.Rect(0, 0, 300, 100),
            "LEADERBOARD": pygame.Rect(0, 100, 300, 350),
            "REALTIME STASH": pygame.Rect(0, 450, 300, 150),
            "SNAPTRAY": pygame.Rect(300, 50, 600, 600),
            "ACTIVE TASK": pygame.Rect(900, 0, 300, 100),
            "SCORE TABLE": pygame.Rect(900, 100, 300, 350),
            "TURN & ROLL OVERVIEW": pygame.Rect(900, 450, 300, 150),
            "GAME CHAT": pygame.Rect(0, 600, 600, 200),
            "GAME DATA LOG": pygame.Rect(600, 600, 600, 200)
        }

        # Colors for each section
        self.section_colors = {
            "GAME SETTINGS": self.RED,
            "LEADERBOARD": self.GREEN,
            "REALTIME STASH": self.BLUE,
            "SNAPTRAY": self.YELLOW,
            "ACTIVE TASK": self.CYAN,
            "SCORE TABLE": self.MAGENTA,
            "TURN & ROLL OVERVIEW": self.ORANGE,
            "GAME CHAT": self.PURPLE,
            "GAME DATA LOG": (100, 100, 100)  # Dark gray
        }

        # Buttons
        snaptray_rect = self.sections["SNAPTRAY"]
        self.roll_button = Button(snaptray_rect.left + 50, snaptray_rect.bottom - 70, 150, 50, "ROLL NOW", self.BLUE, self.BLACK)
        self.stash_button = Button(snaptray_rect.left + 225, snaptray_rect.bottom - 70, 150, 50, "STASH", self.GREEN, self.BLACK)
        self.bank_button = Button(snaptray_rect.left + 400, snaptray_rect.bottom - 70, 150, 50, "BANK", self.RED, self.BLACK)

        self.bust_button = None
        self.player_turn_button = None

        self.selected_dice = []
        self.dice_rects = []
        self.scoring_combinations = []

        # Scrollable game log
        self.log_font = pygame.font.Font(None, 20)
        self.log_line_height = 25
        self.log_scroll_y = 0
        self.max_visible_lines = 8

    def setup_game(self):
        self.game_state.add_player(User("Human", "human@example.com", "password"))
        self.game_state.add_player(User("Bot", "bot@example.com", "password"))
        self.determine_starting_player()
        self.game_state.set_active_task("Click ROLL NOW to start your turn")

    def determine_starting_player(self):
        human_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)
        while human_roll == bot_roll:
            human_roll = random.randint(1, 6)
            bot_roll = random.randint(1, 6)
        if human_roll > bot_roll:
            self.game_state.current_player_index = 0
        else:
            self.game_state.current_player_index = 1
        self.game_state.players[self.game_state.current_player_index].is_active = True
        self.game_state.add_log_entry(f"Starting player determined: {self.game_state.current_player.user.username}")

    def draw_sections(self):
        for section, rect in self.sections.items():
            pygame.draw.rect(self.screen, self.section_colors[section], rect)
            self.draw_section_content(section, rect)

        self.roll_button.draw(self.screen)
        self.stash_button.draw(self.screen)
        self.bank_button.draw(self.screen)

        if self.bust_button:
            self.bust_button.draw(self.screen)

        if self.player_turn_button:
            self.player_turn_button.draw(self.screen)

    def draw_section_content(self, section, rect):
        if section == "GAME SETTINGS":
            self.draw_text(f"•LIVEDICE [ F ]", rect, self.BLACK)
            self.draw_text(f"Target: 4000 points", rect, self.BLACK, offset_y=30)
        elif section == "LEADERBOARD":
            for i, player in enumerate(self.game_state.players):
                self.draw_text(f"{player.user.username}: {player.score} [{player.turn_score}]", rect, self.BLACK, offset_y=i*30)
        elif section == "REALTIME STASH":
            current_player = self.game_state.current_player
            self.draw_text(f"Current Player: {current_player.user.username}", rect, self.BLACK)
            self.draw_text(f"Stashed Dice: {', '.join(map(str, current_player.stashed_dice))}", rect, self.BLACK, offset_y=30)
        elif section == "SNAPTRAY":
            self.dice_rects = []  # Reset dice_rects
            for i, value in enumerate(self.game_state.dice_values):
                dice_rect = pygame.Rect(rect.left + i*100 + 50, rect.top + 250, 80, 80)
                self.dice_rects.append(dice_rect)
                color = self.GREEN if self.game_state.is_scoring_dice([value]) else self.WHITE
                if i in self.selected_dice:
                    pygame.draw.rect(self.screen, self.YELLOW, dice_rect)
                else:
                    pygame.draw.rect(self.screen, color, dice_rect)
                self.draw_text(str(value), dice_rect, self.BLACK, font_size=48)

            # Draw scoring combination text boxes
            for i, (combination, points) in enumerate(self.scoring_combinations):
                text_box = pygame.Rect(rect.left + i*200 + 50, rect.top + 50, 180, 60)
                pygame.draw.rect(self.screen, self.WHITE, text_box)
                pygame.draw.rect(self.screen, self.BLACK, text_box, 2)
                self.draw_text(f"{combination}", text_box, self.BLACK, font_size=20)
                self.draw_text(f"[ {points} POINTS ]", text_box, self.BLACK, offset_y=30, font_size=20)

            # Update ROLL button text
            remaining_dice = len(self.game_state.dice_values)
            roll_text = f"ROLL the REMAINING [{remaining_dice}]"
            if remaining_dice == 1:
                roll_text += " DANGER!"
            self.roll_button.text = roll_text

        elif section == "ACTIVE TASK":
            self.draw_text(self.game_state.active_task, rect, self.BLACK)
        elif section == "SCORE TABLE":
            score_table = [
                "Single 1: 100 points",
                "Single 5: 50 points",
                "Three 1s: 1000 points",
                "Three of a kind: 100 * face value",
                "Double 6: 100 points"
            ]
            for i, entry in enumerate(score_table):
                self.draw_text(entry, rect, self.BLACK, offset_y=i*30)
        elif section == "TURN & ROLL OVERVIEW":
            current_player = self.game_state.current_player
            self.draw_text(f"Current Player: {current_player.user.username}", rect, self.BLACK)
            self.draw_text(f"Turn: {current_player.turn_count}", rect, self.BLACK, offset_y=30)
            self.draw_text(f"Roll: {current_player.roll_count} ({current_player.stash_level})", rect, self.BLACK, offset_y=60)
            self.draw_text(f"Turn Score: {current_player.turn_score}", rect, self.BLACK, offset_y=90)
        elif section == "GAME CHAT":
            for i, message in enumerate(self.game_state.game_chat[-5:]):  # Show last 5 messages
                self.draw_text(f"{message['user']}: {message['message']}", rect, self.BLACK, offset_y=i*30)
        elif section == "GAME DATA LOG":
            self.draw_scrollable_log(rect)

    def draw_scrollable_log(self, rect):
        log_surface = pygame.Surface((rect.width, rect.height))
        log_surface.fill(self.section_colors["GAME DATA LOG"])

        y_offset = 0
        for entry in self.game_state.game_log[self.log_scroll_y:]:
            text_surface = self.log_font.render(entry, True, self.BLACK)
            log_surface.blit(text_surface, (10, y_offset))
            y_offset += self.log_line_height
            if y_offset >= rect.height:
                break

        self.screen.blit(log_surface, rect)

        # Draw scroll bar
        total_height = len(self.game_state.game_log) * self.log_line_height
        visible_ratio = min(1, rect.height / total_height)
        scroll_bar_height = max(20, int(rect.height * visible_ratio))
        scroll_bar_pos = int((self.log_scroll_y / len(self.game_state.game_log)) * (rect.height - scroll_bar_height))
        pygame.draw.rect(self.screen, self.WHITE, (rect.right - 10, rect.top + scroll_bar_pos, 10, scroll_bar_height))

    def draw_text(self, text, rect, color, offset_y=0, font_size=24):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect(topleft=(rect.left + 10, rect.top + 10 + offset_y))
        self.screen.blit(text_surface, text_rect)

    def update(self):
        if self.game_state.current_player.user.username == "Bot" and not self.game_state.turn_started:
            self.game_state.bot_turn()
            self.scoring_combinations = self.game_state.get_scoring_combinations()
            self.create_player_turn_button()
        elif self.game_state.current_player.user.username == "Human":
            self.human_turn()

        if self.game_state.check_game_over():
            self.end_game()

    def human_turn(self):
        # Human turn logic is handled by buttons
        pass

    def stash_dice(self):
        if self.selected_dice:
            self.game_state.stash_dice(self.selected_dice)
            self.selected_dice = []
            self.scoring_combinations = self.game_state.get_scoring_combinations()
            if not self.game_state.dice_values:
                self.roll_dice()

    def roll_dice(self):
        self.scoring_combinations = self.game_state.roll_dice()
        if not self.scoring_combinations:
            self.game_state.bust()
            self.create_bust_button()
        self.roll_button.text = "ROLL NOW"
        self.game_state.turn_started = True

    def bank_points(self):
        self.game_state.bank_points()
        self.game_state.turn_started = False
        self.roll_button.text = "ROLL NOW"

    def end_game(self):
        winner = max(self.game_state.players, key=lambda p: p.score)
        self.game_state.add_log_entry(f"Game Over! {winner.user.username} wins with {winner.score} points!")
        self.game_state.set_active_task("Game Over")

    def create_bust_button(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        self.bust_button = Button(snaptray_rect.centerx - 100, snaptray_rect.centery - 25, 200, 50, "OH NO, THAT'S A BUST!", self.RED, self.WHITE)

    def create_player_turn_button(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        self.player_turn_button = Button(snaptray_rect.centerx - 100, snaptray_rect.centery + 50, 200, 50, "Player's Turn Roll Now!!", self.GREEN, self.BLACK)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                pos = event.pos
                if self.game_state.current_player.user.username == "Human":
                    if self.roll_button.is_clicked(pos):
                        self.roll_dice()
                    elif self.stash_button.is_clicked(pos):
                        self.stash_dice()
                    elif self.bank_button.is_clicked(pos):
                        self.bank_points()
                    elif self.bust_button and self.bust_button.is_clicked(pos):
                        self.bust_button = None
                        self.game_state.next_player()
                        self.game_state.turn_started = False
                    else:
                        # Check if a die or dice combination was clicked
                        for i, dice_rect in enumerate(self.dice_rects):
                            if dice_rect.collidepoint(pos):
                                self.handle_dice_click(i)
                elif self.player_turn_button and self.player_turn_button.is_clicked(pos):
                    self.player_turn_button = None
                    self.game_state.next_player()
                    self.game_state.turn_started = False
            elif event.button == 4:  # Scroll up
                self.log_scroll_y = max(0, self.log_scroll_y - 1)
            elif event.button == 5:  # Scroll down
                self.log_scroll_y = min(len(self.game_state.game_log) - self.max_visible_lines, self.log_scroll_y + 1)

    def handle_dice_click(self, index):
        # Check if the clicked die is part of a scoring combination
        for combination, _ in self.scoring_combinations:
            if combination.startswith("TRIPLE"):
                value = int(combination.split()[1])
                if self.game_state.dice_values[index] == value:
                    self.selected_dice = [i for i, v in enumerate(self.game_state.dice_values) if v == value]
                    return
            elif combination == "DOUBLE 6" and self.game_state.dice_values[index] == 6:
                self.selected_dice = [i for i, v in enumerate(self.game_state.dice_values) if v == 6][:2]
                return
            elif combination.startswith("SINGLE"):
                value = 1 if "1" in combination else 5
                if self.game_state.dice_values[index] == value:
                    if index in self.selected_dice:
                        self.selected_dice.remove(index)
                    else:
                        self.selected_dice.append(index)
                    return
        
        # If not part of a combination, toggle selection of the single die
        if index in self.selected_dice:
            self.selected_dice.remove(index)
        else:
            self.selected_dice.append(index)

def run_game(ui):
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                ui.handle_event(event)

        ui.screen.fill(ui.WHITE)
        ui.draw_sections()
        ui.update()

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    ui = InGameUI()
    run_game(ui)