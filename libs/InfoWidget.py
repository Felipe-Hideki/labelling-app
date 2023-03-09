from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QCursor

from libs.MainWindowManager import MainWindowManager

class InfoWidget(QWidget):
    RANGE_TO_CHANGE_SIZE = 30

    def __init__(self, parent):
        super().__init__(parent)
        self.v_layout = QVBoxLayout()
        self.v_layout.setAlignment(Qt.AlignTop)

        self.v_layout.setContentsMargins(0, 0, 0, 0)

        MainWindowManager.instance().OnMouseMove.connect(self.On_mouse_move)

        self.setLayout(self.v_layout)
    
    def On_mouse_move(self):
        mousepos = self.mapFromGlobal(QCursor.pos()) + 6

        print(f"Mouse pos: {mousepos.x()} | Widget pos: {self.pos().x()}")
        print(f"Range: {int(self.RANGE_TO_CHANGE_SIZE / 2)} | {int(self.RANGE_TO_CHANGE_SIZE / 2)}")

        if mousepos.x() < self.pos().x() + int(self.RANGE_TO_CHANGE_SIZE / 2) and mousepos.x() > self.pos().x() -  int(self.RANGE_TO_CHANGE_SIZE / 2):
            print("setting cursor")
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        else:
            print("Restore cursor")
            QApplication.setOverrideCursor(Qt.ArrowCursor)
    def change_size(self, width: int):
        self.setFixedWidth(width)