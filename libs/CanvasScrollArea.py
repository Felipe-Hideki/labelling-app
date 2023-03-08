from PyQt5.QtWidgets import QWidget, QVBoxLayout, QAbstractScrollArea, QScrollBar
from PyQt5.QtCore import QRect, Qt, QSize, QPoint, pyqtSignal, QObject

from libs.Vector import Vector2Int

def get_canvas_style_sheet():
    return "QScrollBar\
        {\
        background: rgb(0, 0, 0)\
        }\
        QScrollBar::handle\
        {\
        background: rgb(25, 25, 25)\
        border-color: rgb(100, 100, 100)\
        }"

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

        self.hor_scroll.setStyleSheet(get_canvas_style_sheet())
        self.ver_scroll.setStyleSheet(get_canvas_style_sheet())

    def update(self):
        width = 15

        pos = self.canvas.rect().topRight() - QPoint(width-1, 0)
        size = QSize(width, self.canvas.rect().height() - 20 - width)
        self.ver_scroll.setGeometry(QRect(pos.x(), pos.y(), size.width(), size.height()))

        pos = self.ver_scroll.geometry().bottomRight() + QPoint(-self.canvas.rect().width(), 1)
        size = QSize(self.canvas.rect().width() - width + 1, width)
        self.hor_scroll.setGeometry(QRect(pos.x(), pos.y(), size.width(), size.height()))

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

    def on_viewport_move(self, viewport_pos: Vector2Int):
        """
        Called when the viewport is moved.
        
        Args:
            viewport_pos (Vector2Int): The new position of the viewport.
        """
        self.hor_scroll.setValue(viewport_pos.x)
        self.ver_scroll.setValue(viewport_pos.y)


    def on_scale(self, cs_size: Vector2Int, viewport_size: Vector2Int, viewport_pos: Vector2Int):
        """
        Called when the canvas is scaled.
        
        Args:
            scale (float): The new scale of the canvas.
            pixmap_size (Vector2Int): The size of the pixmap.
        """

        __move_space = (cs_size - viewport_size)
        _range = __move_space / 2

        if __move_space.x > 0:
            self.hor_scroll.setRange(-_range.x, _range.x)
            self.hor_scroll.setPageStep(int(__move_space.x * .3))
            self.hor_scroll.show()
        else:
            self.hor_scroll.hide()

        if __move_space.y > 0:
            self.ver_scroll.setRange(-_range.y, _range.y)
            self.ver_scroll.setPageStep(int(__move_space.y * .3))
            self.ver_scroll.show()
        else:
            self.ver_scroll.hide()

        if self.hor_scroll.value() > _range.x or self.hor_scroll.value() < -_range.x:
            self.hor_scroll.setValue(viewport_pos.x)
        
        if self.ver_scroll.value() > _range.y or self.hor_scroll.value() < -_range.y:
            self.ver_scroll.setValue(viewport_pos.y)
    