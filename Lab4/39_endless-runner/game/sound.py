"""Synthesized feedback with graceful fallback when audio is unavailable."""
from array import array
import math
import pygame


class SoundBank:
    def __init__(self):
        self.muted = False
        self.effects = {}
        if not pygame.mixer.get_init():
            return
        rate, _, channels = pygame.mixer.get_init()
        for name, notes in {"jump": (440, 660), "score": (740, 988),
                            "over": (330, 220, 110)}.items():
            samples = array("h")
            for frequency in notes:
                count = int(rate * 0.09)
                for i in range(count):
                    envelope = min(i / (rate * 0.005), 1) * (1 - i / count) ** 2
                    value = int(6500 * envelope * math.sin(2 * math.pi * frequency * i / rate))
                    samples.extend([value] * channels)
            self.effects[name] = pygame.mixer.Sound(buffer=samples)

    def play(self, name):
        if not self.muted and name in self.effects:
            self.effects[name].play()
