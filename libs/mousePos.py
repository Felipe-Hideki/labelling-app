from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QTimer, QSize

from libs.CanvasHelper import CanvasHelper as helper
from libs.Canvas import Canvas

class MousePos(QWidget):
    def __init__(self):
        super().__init__()
        self.mousePos = QLabel(self)
        self.mousePos.resize(200, 20)

        self.relativePos = QLabel(self)
        self.relativePos.resize(200, 20)

        self.viewport = QLabel(self)
        self.viewport.resize(200, 20)
        self.on_timer_ends()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_ends)
        self.timer.start(50)

        vl = QVBoxLayout()
        vl.addWidget(self.mousePos)
        vl.addWidget(self.relativePos)
        vl.addWidget(self.viewport)

        self.setLayout(vl)     

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)   

    def sizeHint(self) -> QSize:
        return QSize(200, 20)

    def on_timer_ends(self):
        cursor = QCursor.pos()
        relative_pos = helper.relative_pos(cursor, Canvas.instance().get_origin().as_qpoint())

        self.mousePos.setText(f"Mouse position: {cursor.x()}, {cursor.y()}")
        self.relativePos.setText(f"Mouse relative position: {relative_pos.x}, {relative_pos.y}")
        self.viewport.setText(f"Viewport: {Canvas.instance().viewport_offset.x}, {Canvas.instance().viewport_offset.y}")