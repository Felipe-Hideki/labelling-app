import unittest
import sys
import os

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to the system path
sys.path.append(parent_dir)

from PyQt5.QtCore import QPoint, QSize, QRect

from libs.Standalones.Vector import Vector2Int

class TestVector(unittest.TestCase):
    def test_vector_constructor(self):
        # Test Vector2Int __init__ without arguments
        t = Vector2Int()
        self.assertEqual(t.x, 0)
        self.assertEqual(t.y, 0)

        # Test Vector2Int __init__ with x and y
        t = Vector2Int(1, 2)

        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 2)

        # Test Vector2Int __init__ with x and y as float
        t = Vector2Int(1.0, 2.0)

        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 2)

        # Test Vector2Int __init__ with Vector2Int
        t = [Vector2Int(1, 2), None]
        t[1] = Vector2Int(t[0])

        t[0].x = 2
        t[0].y = 3

        self.assertEqual(t[1].x, 1)
        self.assertEqual(t[1].y, 2)

        # Test Vector2Int __init__ with QPoint
        t = Vector2Int(QPoint(1, 2))

        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 2)

        # Test Vector2Int __init__ with QSize
        t = Vector2Int(QSize(1, 2))

        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 2)

    def test_vector_add(self):
        # Test Vector2Int __add__ with Vector2Int
        t = Vector2Int(1, 2) + Vector2Int(3, 4)

        self.assertEqual(t.x, 4)
        self.assertEqual(t.y, 6)

        # Test Vector2Int __add__ with QPoint
        t = Vector2Int(1, 2) + QPoint(3, 4)

        self.assertEqual(t.x, 4)
        self.assertEqual(t.y, 6)

        # Test Vector2Int __add__ with QSize
        t = Vector2Int(1, 2) + QSize(3, 4)

        self.assertEqual(t.x, 4)
        self.assertEqual(t.y, 6)

    def test_vector_sub(self):
        # Test Vector2Int __sub__ with Vector2Int
        t = Vector2Int(1, 2) - Vector2Int(3, 4)

        self.assertEqual(t.x, -2)
        self.assertEqual(t.y, -2)

        # Test Vector2Int __sub__ with QPoint
        t = Vector2Int(1, 2) - QPoint(3, 4)

        self.assertEqual(t.x, -2)
        self.assertEqual(t.y, -2)

        # Test Vector2Int __sub__ with QSize
        t = Vector2Int(1, 2) - QSize(3, 4)

        self.assertEqual(t.x, -2)
        self.assertEqual(t.y, -2)
    
    def test_vector_mul(self):
        # Test Vector2Int __mul__ with int
        t = Vector2Int(1, 2) * 3

        self.assertEqual(t.x, 3)
        self.assertEqual(t.y, 6)

        # Test Vector2Int __mul__ with float
        t = Vector2Int(1, 2) * 3.0

        self.assertEqual(type(t.x) is int, True)
        self.assertEqual(type(t.y) is int, True)
        self.assertEqual(t.x, 3)
        self.assertEqual(t.y, 6)
    
    def test_vector_div(self):
        # Test Vector2Int __div__ with int
        t = Vector2Int(1, 2) / 2

        self.assertEqual(t.x, 0)
        self.assertEqual(t.y, 1)

        # Test Vector2Int __div__ with float
        t = Vector2Int(1, 2) / 2.0

        self.assertEqual(type(t.x) is int, True)
        self.assertEqual(type(t.y) is int, True)
        self.assertEqual(t.x, 0)
        self.assertEqual(t.y, 1)
    
    def test_vector_eq(self):
        # Test Vector2Int __eq__ with Vector2Int
        t = Vector2Int(1, 2) == Vector2Int(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) == Vector2Int(2, 3)
        self.assertEqual(t, False)

        # Test Vector2Int __eq__ with QPoint
        t = Vector2Int(1, 2) == QPoint(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) == QPoint(2, 3)
        self.assertEqual(t, False)

        # Test Vector2Int __eq__ with QSize
        t = Vector2Int(1, 2) == QSize(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) == QSize(2, 3)
        self.assertEqual(t, False)

    def test_vector_ne(self):
        # Test Vector2Int __ne__ with Vector2Int
        t = Vector2Int(1, 2) != Vector2Int(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) != Vector2Int(2, 3)
        self.assertEqual(t, True)

        # Test Vector2Int __ne__ with QPoint
        t = Vector2Int(1, 2) != QPoint(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) != QPoint(2, 3)
        self.assertEqual(t, True)

        # Test Vector2Int __ne__ with QSize
        t = Vector2Int(1, 2) != QSize(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) != QSize(2, 3)
        self.assertEqual(t, True)

    def test_vector_lt(self):
        # Test Vector2Int __lt__ with Vector2Int
        t = Vector2Int(1, 2) < Vector2Int(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) < Vector2Int(2, 3)
        self.assertEqual(t, True)

        # Test Vector2Int __lt__ with QPoint
        t = Vector2Int(1, 2) < QPoint(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) < QPoint(2, 3)
        self.assertEqual(t, True)

        # Test Vector2Int __lt__ with QSize
        t = Vector2Int(1, 2) < QSize(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) < QSize(2, 3)
        self.assertEqual(t, True)
    
    def test_vector_le(self):
        # Test Vector2Int __le__ with Vector2Int
        t = Vector2Int(1, 2) <= Vector2Int(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) <= Vector2Int(2, 3)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) <= Vector2Int(0, 1)
        self.assertEqual(t, False)

        # Test Vector2Int __le__ with QPoint
        t = Vector2Int(1, 2) <= QPoint(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) <= QPoint(2, 3)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) <= QPoint(0, 1)
        self.assertEqual(t, False)

        # Test Vector2Int __le__ with QSize
        t = Vector2Int(1, 2) <= QSize(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) <= QSize(2, 3)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) <= QSize(0, 1)
        self.assertEqual(t, False)
    
    def test_vector_gt(self):
        # Test Vector2Int __gt__ with Vector2Int
        t = Vector2Int(1, 2) > Vector2Int(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) > Vector2Int(0, 1)
        self.assertEqual(t, True)

        # Test Vector2Int __gt__ with QPoint
        t = Vector2Int(1, 2) > QPoint(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) > QPoint(0, 1)
        self.assertEqual(t, True)

        # Test Vector2Int __gt__ with QSize
        t = Vector2Int(1, 2) > QSize(1, 2)
        self.assertEqual(t, False)
        t = Vector2Int(1, 2) > QSize(0, 1)
        self.assertEqual(t, True)
    
    def test_vector_ge(self):
        # Test Vector2Int __ge__ with Vector2Int
        t = Vector2Int(1, 2) >= Vector2Int(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) >= Vector2Int(0, 1)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) >= Vector2Int(2, 3)
        self.assertEqual(t, False)

        # Test Vector2Int __ge__ with QPoint
        t = Vector2Int(1, 2) >= QPoint(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) >= QPoint(0, 1)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) >= QPoint(2, 3)
        self.assertEqual(t, False)

        # Test Vector2Int __ge__ with QSize
        t = Vector2Int(1, 2) >= QSize(1, 2)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) >= QSize(0, 1)
        self.assertEqual(t, True)
        t = Vector2Int(1, 2) >= QSize(2, 3)
        self.assertEqual(t, False)
    
    def test_vector_abs(self):
        # Test Vector2Int __abs__
        t = abs(Vector2Int(-1, -2))
        self.assertEqual(t == Vector2Int(1, 2), True)
        t = abs(Vector2Int(1, -2))
        self.assertEqual(t == Vector2Int(1, 2), True)

    def test_vector_min_max(self):
        # Test Vector2Int min, max
        t = Vector2Int.get_min_max([Vector2Int(1, 2), Vector2Int(3, 4), Vector2Int(5, 6), Vector2Int(7, 8)])
        self.assertEqual(t[0] == Vector2Int(1, 2), True)
        self.assertEqual(t[1] == Vector2Int(7, 8), True)

    def test_vector_distance(self):
        # Test Vector2Int distance
        t = Vector2Int.distance(Vector2Int(2, 2), Vector2Int(2, 4))
        self.assertEqual(t, 2)
        
        t = Vector2Int.distance(Vector2Int(2, 2), Vector2Int(4, 4))
        self.assertAlmostEqual(t, 2.82, 1)

    def test_vector_magnitude(self):
        # Test Vector2Int magnitude
        t = Vector2Int.magnitude(Vector2Int(0, 2))
        self.assertEqual(t, 2)
        
        t = Vector2Int.magnitude(Vector2Int(2, 2))
        self.assertAlmostEqual(t, 2.82, 1)

    def test_vector_normalize(self):
        # Test Vector2Int normalize
        t = Vector2Int.normalize(Vector2Int(0, 2))
        self.assertEqual(t.x(), 0)
        self.assertEqual(t.y(), 1)
        
        t = Vector2Int.normalize(Vector2Int(2, 2))
        self.assertAlmostEqual(t.x(), 0.7, 1)
        self.assertAlmostEqual(t.y(), 0.7, 1)

        # Test Vector2Int normalized
        t = Vector2Int(0, 2).normalized()
        self.assertEqual(t.x(), 0)
        self.assertEqual(t.y(), 1)

        t = Vector2Int(2, 2).normalized()
        self.assertAlmostEqual(t.x(), 0.7, 1)
        self.assertAlmostEqual(t.y(), 0.7, 1)
        
    def test_vector_scale(self):
        # Test Vector2Int scale
        t = Vector2Int(2, 2)
        Vector2Int.scale(t, 2)
        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 1)

        t = Vector2Int(2, 2)
        Vector2Int.scale(t, 0.5)
        self.assertEqual(t.x, 4)
        self.assertEqual(t.y, 4)

        # Test Vector2Int scaled

        t = Vector2Int(2, 2).scaled(2)
        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 1)

        t = Vector2Int(2, 2).scaled(0.5)
        self.assertEqual(t.x, 4)
        self.assertEqual(t.y, 4)

    def test_vector_clip(self):
        # test Vector2Int clip with QRect
        t = [Vector2Int(2, 2), QRect()]
        t[1].setBottomRight(QPoint(1, 1))
        t[0].clip(t[1])
        self.assertEqual(t[0].x, 1)
        self.assertEqual(t[0].y, 1)

        t = [Vector2Int(2, 2), QRect()]
        t[1].setBottomRight(QPoint(3, 3))
        t[0].clip(t[1])
        self.assertEqual(t[0].x, 2)
        self.assertEqual(t[0].y, 2)

        # test Vector2Int clipped with Vector2Int, Vector2Int
        t = Vector2Int(2, 2)
        t.clip(Vector2Int(0, 0), Vector2Int(1, 1))
        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, 1)

        t = Vector2Int(2, 2)
        t.clip(Vector2Int(0, 0), Vector2Int(3, 3))
        self.assertEqual(t.x, 2)
        self.assertEqual(t.y, 2)

if __name__ == '__main__':
    unittest.main()