from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLayout
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPalette, QColor
from typing import overload

class mainWidget(QWidget):
    @overload
    def __init__(self, parent: QWidget=None): ...

    def __init__(self, **kwargs):
        super().__init__()
        if 'parent' in kwargs:
            self.setParent(kwargs['parent'])
        else:
            raise Exception()
        self.mainLayout = QHBoxLayout()
        self.left_container = QWidget()
        self.right_container = QWidget()

        pal = QPalette()
        pal.setColor(QPalette.Window, Qt.red)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        
        self.set_left(self.left_container)
        self.set_right(self.right_container)
        self.setLayout(self.mainLayout)

    def size(self) -> QSize:
        return self.parent().size()

    def set_left(self, widget: QWidget) -> None:
        if self.left_container is not None:
            self.mainLayout.removeWidget(self.left_container)
        self.left_container = widget
        self.mainLayout.addWidget(self.left_container)
        cmargins = self.mainLayout.contentsMargins()
        self.mainLayout.setContentsMargins(0, 0, cmargins.right(), cmargins.bottom())

    def set_right(self, widget: QWidget) -> None:
        if self.left_container is not None:
            self.mainLayout.removeWidget(self.right_container)
        self.right_container = widget
        self.mainLayout.addWidget(self.right_container)