from PyQt5.QtWidgets import QWidget, QVBoxLayout, QAbstractScrollArea, QScrollBar
from PyQt5.QtCore import QRect, Qt, QSize, QPoint, pyqtSignal, QObject

from libs.Vector import Vector2Int

class CanvasScrollManager(QObject):
    scroll_changed: pyqtSignal = pyqtSignal(Qt.Orientation, int)

    def __init__(self, canvas: QWidget):
        super().__init__(canvas)
        self.canvas = canvas

        self.hor_scroll = QScrollBar(Qt.Horizontal, canvas)
        self.ver_scroll = QScrollBar(Qt.Vertical, canvas)

        self.update()

        self.hor_scroll.valueChanged.connect(self.__on_scroll_hor)
        self.ver_scroll.valueChanged.connect(self.__on_scroll_ver)
        
    def update(self):
        width = 15

        pos: QPoint = self.canvas.rect().bottomLeft() - QPoint(0, width)
        size: QSize = QSize(int(self.canvas.rect().width() * .95), width)
        self.hor_scroll.setGeometry(QRect(pos.x(), pos.y(), size.width(), size.height()))

        pos = self.canvas.rect().topRight() - QPoint(width, 0)
        size = QSize(width, int(self.canvas.rect().height() * .95))
        self.ver_scroll.setGeometry(QRect(pos.x(), pos.y(), size.width(), size.height()))

        del pos, size

    def __on_scroll_hor(self, value: int):
        """
        Called when the scroll bar is moved.
        
        Args:
            value (int): The new value of the scroll bar.
        """
        self.scroll_changed.emit(Qt.Orientation.Horizontal, value)

    def __on_scroll_ver(self, value: int):
        """
        Called when the scroll bar is moved.
        
        Args:
            value (int): The new value of the scroll bar.
        """
        self.scroll_changed.emit(Qt.Orientation.Vertical, value)

    def on_scale(self, scale: float, pixmap_size: Vector2Int):
        """
        Called when the canvas is scaled.
        
        Args:
            scale (float): The new scale of the canvas.
            pixmap_size (Vector2Int): The size of the pixmap.
        """

        scaled_canvas: QSize = Vector2Int(self.canvas.size()).scaled(scale)
        _range = pixmap_size - scaled_canvas
        print(f"{_range=}")

        if _range.x > 0:
            self.hor_scroll.setRange(0, _range.x)
            self.hor_scroll.show()
        else:
            self.hor_scroll.hide()

        if _range.y > 0:
            self.ver_scroll.setRange(0, _range.y)
            self.ver_scroll.show()
        else:
            self.ver_scroll.hide()

        if self.hor_scroll.value() > _range.x:
            self.hor_scroll.setValue(_range.x)
        
        if self.ver_scroll.value() > _range.y:
            self.ver_scroll.setValue(_range.y)
    