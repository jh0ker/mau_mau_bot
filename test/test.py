import unittest
from game import Game
from player import Player


class Test(unittest.TestCase):

    game = None

    def setUp(self):
        self.game = Game()

    def test_insert(self):
        p0 = Player(self.game, "Player 0")
        p1 = Player(self.game, "Player 1")
        p2 = Player(self.game, "Player 2")

        self.assertEqual(p0, p2.next)
        self.assertEqual(p1, p0.next)
        self.assertEqual(p2, p1.next)

        self.assertEqual(p0.prev, p2)
        self.assertEqual(p1.prev, p0)
        self.assertEqual(p2.prev, p1)

    def test_reverse(self):
        p0 = Player(self.game, "Player 0")
        p1 = Player(self.game, "Player 1")
        p2 = Player(self.game, "Player 2")
        self.game.reverse()
        p3 = Player(self.game, "Player 3")

        self.assertEqual(p0, p3.next)
        self.assertEqual(p1, p2.next)
        self.assertEqual(p2, p0.next)
        self.assertEqual(p3, p1.next)

        self.assertEqual(p0, p2.prev)
        self.assertEqual(p1, p3.prev)
        self.assertEqual(p2, p1.prev)
        self.assertEqual(p3, p0.prev)
