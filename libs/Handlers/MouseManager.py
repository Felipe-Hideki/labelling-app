from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication

class MouseManager(QObject):
    OnMove = pyqtSignal(QMouseEvent)
    OnClick = pyqtSignal(QMouseEvent)
    OnRelease = pyqtSignal(QMouseEvent)

    __instance = None

    @classmethod
    def instance(cls):
        return MouseManager.__instance

    def __init__(self):
        super().__init__()

        self.last_pos = QPoint(0, 0)
        self.current_pos = QPoint(0, 0)

        self.mousePress = {
            Qt.LeftButton: False,
            Qt.RightButton: False,
            Qt.MiddleButton: False
        }

        QApplication.instance().installEventFilter(self)

        MouseManager.__instance = self

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QEvent.MouseMove:
            self.current_pos = a1.globalPos()
            if self.last_pos != self.current_pos:
                self.OnMove.emit(a1)
                self.last_pos = self.current_pos
        if a1.type() == QEvent.MouseButtonPress:
            if a1.button() in self.mousePress.keys() and not self.mousePress[a1.button()]:
                self.mousePress[a1.button()] = True
                self.OnClick.emit(a1)
            
        if a1.type() == QEvent.MouseButtonRelease:
            if a1.button() in self.mousePress.keys() and self.mousePress[a1.button()]:
                self.mousePress[a1.button()] = False
                self.OnRelease.emit(a1)

        return super().eventFilter(a0, a1)