from enum import Enum

from PyQt5.QtWidgets import QWidget, QAction, QMenu, QMenuBar

class actions(Enum):
    file = 0
    edit = 1

class fileMenu(Enum):
    open = 0
    exit = 1

class editMenu(Enum):
    create = 0
    delete = 1

class MenuBar(QMenuBar):
    _instance = None

    def __init__(self, parent: QWidget):
        super().__init__()

        self.file_menu = QMenu("File", parent)

        open_action = QAction("Open", parent)
        exit_action = QAction("Exit", parent)

        self.actions_dict = {
            actions.file: {fileMenu.open: open_action, fileMenu.exit: exit_action},
            }

        self.file_menu.addActions(self.actions_dict[actions.file].values())

        self.addMenu(self.file_menu)

        MenuBar._instance = self

    @classmethod
    def instance(cls):
        return cls._instance
