from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication, QSizePolicy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QCursor

from libs.MainWindowManager import MainWindowManager

class InfoWidget(QWidget):
    RANGE_TO_CHANGE_SIZE = 30

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.v_layout = QVBoxLayout()
        self.v_layout.setAlignment(Qt.AlignTop)

        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.cursor_set = False
        self.moving = False
        
        self.mainWindow = MainWindowManager.instance()

        self.mainWindow.OnMouseMove.connect(self.On_mouse_move)
        self.mainWindow.OnMouseClick.connect(self.On_mouse_click)

        self.setLayout(self.v_layout)
    
    def On_mouse_move(self):
        mousepos = self.mapFromGlobal(self.mainWindow.mouse_pos()) + QPoint(6, 0)

        if mousepos.x() < int(self.RANGE_TO_CHANGE_SIZE / 2) and mousepos.x() > - int(self.RANGE_TO_CHANGE_SIZE / 2):
            if self.moving:
                self.__change_size()
            if self.cursor_set:
                return
            self.cursor_set = True
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
            return
        if self.cursor_set:
            self.cursor_set = False
            QApplication.setOverrideCursor(Qt.ArrowCursor)

    def On_mouse_click(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.__change_size()
            return
        
    def On_mouse_released(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.moving = False
            return
        
    def __change_size(self):
        mousepos = self.mainWindow.mouse_pos() + QPoint(6, 0)

        delta = self.pos().x() - mousepos.x()
        print(self.parent().size().width() - self.sizeHint().width())
        self.setFixedWidth(self.width() + delta)