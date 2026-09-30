import pygame
from game.game_engine import GameEngine


def main():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode((1000, 560))
    pygame.display.set_caption("Neon Stride | Endless Runner")
    clock = pygame.time.Clock()
    engine = GameEngine(*screen.get_size())
    while engine.running:
        dt = min(clock.tick(120) / 1000, 0.1)
        for event in pygame.event.get():
            engine.handle_event(event)
        engine.update(dt)
        engine.render(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
