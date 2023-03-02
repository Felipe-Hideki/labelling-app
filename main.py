from sys import argv

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from libs.Canvas import Canvas
from libs.Shape import *
from libs.setScale import setScale
from libs.mainWidget import mainWidget
from libs.MenuBar import MenuBar
from libs.keyHandler import keyHandler
from libs.mousePos import MousePos

__appname__ = "labelImg"
        
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(__appname__)

        self.keyHandler = keyHandler(self) if keyHandler.instance() is None else keyHandler.instance()

        self.setMenuBar(MenuBar.instance())
        
        self.win1 = QWidget(self)

        self.canvas = Canvas(parent=self)

        self.mainWidget = mainWidget(parent=self)
        self.mainWidget.set_left(self.canvas)
        self.mainWidget.set_right(self.win1)

        self.set_scale = setScale(self.canvas)
        self.mouseTracker = MousePos()

        self.mainWidget.move(0, self.menuBar().sizeHint().height())

        self.win1.v_layout = QVBoxLayout()
        self.win1.v_layout.setAlignment(Qt.AlignTop)
        self.win1.v_layout.addWidget(self.set_scale)
        self.win1.v_layout.addWidget(self.mouseTracker)
        self.win1.setLayout(self.win1.v_layout)

        self.resize(800, 600)
        self.showMaximized()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.keyHandler.save()
        return super().closeEvent(a0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = self.size()
        width = size.width()
        height = size.height()
        
        try:
            self.mainWidget.setFixedSize(size)
            self.canvas.setFixedHeight(height)
            self.win1.setMaximumWidth(int(width*.2))
            self.win1.setFixedHeight(height)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    app = QApplication(argv)
    app.setApplicationName = __appname__

    win = MainWindow()
    app.exec()