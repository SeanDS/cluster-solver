from unittest import TestCase
import math
from ..geometry import Vector
from .configuration import Configuration

class TestConfiguration(TestCase):
    def setUp(self):
        self.p1 = Vector(0.0, 0.0)
        self.p2 = Vector(1.0, 0.0)
        self.c1 = Configuration({1: self.p1, 2: self.p2})

        self.p3 = Vector(0.0, 0.0)
        self.p4 = Vector(1.0, 0.0)
        self.c2 = Configuration({1: self.p3, 2: self.p4})

        self.p5 = Vector(0.0, 0.0)
        self.p6 = Vector(-1.0, 0.0)
        self.c3 = Configuration({1: self.p5, 2: self.p6})

        self.p7 = Vector(0.0, 0.0)
        self.p8 = Vector(1 / math.sqrt(2), 1 / math.sqrt(2))
        self.c4 = Configuration({1: self.p7, 2: self.p8})

        self.p9 = Vector(1.0, 2.0)
        self.p10 = Vector(2.0, 3.0)
        self.c5 = Configuration({1: self.p9, 2: self.p10})

        self.p11 = Vector(-1.0, -2.0)
        self.p12 = Vector(-2.0, -3.0)
        self.c6 = Configuration({1: self.p11, 2: self.p12})

    def test_equality(self):
        # c1 and c2 are identical
        self.assertEqual(self.c1, self.c2)

        # c1 is 180 degrees opposite c3
        self.assertEqual(self.c1, self.c3)

        # c1 is 45 degrees to c4
        self.assertEqual(self.c1, self.c4)

        # c5 is 180 degrees opposite c6
        self.assertEqual(self.c5, self.c6)
