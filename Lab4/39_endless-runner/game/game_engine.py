import math
import pygame
from .player import Player
from .obstacle import Obstacle


def swept_collision(player_before, player_after, obstacle_before, obstacle_after):
    """Check the relative path of moving rectangles, preventing tunneling."""
    if player_before.colliderect(obstacle_before):
        return True
    entry, leave = -math.inf, math.inf
    for axis in ("x", "y"):
        size = "width" if axis == "x" else "height"
        p, o = getattr(player_before, axis), getattr(obstacle_before, axis)
        ps, os = getattr(player_before, size), getattr(obstacle_before, size)
        velocity = (getattr(player_after, axis) - p) - (getattr(obstacle_after, axis) - o)
        if velocity == 0:
            if p + ps <= o or o + os <= p:
                return False
            continue
        t1, t2 = (o - p - ps) / velocity, (o + os - p) / velocity
        entry, leave = max(entry, min(t1, t2)), min(leave, max(t1, t2))
    return entry <= leave and leave >= 0 and 0 <= entry <= 1


class GameEngine:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.ground_y = height - 100
        self.player = Player(150, self.ground_y)
        self.speed, self.max_speed = 390, 650
        self.spawn_interval, self.spawn_timer = 1.4, 0
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.running = True
        self.font = pygame.font.SysFont('consolas', 28)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif not self.game_over and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.player.jump()

    def update(self, dt=1 / 60):
        remaining = min(max(dt, 0), 0.1)
        while remaining > 1e-8 and not self.game_over:
            step = min(remaining, 1 / 120)
            remaining -= step
            self.speed = min(self.max_speed, self.speed + 9 * step)
            before = self.player.rect()
            self.player.update(step)
            self.spawn_timer += step
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer -= self.spawn_interval
                self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))
            for obstacle in self.obstacles:
                old = obstacle.rect()
                obstacle.speed = self.speed
                obstacle.move(step)
                if swept_collision(before, self.player.rect(), old, obstacle.rect()):
                    self.game_over = True
                    return
            for obstacle in self.obstacles:
                if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                    obstacle.scored = True
                    self.score += 1
            self.obstacles = [o for o in self.obstacles if not o.off_screen()]

    def render(self, screen):
        screen.fill((200, 220, 240))
        pygame.draw.line(screen, (120, 80, 40), (0, self.ground_y), (self.width, self.ground_y), 4)
        pygame.draw.rect(screen, (255, 255, 255), self.player.rect())
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, (30, 100, 30), obstacle.rect())
        screen.blit(self.font.render(f'Score: {self.score}', True, (0, 0, 0)), (20, 20))
