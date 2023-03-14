from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from libs.Standalones.Files_Manager import Files_Manager
from libs.Widgets.ShapesListItem import ShapesListItem
from libs.Canvas.CanvasWin import CanvasWin
from libs.Canvas.Shape import Shape

class ShapeList(QWidget):
    __instance = None
    def instance(cls):
        return cls.__instance
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.v_layout = QVBoxLayout()

        self.label = QLabel("Label List", self)

        self.__list = QListWidget(self)
        self.__shapes_list: dict[Shape, ShapesListItem] = {}

        self.__list.setSortingEnabled(True)
        self.__list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__list.selectionModel().selectionChanged.connect(self.__selection_changed)

        canvas = CanvasWin.instance()

        canvas.OnAddShape.connect(self.add_shape)
        canvas.OnRemoveShape.connect(self.remove_shapes)
        canvas.OnSelectShape.connect(self.__selected_shape)
        canvas.OnDeselectShape.connect(self.__deselected_shape)
        canvas.OnChangedShapes.connect(self.__changed_shapes)
        

        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.__list)
        self.from_inside = False

        self.setLayout(self.v_layout)
        ShapeList.__instance = self

    @pyqtSlot(Shape)
    def __selected_shape(self, shape: Shape):
        if shape not in self.__shapes_list:
            return
        self.from_inside = True
        self.__shapes_list[shape].setSelected(True)
    
    @pyqtSlot(Shape)
    def __deselected_shape(self, shape: Shape):
        if shape not in self.__shapes_list:
            return
        self.from_inside = True
        self.__shapes_list[shape].setSelected(False)

    @pyqtSlot(QItemSelection, QItemSelection)
    def __selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if self.from_inside:
            self.from_inside = False
            return
        if not selected.isEmpty():
            [self.__list.itemFromIndex(index).OnSelected() for index in selected.indexes()]
        
        if not deselected.isEmpty():
            [self.__list.itemFromIndex(index).OnDeselected() for index in deselected.indexes()]


    @pyqtSlot(list)
    def __changed_shapes(self, shapes: list[Shape]):
        self.__shapes_list.clear()
        self.__list.clear()

        for shape in shapes:
            self.add_shape(shape)

    def __rem_shape(self, shape: Shape):
        self.__list.takeItem(self.__list.row(self.__shapes_list[shape]))
        del self.__shapes_list[shape]

    def add_shape(self, shape: Shape):
        list_item = ShapesListItem(shape)

        self.__shapes_list[shape] = list_item
        self.__list.addItem(list_item)
    
    def remove_shapes(self, shapes: list[Shape]):
        [self.__rem_shape(shape) for shape in shapes]