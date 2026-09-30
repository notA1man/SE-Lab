import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import unittest
import pygame
from game.game_engine import GameEngine, DIFFICULTIES, swept_collision
from game.obstacle import Obstacle


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.mixer.pre_init(44100, -16, 1)
        pygame.init()
        cls.screen = pygame.display.set_mode((1000, 560))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.game = GameEngine(1000, 560)
        self.game.start("Medium")

    def test_tunneling_and_airborne_clearance(self):
        player = pygame.Rect(150, 416, 32, 44)
        before, after = pygame.Rect(250, 416, 28, 44), pygame.Rect(80, 416, 28, 44)
        self.assertTrue(swept_collision(player, player, before, after))
        airborne = player.move(0, -100)
        self.assertFalse(swept_collision(airborne, airborne, before, after))

    def test_collision_freezes_and_replay_resets(self):
        self.game.score = 7
        self.game.obstacles = [Obstacle(175, self.game.ground_y, 390)]
        self.game.update()
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.best["Medium"], 7)
        position = self.game.player.y
        self.game.update(0.1)
        self.assertEqual(self.game.player.y, position)
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3))
        self.assertEqual(self.game.difficulty, "Hard")
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.obstacles, [])

    def test_scoring_once_and_jump(self):
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w))
        self.game.update(0.1)
        self.assertFalse(self.game.player.on_ground)
        self.game.obstacles = [Obstacle(110, self.game.ground_y, self.game.speed)]
        self.game.update()
        self.assertEqual(self.game.score, 1)
        self.game.update()
        self.assertEqual(self.game.score, 1)

    def test_difficulties_speed_cap_pause_and_render(self):
        for difficulty, (speed, interval, cap) in DIFFICULTIES.items():
            self.game.start(difficulty)
            self.assertEqual((self.game.speed, self.game.spawn_interval), (speed, interval))
            self.game.speed = cap + 1000
            self.game.update()
            self.assertEqual(self.game.speed, cap)
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p))
        distance = self.game.distance
        self.game.update(0.1)
        self.assertEqual(self.game.distance, distance)
        for state in ("menu", "playing", "paused", "over"):
            self.game.state = state
            self.game.render(self.screen)

    def test_frame_rate_independent_physics(self):
        from game.player import Player
        positions = []
        for fps in (30, 60, 120):
            player = Player(150, 460)
            player.jump()
            for _ in range(fps // 2):
                player.update(1 / fps)
            positions.append(player.y)
        self.assertAlmostEqual(max(positions), min(positions), places=6)

    def test_sounds_and_exit(self):
        self.assertEqual(set(self.game.sound.effects), {"jump", "score", "over"})
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
        self.assertTrue(self.game.sound.muted)
        self.game.state = "over"
        self.game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.assertFalse(self.game.running)

    def test_skyline_continuity_across_wrap(self):
        for layer in (0.15, 0.3):
            self.game.distance = 99 / layer
            before = list(self.game.skyline_buildings(layer))
            self.game.distance = 101 / layer
            after = list(self.game.skyline_buildings(layer))
            for x, height in before:
                if 0 < x < self.game.width:
                    self.assertIn((x - 2, height), after)

    def test_jump_dust_expires_before_apex_and_score_has_no_burst(self):
        self.game.jump_buffer = 0.12
        for _ in range(21):
            self.game.update(1 / 60)
        self.assertFalse(self.game.player.on_ground)
        self.assertEqual(self.game.particles, [])
        self.game.obstacles = [Obstacle(110, self.game.ground_y, self.game.speed)]
        self.game.update()
        self.assertEqual(self.game.score, 1)
        self.assertGreater(self.game.score_flash, 0)
        self.assertEqual(self.game.particles, [])


if __name__ == "__main__":
    unittest.main()
