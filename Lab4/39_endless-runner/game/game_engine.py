import math
import random
import pygame
from .player import Player
from .obstacle import Obstacle
from .sound import SoundBank

INK = (12, 17, 35)
WHITE = (234, 243, 255)
MUTED = (142, 160, 191)
CYAN = (65, 230, 220)
PINK = (255, 100, 150)
DIFFICULTIES = {"Easy": (300, 1.65, 540), "Medium": (390, 1.4, 650),
                "Hard": (480, 1.2, 760)}


def swept_collision(player_before, player_after, obstacle_before, obstacle_after):
    """Intersect moving AABBs using relative motion, including between frames."""
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
        self.running = True
        self.state = "menu"
        self.difficulty = "Medium"
        self.best = {name: 0 for name in DIFFICULTIES}
        self.sound = SoundBank()
        self.fonts = {size: pygame.font.SysFont("consolas", size, bold=size >= 28)
                      for size in (16, 20, 28, 40, 64)}
        self.time = 0
        self.buttons = []
        self.reset()

    @property
    def game_over(self):
        return self.state == "over"

    def reset(self):
        self.player = Player(150, self.ground_y)
        self.speed, self.spawn_interval, self.max_speed = DIFFICULTIES[self.difficulty]
        self.spawn_timer = 0
        self.obstacles = []
        self.particles = []
        self.score = 0
        self.distance = 0
        self.jump_buffer = 0
        self.score_flash = 0

    def start(self, difficulty):
        self.difficulty = difficulty
        self.reset()
        self.state = "playing"

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, action in self.buttons:
                if rect.collidepoint(event.pos):
                    if action == "quit":
                        self.running = False
                    else:
                        self.start(action)
                    break
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key == pygame.K_m:
            self.sound.muted = not self.sound.muted
        elif key == pygame.K_ESCAPE:
            if self.state == "playing":
                self.state = "paused"
            elif self.state == "paused":
                self.state = "playing"
            else:
                self.running = False
        elif key == pygame.K_p and self.state in ("playing", "paused"):
            self.state = "paused" if self.state == "playing" else "playing"
        elif self.state in ("menu", "over"):
            if key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.start(list(DIFFICULTIES)[key - pygame.K_1])
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start(self.difficulty)
        elif self.state == "playing" and key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.jump_buffer = 0.12

    def burst(self, x, y, color, count=12, dust=False):
        for _ in range(count):
            self.particles.append([x, y,
                                   random.uniform(-100, -30) if dust else random.uniform(-160, 160),
                                   random.uniform(-65, -20) if dust else random.uniform(-200, -40),
                                   0.18 if dust else 0.5, color])

    def update(self, dt=1 / 60):
        self.time += dt
        if self.state != "playing":
            return
        # Small steps preserve the jump arc during stalls; swept collision also
        # catches obstacles that cross the entire player between two positions.
        remaining = min(max(dt, 0), 0.1)
        while remaining > 1e-8 and self.state == "playing":
            step = min(remaining, 1 / 120)
            remaining -= step
            self._step(step)

    def _step(self, dt):
        self.score_flash = max(0, self.score_flash - dt)
        self.speed = min(self.max_speed, self.speed + 9 * dt)
        before = self.player.rect()
        if self.jump_buffer > 0 and self.player.jump():
            self.jump_buffer = 0
            self.sound.play("jump")
            self.burst(self.player.x + 16, self.ground_y, CYAN, 7, dust=True)
        self.jump_buffer = max(0, self.jump_buffer - dt)
        self.player.update(dt)
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            self.obstacles.append(Obstacle(self.width + 30, self.ground_y, self.speed,
                                           random.choice((26, 32, 40)), random.choice((36, 44, 52))))
        for obstacle in self.obstacles:
            old = obstacle.rect()
            obstacle.speed = self.speed
            obstacle.move(dt)
            if swept_collision(before, self.player.rect(), old, obstacle.rect()):
                self.state = "over"
                self.best[self.difficulty] = max(self.best[self.difficulty], self.score)
                self.sound.play("over")
                self.burst(self.player.x + 16, self.player.y + 22, PINK, 26)
                return
        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1
                self.sound.play("score")
                self.score_flash = 0.25
        self.obstacles = [o for o in self.obstacles if not o.off_screen()]
        self.distance += self.speed * dt
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 500 * dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]

    def text(self, screen, value, pos, size=20, color=WHITE, center=False):
        surface = self.fonts[size].render(str(value), True, color)
        screen.blit(surface, surface.get_rect(center=pos) if center else pos)

    def skyline_buildings(self, layer):
        """Keep building identity as it moves through and beyond the viewport."""
        scroll = self.distance * layer
        first = math.floor(scroll / 100) - 1
        for index in range(first, first + self.width // 100 + 3):
            yield round(index * 100 - scroll), 60 + (index * 37 % 95)

    def render(self, screen):
        screen.fill(INK)
        for y in range(0, self.ground_y, 3):
            fraction = y / self.ground_y
            pygame.draw.rect(screen, (int(12 + 14 * fraction), int(17 + 12 * fraction),
                                     int(35 + 22 * fraction)), (0, y, self.width, 3))
        pygame.draw.circle(screen, (50, 47, 84), (self.width - 185, 140), 64)
        pygame.draw.circle(screen, (78, 66, 112), (self.width - 185, 140), 48, 1)
        for layer, color in ((0.15, (31, 39, 66)), (0.3, (39, 48, 78))):
            for x, h in self.skyline_buildings(layer):
                pygame.draw.rect(screen, color, (x, self.ground_y - h, 75, h))
                pygame.draw.line(screen, (61, 68, 99), (x + 12, self.ground_y - h + 15),
                                 (x + 55, self.ground_y - h + 15), 2)
        pygame.draw.rect(screen, (16, 23, 40), (0, self.ground_y, self.width, 100))
        pygame.draw.line(screen, CYAN, (0, self.ground_y), (self.width, self.ground_y), 3)
        for i in range(-1, self.width // 60 + 2):
            x = int(i * 60 - self.distance % 60)
            pygame.draw.line(screen, (35, 61, 76), (x, self.ground_y + 4), (x - 40, self.height), 1)
        for y in (self.ground_y + 25, self.ground_y + 65):
            pygame.draw.line(screen, (35, 61, 76), (0, y), (self.width, y))
        for p in self.particles:
            pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), max(1, int(p[4] * 7)))
        r = self.player.rect()
        pygame.draw.ellipse(screen, (24, 44, 58), (r.x - 9, self.ground_y + 6, 52, 8))
        pygame.draw.rect(screen, CYAN, r, border_radius=7)
        pygame.draw.rect(screen, (22, 67, 84), (r.x + 6, r.y + 9, 26, 12), border_radius=4)
        pygame.draw.rect(screen, WHITE, (r.x + 19, r.y + 12, 10, 3), border_radius=1)
        for o in self.obstacles:
            pygame.draw.rect(screen, PINK, o.rect(), border_radius=4)
            pygame.draw.rect(screen, (92, 37, 66), o.rect().inflate(-8, -8), border_radius=2)
            pygame.draw.line(screen, PINK, (int(o.x + 6), int(o.y + 8)),
                             (int(o.x + o.width - 6), self.ground_y - 8), 3)
        self.text(screen, "NEON / STRIDE", (28, 24), 28, CYAN)
        self.text(screen, f"{self.score:03d}", (self.width - 130, 20), 40,
                  CYAN if self.score_flash > 0 else WHITE)
        self.text(screen, "CLEARED", (self.width - 132, 64), 16, MUTED)
        self.text(screen, f"{self.difficulty.upper()}  /  BEST {self.best[self.difficulty]}", (28, 62), 16, MUTED)
        self.text(screen, "SPACE / UP / W  jump     P / ESC  pause     M  sound " +
                  ("OFF" if self.sound.muted else "ON"), (28, self.height - 28), 16, MUTED)
        self.buttons = []
        if self.state in ("menu", "over", "paused"):
            veil = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            veil.fill((8, 12, 26, 200))
            screen.blit(veil, (0, 0))
            cx = self.width // 2
            panel = pygame.Rect(cx - 310, 110, 620, 350)
            pygame.draw.rect(screen, (22, 29, 49), panel, border_radius=18)
            pygame.draw.rect(screen, (56, 76, 99), panel, 1, border_radius=18)
            title = {"menu": "NEON STRIDE", "over": "RUN COMPLETE", "paused": "PAUSED"}[self.state]
            self.text(screen, title, (cx, 163), 40, CYAN, True)
            if self.state == "paused":
                self.text(screen, "Take a breath. Your run is waiting.", (cx, 240), 20, MUTED, True)
                self.text(screen, "Press P or ESC to resume", (cx, 315), 20, WHITE, True)
                return
            subtitle = (f"{self.score} obstacles cleared / best {self.best[self.difficulty]} ({self.difficulty})"
                        if self.state == "over" else "Find your rhythm. Clear the skyline.")
            self.text(screen, subtitle, (cx, 221), 20, MUTED, True)
            self.text(screen, "CHOOSE YOUR NEXT RUN", (cx, 264), 16, MUTED, True)
            mouse = pygame.mouse.get_pos()
            for i, name in enumerate(DIFFICULTIES):
                rect = pygame.Rect(cx - 270 + i * 185, 290, 170, 74)
                hover = rect.collidepoint(mouse)
                pygame.draw.rect(screen, (38, 68, 83) if hover else (31, 42, 65), rect, border_radius=10)
                pygame.draw.rect(screen, CYAN if hover else (65, 86, 112), rect, 1, border_radius=10)
                self.text(screen, f"{i + 1}  {name}", rect.center, 20, WHITE, True)
                self.buttons.append((rect, name))
            self.text(screen, "ENTER  replay current difficulty", (cx, 391), 16, MUTED, True)
            exit_rect = pygame.Rect(cx - 80, 414, 160, 30)
            self.text(screen, "ESC / Exit", exit_rect.center, 16, PINK, True)
            self.buttons.append((exit_rect, "quit"))
