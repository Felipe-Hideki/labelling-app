from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QTimer, QSize

from libs.CanvasHelper import CanvasHelper as helper

class Shape_Pos(QWidget):
    def __init__(self):
        super().__init__()
        self.shape_pos = QLabel(self)