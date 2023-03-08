from sys import argv
from cProfile import Profile

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from libs.Canvas import Canvas
from libs.Shape import *
from libs.setScale import setScale
from libs.mainWidget import mainWidget
from libs.MenuBar import MenuBar
from libs.keyHandler import keyHandler, ActionBind
from libs.mousePos import MousePos
from libs.CoordinatesLog import CoordinatesLog
from libs.Files_Manager import Files_Manager

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

        self.setWindowTitle(__appname__)
        # Standalones
        self.keyHandler = keyHandler(self) if keyHandler.instance() is None else keyHandler.instance()
        self.setMenuBar(MenuBar.instance())
        self.files_manager = Files_Manager.instance()

        # Setting up files_manager
        self.files_manager.OnLoadDir.connect(self.load)
        
        # Windows
        self.win1 = QWidget(self)
        self.canvas = Canvas(parent=self)

        # Main widget
        self.mainWidget = mainWidget(parent=self)
        self.mainWidget.set_left(self.canvas)
        self.mainWidget.set_right(self.win1)

        # Utiliies
        self.set_scale = setScale(self.canvas)
        #self.mouseTracker = MousePos()
        #self.viewportLogger = CoordinatesLog()

        # Setting up the main window
        self.canvas.add_shape(Shape("aeiou", ShapePoints.square(Vector2Int(50, 50), 50)))
        self.mainWidget.move(0, self.menuBar().sizeHint().height())

        # Setting up the right window
        self.win1.v_layout = QVBoxLayout()
        self.win1.v_layout.setAlignment(Qt.AlignTop)
        self.win1.v_layout.addWidget(self.set_scale)
        #self.win1.v_layout.addWidget(self.mouseTracker)
        #self.win1.v_layout.addWidget(self.viewportLogger)
        self.win1.setLayout(self.win1.v_layout)

        # Load keybinds
        self.bind()

        self.resize(800, 600)
        self.showMaximized()

    def bind(self) -> None:
        self.keyHandler.bind_to(ActionBind.next_image, self.load_next)
        self.keyHandler.bind_to(ActionBind.prev_image, self.load_previous)
        self.keyHandler.bind_to(ActionBind.create_shape, self.canvas.create_mode)
        self.keyHandler.bind_to(ActionBind.delete_shape, self.canvas.delete)
        self.keyHandler.bind_to(ActionBind.multi_select, self.canvas.multi_select_mode)
        self.keyHandler.bind_to(ActionBind.move, self.canvas.move_mode)

    def load(self, file: str) -> None:
        assert len(file) > 0, "File path is empty"
        self.canvas.set_pixmap(file)

    def load_next(self) -> None:
        if file:= self.files_manager.next_img():
            self.canvas.set_pixmap(file)

    def load_previous(self) -> None:
        if file:= self.files_manager.prev_img():
            self.canvas.set_pixmap(file)

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
    profiler = Profile()
    profiler.enable()
    app = QApplication(argv)
    app.setApplicationName = __appname__

    win = MainWindow()
    exitcode = app.exec()
    profiler.dump_stats("./stats")
    profiler.disable()
    exit(exitcode)