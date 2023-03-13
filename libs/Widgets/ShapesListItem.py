from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from libs.Canvas.Shape import Shape
from libs.Canvas.CanvasWin import CanvasWin

class ShapesListItem(QListWidgetItem):
    def __init__(self, Shape: Shape):
        super().__init__()
        assert Shape, "Tried to initialize a shape item with a null shape"

        self.shape = Shape
        self.canvas = CanvasWin.instance()
        self.canvas.OnEndEdit.connect(self.OnNameEdit)

        self.setText(self.shape.name)

    def OnSelected(self) -> None:
        self.canvas.select(self.shape, True, True)

    def OnDeselected(self):
        if self.shape not in self.canvas.selected_shapes:
            return
        self.canvas.deselect(self.shape)

    def OnNameEdit(self, name: str):
        self.setText(self.shape.name)
