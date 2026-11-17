import pygame
from settings import *
from views import handle_events, draw_screen

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tower of Hanoi - Visualizer")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 16)

    while True:

        # Event processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            handle_events(event)

        # Frame rendering
        draw_screen(screen, font)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

    pygame.quit()
    exit()