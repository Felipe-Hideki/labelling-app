from PyQt5.QtWidgets import QWidget, QAction, QMenu, QMenuBar, QApplication

from libs.Canvas import Canvas
from libs.Utils import Utils

class MenuBar(QMenuBar):
    _instance = None

    def __init__(self, parent: QWidget):
        super().__init__()

        self.file_menu = QMenu("File", parent)

        exit_action = QAction("Exit", parent)

        self.edit_menu = QMenu("Edit", parent)

        create_action = QAction("Create Shape", parent)
        delete_action = QAction("Delete Shape", parent)

        self.actions = {
            self.file_menu: [exit_action],
            self.edit_menu: [create_action, delete_action]
            }

        self.file_menu.addActions(self.actions[self.file_menu])
        self.edit_menu.addActions(self.actions[self.edit_menu]) 

        self.addMenu(self.file_menu)
        self.addMenu(self.edit_menu)

    @classmethod
    def instance(cls):
        if not cls._instance:
            mainWindow = Utils.get_mainWindow()
            cls._instance = cls(mainWindow)
        return cls._instance
