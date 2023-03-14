from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from libs.canvas.Shape import Shape
from libs.canvas.CanvasWin import CanvasWin

class ShapesListItem(QListWidgetItem):
    def __init__(self, Shape: Shape):
        super().__init__()
        assert Shape, "Tried to initialize a shape item with a null shape"

        self.shape = Shape
        self.canvas = CanvasWin.instance()
        self.canvas.OnEndEdit.connect(self.OnNameEdit)

        self.setText(self.shape.name)

    def OnSelected(self) -> None:
        if self.shape.selected:
            return
        self.shape.selected = True
        self.canvas.selected_shapes.append(self.shape)
        self.canvas.update()

    def OnDeselected(self):
        if self.shape not in self.canvas.selected_shapes:
            return
        self.shape.selected = False
        self.canvas.selected_shapes.remove(self.shape)
        self.canvas.update()

    def OnNameEdit(self, name: str):
        self.setText(self.shape.name)
