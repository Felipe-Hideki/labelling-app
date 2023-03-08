from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QTimer, QSize

from libs.CanvasHelper import CanvasHelper as helper
from libs.Canvas import Canvas
from libs.Vector import Vector2Int

class CoordinatesLog(QWidget):
    def __init__(self):
        super().__init__()
        self.viewport = QLabel(self)
        self.viewport.resize(200, 20)
        
        self._min = QLabel(self)
        self._min.resize(200, 20)
        
        self._max = QLabel(self)
        self._max.resize(200, 20)
        
        self.cs_min = QLabel(self)
        self.cs_min.resize(200, 20)

        self.cs_max = QLabel(self)
        self.cs_max.resize(200, 20)

        self.vsize = QLabel(self)
        self.vsize.resize(200, 20)

        self.pixmap_pos = QLabel(self)
        self.pixmap_pos.resize(200, 20)

        self.pixmap_size = QLabel(self)
        self.pixmap_size.resize(200, 20)

        self.pixmap_min = QLabel(self)
        self.pixmap_min.resize(200, 20)

        self.pixmap_max = QLabel(self)
        self.pixmap_max.resize(200, 20)
        self.on_timer_ends()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_ends)
        self.timer.start(50)

        vl = QVBoxLayout()
        vl.addWidget(self.viewport)
        vl.addWidget(self._min)
        vl.addWidget(self._max)
        vl.addWidget(self.vsize)
        vl.addWidget(self.cs_min)
        vl.addWidget(self.cs_max)
        vl.addWidget(self.pixmap_pos)
        vl.addWidget(self.pixmap_size)
        vl.addWidget(self.pixmap_min)
        vl.addWidget(self.pixmap_max)

        self.setLayout(vl)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)   

    def sizeHint(self) -> QSize:
        return QSize(200, 20)

    times = 0

    def on_timer_ends(self):
        try:
            canvas = Canvas.instance()
            viewport_size = canvas.viewport.size()
            pixmap_at =  -canvas.viewport.pos()
            pixmap_size = canvas.original_pixmap.size() * canvas.scale

            self.viewport.setText(f"Viewport: {canvas.viewport.pos().x}, {canvas.viewport.pos().y}")
            self._min.setText(f"Min: {canvas.viewport.to_global(canvas.viewport.top_left()).x}, {canvas.viewport.to_global(canvas.viewport.top_left()).y}")
            self._max.setText(f"Max: {canvas.viewport.to_global(canvas.viewport.bot_right()).x}, {canvas.viewport.to_global(canvas.viewport.bot_right()).y}")
            self.vsize.setText(f"Viewport size: {viewport_size.x}, {viewport_size.y}")
            self.cs_min.setText(f"CS Min: {canvas.cs.get_vertice(0).x}, {canvas.cs.get_vertice(0).y}")
            self.cs_max.setText(f"CS Max: {canvas.cs.get_vertice(2).x}, {canvas.cs.get_vertice(2).y}")
            self.pixmap_pos.setText(f"Pixmap pos: {pixmap_at.x}, {pixmap_at.y}")
            self.pixmap_size.setText(f"Pixmap size: {pixmap_size.width()}, {pixmap_size.height()}")
            self.pixmap_min.setText(f"Pixmap min: {(pixmap_at - pixmap_size/2).x}, {(pixmap_at - pixmap_size/2).y}")
            self.pixmap_max.setText(f"Pixmap max: {(pixmap_at + pixmap_size/2).x}, {(pixmap_at + pixmap_size/2).y}")
            
        except AttributeError as e:
            self.viewport.setText(f"Viewport: None, None")
            print(e)
            self.times += 1
            if self.times > 10:
                raise e