import os
import pygame

class DiceRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.dice_surfaces = self.load_dice_surfaces()
        self.dice_size = {
            'snaptray': 120,
            'stash': 70,
            'log': 28
        }
        self.log_font = pygame.font.Font(os.path.join("assets", "open-sauce-two", "OpenSauceTwo-Regular.ttf"), 24)

    def load_dice_surfaces(self):
        dice_surfaces = {
            'snaptray': {},
            'stash': {},
            'log': {}
        }
        for i in range(1, 7):
            dice_surfaces['snaptray'][f'white_{i}'] = pygame.image.load(f"assets/dice_{i}_120px.png")
            dice_surfaces['snaptray'][f'green_{i}'] = pygame.image.load(f"assets/dice_olgreen_{i}_120px.png")
            dice_surfaces['stash'][f'white_{i}'] = pygame.image.load(f"assets/dice_{i}_70px.png")
            dice_surfaces['stash'][f'green_{i}'] = pygame.image.load(f"assets/dice_olgreen_{i}_70px.png")
            dice_surfaces['log'][f'white_{i}'] = pygame.image.load(f"assets/dice_{i}_28px.png")
            dice_surfaces['log'][f'green_{i}'] = pygame.image.load(f"assets/dice_olgreen_{i}_28px.png")
        
        dice_surfaces['snaptray']['hover'] = pygame.image.load("assets/dice_hover_120px.png")
        dice_surfaces['snaptray']['selected'] = pygame.image.load("assets/dice_selected_120px.png")
        
        return dice_surfaces

    def render_dice_in_snaptray(self, dice_values, positions, selected_dice, hovered_dice, stashable_dice):
        dice_rects = []
        for i, (dice_key, pos) in enumerate(zip(dice_values, positions)):
            dice_surface = self.dice_surfaces['snaptray'][dice_key]
            
            angle = pos[2]
            rotated_surface = pygame.transform.rotate(dice_surface, angle)
            dice_rect = rotated_surface.get_rect(center=(pos[0] + self.dice_size['snaptray'] // 2, pos[1] + self.dice_size['snaptray'] // 2))
            self.screen.blit(rotated_surface, dice_rect)
            
            if i in selected_dice:
                selected_surface = pygame.transform.rotate(self.dice_surfaces['snaptray']['selected'], angle)
                selected_rect = selected_surface.get_rect(center=dice_rect.center)
                self.screen.blit(selected_surface, selected_rect)
            
            if i in hovered_dice:
                hover_surface = pygame.transform.rotate(self.dice_surfaces['snaptray']['hover'], angle)
                hover_rect = hover_surface.get_rect(center=dice_rect.center)
                self.screen.blit(hover_surface, hover_rect)
            
            dice_rects.append(dice_rect)
        return dice_rects

    def render_dice_in_stash(self, dice_values, rect):
        x, y = rect.left + 10, rect.top + 30
        for dice_info in dice_values:
            if dice_info.startswith("<dice>") and dice_info.endswith("</dice>"):
                color, value = dice_info[6:-7].lower().split('_')  # Convert to lowercase
                dice_key = f'{color}_{value}'
                dice_surface = self.dice_surfaces['stash'][dice_key]
                self.screen.blit(dice_surface, (x, y))
                x += self.dice_size['stash'] + 5
                if x > rect.right - self.dice_size['stash']:
                    x = rect.left + 10
                    y += self.dice_size['stash'] + 5

    def render_dice_in_log(self, surface, dice_info, x, y):
        """
        Render a dice image in the game log.
        
        Args:
            surface: Surface to render on
            dice_info: Dice info string (format: "white_4" or "green_6")
            x: X position
            y: Y position
            
        Returns:
            Updated x position after rendering
        """
        try:
            # Parse dice_info format: "white_4" or "green_6"
            dice_info = dice_info.lower().strip()
            parts = dice_info.split('_')
            
            if len(parts) != 2:
                # Invalid format, return without rendering
                return x
            
            color, value_str = parts
            
            # Validate value
            value = int(value_str)
            if value < 1 or value > 6:
                return x
            
            # Build the dice key for the surfaces dictionary
            dice_key = f'{color}_{value}'
            
            # Get the correct dice image from dice_surfaces['log']
            dice_surface = self.dice_surfaces['log'][dice_key]
            
            # Render the dice image
            surface.blit(dice_surface, (x, y))
            
            # Return new x position (dice width + spacing)
            return x + self.dice_size['log'] + 5
            
        except (KeyError, IndexError, ValueError) as e:
            # If image not found or parsing failed, skip rendering
            print(f"Warning: Could not render dice '{dice_info}': {e}")
            return x
