import unittest
import sys
import os

# Get the absolute path of the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the parent directory to the system path
sys.path.append(parent_dir)

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QWidget

from libs.Canvas.CanvasHelper import CanvasHelper

class testWidget(QWidget):
    def __init__(self, rect: QRect):
        super().__init__()
        self.settedrect = rect
    def rect(self) -> QRect:
        return self.settedrect

class TestCanvasHelper(unittest.TestCase):
    def test_relative_position(self):
        # Test relative position
        t = CanvasHelper.relative_pos(QPoint(5, 5), QPoint(10, 10))
        self.assertEqual(t == QPoint(5, 5), True)

if __name__ == '__main__':
    unittest.main()