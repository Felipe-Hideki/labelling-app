import os

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject

from libs.MenuBar import MenuBar, actions, fileMenu

class Files_Manager(QObject):
    OnLoadDir = pyqtSignal(str)

    __instance = None
    @classmethod
    def instance(cls):
        if Files_Manager.__instance is None:
            Files_Manager.__instance = Files_Manager()
        return Files_Manager.__instance

    def __init__(self):
        assert Files_Manager.__instance is None, "Files_Manager is a singleton class, use Files_Manager.instance() instead"
        super().__init__()
        self.__images = []
        self.__cur_img = -1
        self.__folder_size = 0
        self.window = None

        MenuBar.instance().actions_dict[actions.file][fileMenu.open].triggered.connect(self.open_folder)

        Files_Manager.__instance = self

    def open_folder(self, path):
        path = QFileDialog.getExistingDirectory(None, "Select Workfolder", "/home", QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        if len(path) == 0:
            return
        self.__images = [os.path.join(path, img) for img in os.listdir(path) if img.endswith(".jpg") or img.endswith(".png")]
        self.__folder_size = len(self.__images)
        self.__cur_img = 0 if self.__folder_size > 0 else -1
        img = self.__images[self.__cur_img] if self.__cur_img != -1 else ""
        self.OnLoadDir.emit(img)

    def close_folder(self):
        self.__images = []
        self.__cur_img = -1
        self.__folder_size = 0

    def next_img(self) -> str | None:
        if self.__cur_img + 1 >= self.__folder_size:
            return None
        self.__cur_img += 1
        return self.__images[self.__cur_img]

    def prev_img(self) -> str | None:
        if self.__cur_img - 1 < 0:
            return None
        self.__cur_img -= 1
        return self.__images[self.__cur_img]
    
    def cur_img(self) -> str:
        assert self.__cur_img != -1, "There is no workfolder opened"
        return self.__images[self.__cur_img]
    
    def folder_size(self):
        return self.__folder_size
    
    def img_index(self):
        return self.__cur_img