from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLayout
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPalette, QColor, QMouseEvent, QCursor
from typing import overload

class MainWindowManager(QWidget):
    '''
    This class is used to manage the main window layout

    Args:
        parent (QWidget): The parent widget
    '''
    __instance = None

    @classmethod
    def instance(cls):
        return cls.__instance

    @overload
    def __init__(self, parent: QWidget): ...

    def __init__(self, **kwargs):
        super().__init__()
        self.setMouseTracking(True)
        if 'parent' in kwargs:
            self.setParent(kwargs['parent'])
        else:
            raise Exception("Parent need to be set")
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

        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.__mousepos = QPoint(0, 0)

        MainWindowManager.__instance = self

    def mouse_pos(self) -> QPoint:
        return self.__mousepos

    def size(self) -> QSize:
        return self.parent().size()
        

    def set_left(self, widget: QWidget) -> None:
        '''
        Set the left container widget

        Args:
            widget (QWidget): The widget to be set
        '''
        # Remove the old widget
        if self.left_container is not None:
            self.mainLayout.removeWidget(self.left_container)
        
        # Set the new widget and add it to the layout
        self.left_container = widget
        self.mainLayout.addWidget(self.left_container)

    def set_right(self, widget: QWidget) -> None:
        '''
        Set the right container widget

        Args:
            widget (QWidget): The widget to be set
        '''
        # Remove the old widget
        if self.left_container is not None:
            self.mainLayout.removeWidget(self.right_container)

        # Set the new widget and add it to the layout
        self.right_container = widget
        self.mainLayout.addWidget(self.right_container)