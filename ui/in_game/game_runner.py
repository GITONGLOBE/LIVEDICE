import pygame

class GameRunner:
    @staticmethod
    def run_game(ui):
        clock = pygame.time.Clock()
        running = True
        fps = 60

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    ui.handle_event(event)

            ui.update()
            ui.draw()
            pygame.display.flip()
            clock.tick(fps)

        pygame.quit()