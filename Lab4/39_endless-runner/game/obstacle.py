import pygame


class Obstacle:
    def __init__(self, x, ground_y, speed, width=28, height=44):
        self.x, self.y = float(x), ground_y - height
        self.width, self.height = width, height
        self.speed = speed
        self.scored = False

    def move(self, dt=1 / 60):
        self.x -= self.speed * dt

    def off_screen(self):
        return self.x + self.width < 0

    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)
