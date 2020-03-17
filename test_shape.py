from unittest import TestCase

from shape import Shape


class TestShape(TestCase):
    def test_paint(self):

        shape = Shape()
        self.assertEqual(shape.line_color, Shape.line_color)