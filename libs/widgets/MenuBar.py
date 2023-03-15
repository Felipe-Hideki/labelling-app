from enum import Enum

from PyQt5.QtWidgets import QWidget, QAction, QMenu, QMenuBar, QApplication

from libs.standalones.Utils import Utils

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

        self.edit_menu = QMenu("Edit", parent)

        create_action = QAction("Create Shape", parent)
        delete_action = QAction("Delete Shape", parent)

        self.actions_dict = {
            actions.file: {fileMenu.open: open_action, fileMenu.exit: exit_action},
            actions.edit: {editMenu.create: create_action, editMenu.delete: delete_action}
            }

        self.file_menu.addActions(self.actions_dict[actions.file].values())
        self.edit_menu.addActions(self.actions_dict[actions.edit].values()) 

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)

        MenuBar._instance = self

    @classmethod
    def instance(cls):
        if not cls._instance:
            mainWindow = Utils.get_mainWindow()
            cls._instance = cls(mainWindow)
        return cls._instance
