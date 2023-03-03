from PyQt5.QtWidgets import *
from libs.Canvas import Canvas

class setScale(QWidget):
    def __init__(self, canvas: Canvas):
        super().__init__()
        self.canvas = canvas
        self.label = QLabel()
        self.label.setText("set scale: ")
        self.input = QLineEdit()
        
        def on_edit_end():
            try:
                self.canvas.set_scale(float(self.input.text()))
                self.input.setText('')
            except Exception as e:
                print(e)
                return
        self.input.editingFinished.connect(on_edit_end)

        self.qh_layout = QHBoxLayout()
        self.qh_layout.addWidget(self.label)
        self.qh_layout.addWidget(self.input)
        self.setLayout(self.qh_layout)