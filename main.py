from sys import argv
from cProfile import Profile

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from libs.canvas.CanvasWin import CanvasWin as Canvas
from libs.widgets.setScale import setScale
from libs.widgets.MainWindowManager import MainWindowManager
from libs.widgets.MenuBar import MenuBar
from libs.widgets.InfoWidget import InfoWidget
from libs.widgets.ShapesList import ShapeList
from libs.widgets.FileListWidget import FileListWidget
from libs.handlers.MouseManager import MouseManager
from libs.handlers.keyboard.KeyHandler import KeyHandler
from libs.standalones.PersistentData import PersistentData
from libs.standalones.Files_Manager import Files_Manager

__appname__ = "labelImg"
        
class MainWindow(QMainWindow):
    __instance = None

    @classmethod
    def instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        super().__init__()
        MainWindow.__instance = self

        MouseManager()

        self.setWindowTitle(__appname__)
        # Standalones
        self.keyHandler = KeyHandler(self)
        self.__settings = PersistentData()
        self.files_manager = Files_Manager()

        # Menu bar
        self.setMenuBar(MenuBar.instance())

        # Setting up files_manager
        self.files_manager.window = self

        # Main widget
        self.mainWidget = MainWindowManager(parent=self)

        # Windows
        self.info_widget = InfoWidget(self)
        self.canvas = Canvas(parent=self)

        # Setting up the main window
        self.mainWidget.set_left(self.canvas)
        self.mainWidget.set_right(self.info_widget)

        # Utiliies
        self.shapes_list = ShapeList(self.info_widget)
        self.filelist = FileListWidget(self.info_widget)
        self.set_scale = setScale(self.canvas)
        #self.mouseTracker = MousePos()
        #self.viewportLogger = CoordinatesLog()

        # Setting up the main window
        self.mainWidget.move(0, self.menuBar().sizeHint().height())

        # Setting up the right window
        self.info_widget.v_layout.addWidget(self.set_scale)
        self.info_widget.v_layout.addWidget(self.shapes_list)
        self.info_widget.v_layout.addWidget(self.filelist)
        #self.win1.v_layout.addWidget(self.mouseTracker)
        #self.win1.v_layout.addWidget(self.viewportLogger)

        super().resize(800, 600)
        self.showMaximized()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.keyHandler.save()
        self.__settings.save()
        return super().closeEvent(a0)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = self.size()
        width = size.width()
        height = size.height()
        
        try:
            self.mainWidget.setFixedSize(size)
            self.canvas.setFixedHeight(height)
            self.info_widget.setMaximumWidth(int(width*.2))
            self.info_widget.setFixedHeight(height)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    profiler = Profile()
    profiler.enable()
    app = QApplication(argv)
    app.setApplicationName = __appname__

    win = MainWindow()
    exitcode = app.exec()
    profiler.dump_stats("./stats")
    profiler.disable()
    exit(exitcode)