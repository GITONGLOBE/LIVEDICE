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
        large_font = pygame.font.Font(None, 28)
        medium_font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
        
        lines = self.text.split('\n')
        y_offset = 10
        for line in lines:
            if line.startswith('**'):
                font = large_font
                line = line[2:]
            elif line.startswith('*'):
                font = small_font
                line = line[1:]
            else:
                font = medium_font
            
            text_surface = font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.top + y_offset + font.get_linesize() // 2))
            screen.blit(text_surface, text_rect)
            y_offset += font.get_linesize()

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

        self.dragging_scrollbar = False
        self.drag_start_y = 0

        self.game_state = GameState()

        self.debug_print_game_log()

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
        self.roll_button = None
        self.stash_button = None
        self.bank_button = None
        self.start_turn_button = None
        self.bust_text_box = None

        self.selected_dice = []
        self.dice_rects = []
        self.scoring_combinations = []

        # Scrollable game log
        self.log_font = pygame.font.Font(None, 20)
        self.log_line_height = 25
        self.log_scroll_y = 0
        self.max_visible_lines = 8

        self.load_dice_images()
        self.setup_game()

        self.bot_roll_button = None
        self.bot_stash_button = None
        self.bot_bank_button = None

    def create_bust_text_box(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        box_width = 400
        box_height = 80
        margin_top = 50  # Adjust this value to move the bust text box up or down
        self.bust_text_box = pygame.Rect(
            snaptray_rect.centerx - box_width // 2,
            snaptray_rect.top + margin_top,
            box_width,
            box_height
        )

    def load_dice_images(self):
        self.dice_images = {}
        self.small_dice_images = {}
        self.green_dice_images = {}
        self.small_green_dice_images = {}
        for i in range(1, 7):
            self.dice_images[i] = pygame.image.load(os.path.join('assets', f'dice_{i}.png'))
            self.small_dice_images[i] = pygame.image.load(os.path.join('assets', f'dice_{i}_36px.png'))
            self.green_dice_images[i] = pygame.image.load(os.path.join('assets', f'dice_olgreen_{i}.png'))
            self.small_green_dice_images[i] = pygame.image.load(os.path.join('assets', f'dice_olgreen_{i}_36px.png'))

    def get_scoring_dice(self):
        scoring_dice = []
        dice_values = self.game_state.dice_values
        counts = [dice_values.count(i) for i in range(1, 7)]
        
        # Check for triples
        for i in range(6):
            if counts[i] >= 3:
                scoring_dice.extend([j for j, val in enumerate(dice_values) if val == i+1][:3])
        
        # Check for remaining 1s and 5s
        for i, val in enumerate(dice_values):
            if i not in scoring_dice and val in [1, 5]:
                scoring_dice.append(i)
        
        # Check for double 6s
        if counts[5] >= 2 and len([i for i in scoring_dice if dice_values[i] == 6]) < 2:
            sixes = [i for i, val in enumerate(dice_values) if val == 6 and i not in scoring_dice][:2]
            scoring_dice.extend(sixes)
        
        return scoring_dice

    def render_dice(self, surface, dice_values, x, y):
        for i, value in enumerate(dice_values):
            surface.blit(self.dice_images[value], (x + i*35, y))

    def start_turn(self):
        print("Starting turn or new stash")
        if self.bust_text_box:
            # Handle the end of a busted turn
            self.game_state.next_player()
            self.game_state.reset_turn()
            self.bust_text_box = None
        elif len(self.game_state.current_player.stashed_dice) == 6:
            self.game_state.move_stash_to_stash_house()
            print("Moved stash to stash house")
        
        self.game_state.turn_started = True
        self.game_state.dice_values = []  # Clear dice values here
        self.roll_dice()
        self.update_buttons()
        self.update_game_log()

    def setup_game(self):
        self.game_state.add_player(User("Human", "human@example.com", "password"))
        self.game_state.add_player(User("Bot", "bot@example.com", "password"))
        self.determine_starting_player()
        self.game_state.set_active_task("Click START TURN to begin your turn")
        self.update_buttons()

    def start_game(self):
        self.setup_game()
        self.update_buttons()

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

    def draw_section(self):
        for section, rect in self.sections.items():
            pygame.draw.rect(self.screen, self.section_colors[section], rect)
            if section == "GAME DATA LOG":
                self.draw_scrollable_log(rect)
            else:
                self.draw_section_content(section, rect)

        if self.bank_button:
            self.bank_button.draw(self.screen)
        if self.start_turn_button:
            self.start_turn_button.draw(self.screen)
        if self.stash_button:
            self.stash_button.draw(self.screen)
        if self.roll_button:
            self.roll_button.draw(self.screen)

        if self.game_state.current_player.user.username == "Bot":
            if self.bot_roll_button:
                self.bot_roll_button.draw(self.screen)
            if self.bot_stash_button:
                self.bot_stash_button.draw(self.screen)
            if self.bot_bank_button:
                self.bot_bank_button.draw(self.screen)

        if self.bust_text_box:
            pygame.draw.rect(self.screen, self.RED, self.bust_text_box)
            current_player = self.game_state.current_player
            lost_points = (self.game_state.calculate_score(self.game_state.dice_values) +
                        self.game_state.calculate_score(current_player.stashed_dice) +
                        current_player.stash_house)
            
            bust_text = f"Oh Noo! {current_player.user.username} That's a BUST!"
            self.draw_text(bust_text, self.bust_text_box, self.WHITE, font_size=28, offset_y=-20)
            
            points_text = f"{lost_points} POINTS LOST!"
            self.draw_text(points_text, self.bust_text_box, self.WHITE, font_size=20, offset_y=20)
            
            self.draw_text("TURN ENDED", self.bust_text_box, self.WHITE, font_size=24, offset_y=50)

    def draw_scrollable_log(self, rect):
        log_surface = pygame.Surface((rect.width, rect.height))
        log_surface.fill(self.section_colors["GAME DATA LOG"])

        visible_lines = rect.height // self.log_line_height
        total_lines = len(self.game_state.game_log)

        # Reverse the scrolling logic
        start_index = self.log_scroll_y
        end_index = min(start_index + visible_lines, total_lines)

        y = rect.height - self.log_line_height
        for i in range(end_index - 1, start_index - 1, -1):
            entry = self.game_state.game_log[i]
            text_surface = self.log_font.render(entry, True, self.BLACK)
            log_surface.blit(text_surface, (10, y))
            y -= self.log_line_height

        if total_lines > visible_lines:
            scrollbar_height = max(20, int((visible_lines / total_lines) * rect.height))
            scrollbar_pos = int((self.log_scroll_y / max(1, total_lines - visible_lines)) * (rect.height - scrollbar_height))
            pygame.draw.rect(log_surface, self.WHITE, (rect.width - 10, scrollbar_pos, 10, scrollbar_height))

        self.screen.blit(log_surface, rect)

    def update_game_log(self):
        visible_lines = self.sections["GAME DATA LOG"].height // self.log_line_height
        total_lines = len(self.game_state.game_log)
        self.log_scroll_y = max(0, total_lines - visible_lines)

    def draw_section_content(self, section, rect):
        if section == "GAME SETTINGS":
            self.draw_text(f"•LIVEDICE [ F ]", rect, self.BLACK)
            self.draw_text(f"Target: 4000 points", rect, self.BLACK, offset_y=30)
        elif section == "LEADERBOARD":
            for i, player in enumerate(self.game_state.players):
                self.draw_text(f"{player.user.username}: {player.score} [{player.turn_score}]", rect, self.BLACK, offset_y=i*30)

        elif section == "REALTIME STASH":
            current_player = self.game_state.current_player
            stash_number = self.get_stash_number(current_player)
            self.draw_text(f"{stash_number} STASH", rect, self.BLACK, offset_y=10)
            
            for i, value in enumerate(current_player.stashed_dice):
                dice_rect = pygame.Rect(rect.left + i * 40 + 10, rect.top + 40, 36, 36)
                self.screen.blit(self.small_green_dice_images[value], dice_rect)
            
            pygame.draw.line(self.screen, self.BLACK, (rect.left + 10, rect.top + 90), (rect.right - 10, rect.top + 90), 2)
            
            self.draw_text("STASH HOUSE is holding", rect, self.BLACK, offset_y=100)
            self.draw_text(f"{current_player.stash_house_count} STASHES with {current_player.stash_house} POINTS", rect, self.BLACK, offset_y=120)
        
        elif section == "SNAPTRAY":
            self.dice_rects = []  # Reset dice_rects
            stashable_dice = self.get_stashable_dice()
            for i, value in enumerate(self.game_state.dice_values):
                dice_rect = pygame.Rect(rect.left + i*100 + 50, rect.top + 250, 80, 80)
                self.dice_rects.append(dice_rect)
                if i in stashable_dice:
                    dice_image = self.green_dice_images[value]
                else:
                    dice_image = self.dice_images[value]
                self.screen.blit(dice_image, dice_rect)
                print(f"Dice {i} rect: {dice_rect}")
                
                if i in self.selected_dice:
                    pygame.draw.rect(self.screen, self.BLUE, dice_rect, 3)
                elif i in stashable_dice:
                    pygame.draw.rect(self.screen, self.GREEN, dice_rect, 3)
                    
                    # Draw blue outline for selected dice
                    if i in self.selected_dice:
                        pygame.draw.rect(self.screen, self.BLUE, dice_rect, 3)
                    
                    # Draw red outline for hovered dice
                    if dice_rect.collidepoint(pygame.mouse.get_pos()):
                        pygame.draw.rect(self.screen, self.RED, dice_rect, 3)

                # Draw scoring combination text boxes
                for i, (combination, points) in enumerate(self.scoring_combinations):
                    text_box = pygame.Rect(rect.left + i*200 + 50, rect.top + 50, 180, 60)
                    pygame.draw.rect(self.screen, self.WHITE, text_box)
                    pygame.draw.rect(self.screen, self.BLACK, text_box, 2)
                    self.draw_text(f"{combination}", text_box, self.BLACK, font_size=20)
                    self.draw_text(f"[ {points} POINTS ]", text_box, self.BLACK, offset_y=30, font_size=20)

        elif section == "ACTIVE TASK":
            self.draw_text(self.game_state.active_task, rect, self.BLACK)

        elif section == "SCORE TABLE":
            score_table = [
                ([5], "Single 5 = 50 points"),
                ([1], "Single 1 = 100 points"),
                ([6, 6], "Double 6 = 100 points"),
                ([2, 2, 2], "Triple 2 = 200 points"),
                ([3, 3, 3], "Triple 3 = 300 points"),
                ([4, 4, 4], "Triple 4 = 400 points"),
                ([5, 5, 5], "Triple 5 = 500 points"),
                ([6, 6, 6], "Triple 6 = 600 points"),
                ([1, 1, 1], "Triple 1 = 1000 points")
            ]
            
            current_roll = self.game_state.dice_values
            for i, (dice, entry) in enumerate(score_table):
                row_rect = pygame.Rect(rect.left, rect.top + i*35, rect.width, 30)
                
                # Check if the exact combination is in the current roll
                is_match = False
                if len(dice) == 1:
                    is_match = dice[0] in current_roll
                elif len(dice) == 2:
                    is_match = current_roll.count(dice[0]) >= 2
                elif len(dice) == 3:
                    is_match = current_roll.count(dice[0]) >= 3
                
                # Render dice images
                for j, value in enumerate(dice):
                    dice_image = self.small_green_dice_images[value] if is_match else self.small_dice_images[value]
                    self.screen.blit(dice_image, (rect.left + 5 + j*40, rect.top + i*35))
                
                # Render text
                text_color = self.GREEN if is_match else self.BLACK
                self.draw_text(entry, rect, text_color, offset_y=i*35, offset_x=40*len(dice) + 10)

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

    def draw_text(self, text, rect, color, offset_y=0, offset_x=0, font_size=24):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(str(text), True, color)
        text_rect = text_surface.get_rect(topleft=(rect.left + 10 + offset_x, rect.top + 10 + offset_y))
        self.screen.blit(text_surface, text_rect)

    def bot_turn(self):
        current_score = self.game_state.calculate_score(self.game_state.dice_values)
        if current_score == 0:
            self.game_state.bust()
            self.game_state.add_log_entry(f"Bot busted! Lost {self.game_state.current_player.turn_score} points.")
            self.game_state.next_player()
        elif len(self.game_state.current_player.stashed_dice) == 6:
            self.game_state.start_new_stash()
            self.game_state.roll_dice()
        elif self.game_state.current_player.turn_score + current_score < 300 or random.random() < 0.5:
            scoring_dice = [i for i, die in enumerate(self.game_state.dice_values) if self.game_state.is_scoring_dice([die])]
            self.game_state.stash_dice(scoring_dice)
            if self.game_state.dice_values:
                self.game_state.roll_dice()
        else:
            self.bank_points()
        
        # Add a small delay to make the bot's actions visible
        pygame.time.delay(1000)

        # If it's still the bot's turn, continue
        if self.game_state.current_player.user.username == "Bot":
            self.bot_turn()

    def update(self):
        if self.game_state.current_player.user.username == "Bot":
            if not self.game_state.turn_started:
                self.start_turn()
            else:
                self.bot_turn()        
        if self.game_state.check_game_over():
            self.end_game()

    def human_turn(self):
        # Human turn logic is handled by buttons
        pass

    def stash_dice(self):
        print("Stashing dice")
        print(f"Selected dice before stash: {self.selected_dice}")
        if self.selected_dice:
            self.game_state.stash_dice(self.selected_dice)
            print(f"Stashed dice after stash: {self.game_state.current_player.stashed_dice}")
            self.selected_dice = []
            self.scoring_combinations = self.game_state.get_scoring_combinations()
            print(f"Scoring combinations after stash: {self.scoring_combinations}")
            
            if len(self.game_state.current_player.stashed_dice) == 6:
                print("Stash is full, waiting for player to start new stash")
                self.game_state.set_active_task("Start new stash")
            elif not self.game_state.dice_values:
                print("No dice values left, waiting for player to roll")
                self.game_state.set_active_task("Roll dice")
            else:
                print(f"Remaining dice values: {self.game_state.dice_values}")
                self.game_state.set_active_task("Select dice to stash or roll again")
            
            self.update_buttons()
            self.update_game_log()

        if not self.game_state.dice_values and not self.game_state.current_player.stashed_dice:
            print("No dice values and no stashed dice, waiting for player to start new turn")
            self.game_state.set_active_task("Start new turn")
            self.update_buttons()
            self.update_game_log()

    def roll_dice(self):
        print("Rolling dice")
        if len(self.game_state.current_player.stashed_dice) == 6:
            print("All dice stashed, starting new stash")
            self.game_state.start_new_stash()
        
        self.scoring_combinations = self.game_state.roll_dice()
        print(f"Rolled dice: {self.game_state.dice_values}")
        print(f"Scoring combinations: {self.scoring_combinations}")
        
        if not self.scoring_combinations:
            print("No scoring combinations, busting")
            self.game_state.bust()
            self.create_bust_text_box()
        
        self.game_state.turn_started = True
        self.selected_dice = []  # Clear selected dice after rolling
        self.update_buttons()
        self.update_game_log()

    def bank_points(self):
        self.game_state.bank_points()
        self.game_state.turn_started = False
        self.update_buttons()
        self.update_game_log()

    def end_game(self):
        winner = max(self.game_state.players, key=lambda p: p.score)
        self.game_state.add_log_entry(f"Game Over! {winner.user.username} wins with {winner.score} points!")
        self.game_state.set_active_task("Game Over")

    def update_buttons(self):
        snaptray_rect = self.sections["SNAPTRAY"]
        margin = 20
        button_width = (snaptray_rect.width - 3 * margin) // 2
        button_height = 100
        vertical_spacing = 10

        bottom_y = snaptray_rect.bottom - button_height - margin - 50
        top_y = bottom_y - button_height - vertical_spacing

        self.roll_button = None
        self.stash_button = None
        self.bank_button = None
        self.start_turn_button = None

        current_player = self.game_state.current_player

        # Calculate scores
        table_score = self.game_state.calculate_score(self.game_state.dice_values)
        stash_score = self.game_state.calculate_score(current_player.stashed_dice)
        virtual_score = current_player.turn_score + current_player.stash_house + table_score + stash_score

        # BANK button
        bank_text = f"**BANK {virtual_score} POINTS\n"
        bank_text += f"*ON TABLE: {table_score} / {self.get_stash_number(current_player)} STASH: {stash_score} / STASH HOUSE: {current_player.stash_house}"
        self.bank_button = Button(snaptray_rect.left + margin, top_y, button_width, button_height, bank_text, self.RED, self.BLACK)

        # Calculate turn number
        turn_number = (self.game_state.total_turns // len(self.game_state.players)) + 1

        if self.bust_text_box or not self.game_state.turn_started or (self.game_state.dice_values == [] and current_player.stashed_dice == []):
            start_turn_text = f"{current_player.user.username}\n**START TURN [{turn_number}]\n*AND ROLL THE DICE"
            self.start_turn_button = Button(snaptray_rect.right - button_width - margin, top_y, button_width, button_height, 
                                            start_turn_text, self.GREEN, self.BLACK)
        elif len(current_player.stashed_dice) == 6:
            next_stash = self.get_stash_number(current_player, next=True)
            self.start_turn_button = Button(snaptray_rect.right - button_width - margin, bottom_y, button_width, button_height, 
                                            f"{current_player.user.username}\n**START {next_stash} STASH\n*AND ROLL THE DICE", 
                                            self.GREEN, self.BLACK)
        else:
            if self.get_stashable_dice():
                self.stash_button = Button(snaptray_rect.left + margin, bottom_y, button_width, button_height, 
                                        f"**STASH\n{self.get_stash_number(current_player)} STASH", 
                                        self.GREEN, self.BLACK)
            
            if current_player.stashed_dice or self.get_stashable_dice():
                remaining_dice = len(self.game_state.dice_values)
                roll_text = f"{current_player.user.username}\n**ROLL {remaining_dice}\n*ROLL {current_player.roll_count + 1}"
                self.roll_button = Button(snaptray_rect.right - button_width - margin, bottom_y, button_width, button_height, 
                                        roll_text, self.BLUE, self.BLACK)

        self.update_button_texts()

    def handle_bot_turn(self):
        if self.game_state.current_player.user.username == "Bot":
            bot_status = self.game_state.bot_turn()
            if bot_status == "BOT_TURN_START":
                self.update_buttons()
                self.bot_roll_button = Button(self.sections["SNAPTRAY"].centerx - 150, self.sections["SNAPTRAY"].bottom - 60, 100, 50, "Bot Roll", self.BLUE, self.BLACK)
                self.bot_stash_button = Button(self.sections["SNAPTRAY"].centerx - 50, self.sections["SNAPTRAY"].bottom - 60, 100, 50, "Bot Stash", self.GREEN, self.BLACK)
                self.bot_bank_button = Button(self.sections["SNAPTRAY"].centerx + 50, self.sections["SNAPTRAY"].bottom - 60, 100, 50, "Bot Bank", self.RED, self.BLACK)
            self.update_game_log()

    def get_stash_number(self, player, next=False):
        stash_number = player.stash_level + (1 if next else 0)
        if stash_number == 1:
            return "1st"
        elif stash_number == 2:
            return "2nd"
        elif stash_number == 3:
            return "3rd"
        else:
            return f"{stash_number}th"

    def get_stashable_dice(self):
        stashable = []
        combinations = self.game_state.get_scoring_combinations()
        
        for combination, _ in combinations:
            if combination.startswith("TRIPLE"):
                value = int(combination.split()[-1])
                stashable.extend([i for i, v in enumerate(self.game_state.dice_values) if v == value][:3])
            elif combination == "DOUBLE 6":
                stashable.extend([i for i, v in enumerate(self.game_state.dice_values) if v == 6][:2])
            elif combination.startswith("SINGLE"):
                value = 1 if '1' in combination else 5
                stashable.extend([i for i, v in enumerate(self.game_state.dice_values) if v == value])
        
        return list(set(stashable))  # Remove duplicates

    def update_button_texts(self):
        current_player = self.game_state.current_player

        if self.roll_button:
            remaining_dice = len(self.game_state.dice_values)
            roll_text = f"{current_player.user.username}\n**ROLL {remaining_dice}\n*ROLL {current_player.roll_count + 1}"
            if remaining_dice == 1:
                roll_text += " DANGER!"
            self.roll_button.text = roll_text

        if self.stash_button:
            stash_number = self.get_stash_number(current_player)
            self.stash_button.text = f"**STASH\n{stash_number} STASH"

        if self.bank_button:
            table_score = self.game_state.calculate_score(self.game_state.dice_values)
            stash_score = self.game_state.calculate_score(current_player.stashed_dice)
            virtual_score = current_player.turn_score + current_player.stash_house + table_score + stash_score
            bank_text = f"**BANK {virtual_score} POINTS\n"
            bank_text += f"*ON TABLE: {table_score} / {self.get_stash_number(current_player)} STASH: {stash_score} / STASH HOUSE: {current_player.stash_house}"
            self.bank_button.text = bank_text

        if self.start_turn_button:
            turn_number = (self.game_state.total_turns // len(self.game_state.players)) + 1
            if current_player.stash_level == 1:
                self.start_turn_button.text = f"{current_player.user.username}\n**START TURN [{turn_number}]\n*AND ROLL THE DICE"
            else:
                next_stash = self.get_stash_number(current_player, next=True)
                self.start_turn_button.text = f"{current_player.user.username}\n**START {next_stash} STASH\n*AND ROLL THE DICE"

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                pos = event.pos
                if self.game_state.current_player.user.username == "Human":
                    if self.start_turn_button and self.start_turn_button.is_clicked(pos):
                        if len(self.game_state.current_player.stashed_dice) == 6:
                            self.game_state.start_new_stash()
                        self.start_turn()
                    elif self.roll_button and self.roll_button.is_clicked(pos):
                        self.roll_dice()
                    elif self.stash_button and self.stash_button.is_clicked(pos):
                        self.stash_dice()
                    elif self.bank_button and self.bank_button.is_clicked(pos):
                        self.bank_points()
                    else:
                        for i, dice_rect in enumerate(self.dice_rects):
                            if dice_rect.collidepoint(pos):
                                self.handle_dice_click(i)
                elif self.game_state.current_player.user.username == "Bot":
                    if self.bot_roll_button and self.bot_roll_button.is_clicked(pos):
                        self.game_state.bot_action("ROLL")
                    elif self.bot_stash_button and self.bot_stash_button.is_clicked(pos):
                        self.game_state.bot_action("STASH")
                    elif self.bot_bank_button and self.bot_bank_button.is_clicked(pos):
                        self.game_state.bot_action("BANK")
                    self.handle_bot_turn()
                
                # Handle scrollbar dragging
                log_rect = self.sections["GAME DATA LOG"]
                if log_rect.collidepoint(pos):
                    self.dragging_scrollbar = True
                    self.drag_start_y = pos[1]
            
            elif event.button == 4:  # Scroll up
                self.log_scroll_y = max(0, self.log_scroll_y - 1)
            elif event.button == 5:  # Scroll down
                visible_lines = self.sections["GAME DATA LOG"].height // self.log_line_height
                max_scroll = max(0, len(self.game_state.game_log) - visible_lines)
                self.log_scroll_y = min(max_scroll, self.log_scroll_y + 1)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging_scrollbar = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_scrollbar:
                dy = event.pos[1] - self.drag_start_y
                self.drag_start_y = event.pos[1]
                visible_lines = self.sections["GAME DATA LOG"].height // self.log_line_height
                total_lines = len(self.game_state.game_log)
                max_scroll = max(0, total_lines - visible_lines)
                self.log_scroll_y = max(0, min(max_scroll, self.log_scroll_y + int(dy * 0.1)))
        
        self.draw_section()

    def handle_dice_click(self, index):
        print(f"Clicked die at index {index}")
        print(f"Stashable dice: {self.get_stashable_dice()}")
        print(f"Current dice values: {self.game_state.dice_values}")
        print(f"Current selected dice: {self.selected_dice}")

        if index not in self.get_stashable_dice():
            print(f"Die at index {index} is not stashable")
            return  # Do nothing if the clicked die is not stashable

        value = self.game_state.dice_values[index]
        combinations = self.game_state.get_scoring_combinations()
        
        print(f"Scoring combinations: {combinations}")

        # Check if the die is part of a scoring combination
        for combination, _ in combinations:
            if combination.startswith("TRIPLE") and value == int(combination.split()[-1]):
                indices = [i for i, v in enumerate(self.game_state.dice_values) if v == value][:3]
                print(f"Toggling triple: {indices}")
                self.toggle_selection(indices)
                break
            elif combination == "DOUBLE 6" and value == 6:
                indices = [i for i, v in enumerate(self.game_state.dice_values) if v == 6][:2]
                print(f"Toggling double 6: {indices}")
                self.toggle_selection(indices)
                break
        else:
            # If not part of a combination, it's a single scoring die (1 or 5)
            print(f"Toggling single die: {index}")
            self.toggle_selection([index])
        
        print(f"Selected dice after toggle: {self.selected_dice}")
        self.update_buttons()

    def handle_bust(self):
        self.create_bust_text_box()
        current_player = self.game_state.current_player
        lost_points = (self.game_state.calculate_score(self.game_state.dice_values) +
                    self.game_state.calculate_score(current_player.stashed_dice) +
                    current_player.stash_house)
        self.game_state.add_log_entry(f"{current_player.user.username} busted! Lost {lost_points} points.")
        # Don't clear dice values or change player here
        self.update_buttons()
        self.update_game_log()

    def toggle_selection(self, indices):
        print(f"Toggling selection for indices: {indices}")
        if all(i in self.selected_dice for i in indices):
            for i in indices:
                self.selected_dice.remove(i)
        else:
            for i in indices:
                if i not in self.selected_dice:
                    self.selected_dice.append(i)
        print(f"Selected dice after toggle: {self.selected_dice}")

    def debug_print_game_log(self):
        print("Game Log Contents:")
        for i, entry in enumerate(self.game_state.game_log):
            print(f"{i}: {entry}")

class GameRunner:
    @staticmethod
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
            ui.draw_section()  # Changed from draw_sections to draw_section

            pygame.display.flip()
            clock.tick(60)  # Limit to 60 FPS

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    ui = InGameUI()
    GameRunner.run_game(ui)