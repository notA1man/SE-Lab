import pygame


class Player:
    def __init__(self, x, ground_y, width=32, height=44):
        self.x, self.ground_y = x, ground_y
        self.width, self.height = width, height
        self.y = ground_y - height
        self.vy = 0.0
        self.gravity = 2400.0
        self.jump_strength = -840.0
        self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False
            return True
        return False

    def update(self, dt=1 / 60):
        self.y += self.vy * dt + self.gravity * dt * dt / 2
        self.vy += self.gravity * dt
        if self.y >= self.ground_y - self.height:
            self.y = self.ground_y - self.height
            self.vy = 0
            self.on_ground = True

    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)
