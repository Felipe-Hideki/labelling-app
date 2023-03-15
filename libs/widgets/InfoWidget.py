from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

from libs.handlers.MouseManager import MouseManager

class InfoWidget(QWidget):
    RANGE_TO_CHANGE_SIZE = 15

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.v_layout = QVBoxLayout()
        self.v_layout.setAlignment(Qt.AlignTop)

        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.cursor_set = False
        self.moving = False

        self.mm = MouseManager.instance()
        self.mm.OnMove.connect(self.__OnMouseMove)
        self.mm.OnClick.connect(self.__OnMouseClick)
        self.mm.OnRelease.connect(self.__OnMouseRelease)

        self.setLayout(self.v_layout)

    def __in_range(self, pos: int):
        return pos > -int(InfoWidget.RANGE_TO_CHANGE_SIZE / 2) and \
              pos < int(InfoWidget.RANGE_TO_CHANGE_SIZE / 2)

    def __OnMouseMove(self, event: QMouseEvent):
        mouseX = self.mapFromGlobal(event.globalPos()).x() + 6
        if self.moving:
            delta = self.x() - event.globalX() - 6
            self.setFixedWidth(self.width() + delta)
            return
        
        if not self.cursor_set and self.__in_range(mouseX):
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
            self.cursor_set = True
        elif self.cursor_set and not self.__in_range(mouseX):
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.cursor_set = False


    def __OnMouseClick(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.cursor_set:
            self.moving = True

    def __OnMouseRelease(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.moving = False