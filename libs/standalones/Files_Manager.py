import os

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject

from libs.standalones.Utils import utils as utils
from libs.widgets.MenuBar import MenuBar, actions, fileMenu
from libs.handlers.keyboard.KeyHandler import KeyHandler, ActionBind
from libs.standalones.PersistentData import PersistentData, PersistentDataType


class Files_Manager(QObject):
    OnLoadDir = pyqtSignal(list)
    OnLoadImage = pyqtSignal(str)

    __instance = None
    @classmethod
    def instance(cls):
        return Files_Manager.__instance

    def __init__(self, parent=None, _appname="labelImg"):
        assert Files_Manager.__instance is None, "Files_Manager is a singleton class, use Files_Manager.instance() instead"
        super().__init__(parent=parent)
        self.__images = []
        self.__cur_img = -1
        self.__folder_size = 0
        self.window = parent
        self._appname = _appname

        MenuBar.instance().actions_dict[actions.file][fileMenu.open].triggered.connect(self.open_folder)

        kh = KeyHandler.instance()
        kh.bind_to(ActionBind.next_image, self.next_img)
        kh.bind_to(ActionBind.prev_image, self.prev_img)

        self.__settings = PersistentData.instance()

        Files_Manager.__instance = self

    def __load(self, index: int):
        self.__cur_img = index
        self.OnLoadImage.emit(self.__images[index])
        self.window.setWindowTitle(f"{self._appname} - {self.__cur_img+1} / {self.__folder_size}")

    def open_folder(self, path):
        path = QFileDialog.getExistingDirectory(None, "Select Workfolder", \
            self.__settings[PersistentDataType.last_folder], QFileDialog.ShowDirsOnly | \
            QFileDialog.DontUseNativeDialog)
        if len(path) == 0:
            return
        self.__images = [os.path.join(path, img) for img in os.listdir(path) if img.endswith(".jpg") or img.endswith(".png")]
        if len(self.__images) <= 0:
            return
        utils.natural_sort(self.__images, key=lambda s: s.lower())
        self.__folder_size = len(self.__images)
        self.__cur_img = 0
        
        self.OnLoadDir.emit(self.__images)
        self.__load(self.__cur_img)

        PersistentData.instance()[PersistentDataType.last_folder] = path

    def close_folder(self):
        self.__images = []
        self.__cur_img = -1
        self.__folder_size = 0

    def load_img(self, img: str | int):
        if type(img) == str:
            self.__load(self.__images.index(img))
            return
        self.__load(img)

    def next_img(self) -> str | None:
        if self.__cur_img + 1 >= self.__folder_size:
            return None
        self.__cur_img += 1
        self.__load(self.__cur_img)
        return self.__images[self.__cur_img]

    def prev_img(self) -> str | None:
        if self.__cur_img - 1 < 0:
            return None
        self.__cur_img -= 1
        self.__load(self.__cur_img)
        return self.__images[self.__cur_img]
    
    def cur_img(self) -> str | None:
        if self.__cur_img < 0:
            return None
        return self.__images[self.__cur_img]
    
    def folder_size(self):
        return self.__folder_size
    
    def img_index(self):
        return self.__cur_img

    def imgs(self) -> list[str]:
        return self.__images