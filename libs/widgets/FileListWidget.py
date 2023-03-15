from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from libs.standalones.Files_Manager import Files_Manager

class FileListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Loading flag
        self.from_inside = False

        # Layout
        self.v_layout = QVBoxLayout()
        
        # Widgets
        self.label = QLabel("File list", self)
        self.__list = QListWidget(self)

        # Add to layout
        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.__list)
        
        # Set layout 
        self.setLayout(self.v_layout)
        # Set Height
        self.setFixedHeight(400)
        
        # Add bottom margin
        cm = self.contentsMargins()
        self.setContentsMargins(cm.left(), cm.top(), cm.right(), 50)

        # File Manager configuration
        self.fm = Files_Manager.instance()
        self.fm.OnLoadDir.connect(self.OnLoadDir)
        self.fm.OnLoadImage.connect(self.OnLoadImg)
        self.__list.itemPressed.connect(self.OnClickItem)

    @pyqtSlot(QListWidgetItem)
    def OnClickItem(self, item: QListWidgetItem):
        self.from_inside = True
        self.fm.load_img(item.text())

    @pyqtSlot(list)
    def OnLoadDir(self, images: list[str]):
        self.__list.clear()

        for img in images:
            self.__list.addItem(img)

    @pyqtSlot(str)
    def OnLoadImg(self, img: str):
        if self.from_inside:
            self.from_inside = False
            return
        
        self.__list.clearSelection()
        self.__list.item(self.fm.img_index()).setSelected(True)