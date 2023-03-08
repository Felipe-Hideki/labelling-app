import time

from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QTimer, QSize

from libs.Canvas import Canvas
from libs.Vector import Vector2Int
from libs.keyHandler import keyHandler as keyboard

class MousePos(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timer_ends)
        self.timer.start(1)

        self.framerateTimer = QTimer(self)
        self.framerateTimer.timeout.connect(self.update_frame)
        self.framerateTimer.start(int(1000/60))
        self.start_time = time.monotonic()
        self.num_frames = 0

        self.mousePos = QLabel(self)
        self.mousePos.resize(200, 20)

        self.relativePos = QLabel(self)
        self.relativePos.resize(200, 20)
        
        self.fps = QLabel(self)
        self.fps.resize(200, 20)

        self.key_pressed = QLabel(self)
        self.key_pressed.resize(200, 20)

        self.shape_count = QLabel(self)
        self.shape_count.resize(200, 20)
        keyboard.instance().bind_to("create-shape", self.has_pressed)
        self.on_timer_ends()

        vl = QVBoxLayout()
        vl.addWidget(self.mousePos)
        vl.addWidget(self.relativePos)
        vl.addWidget(self.fps)
        vl.addWidget(self.key_pressed)
        vl.addWidget(self.shape_count)

        self.setLayout(vl)     

        self.key_pressed.setText("Key pressed: None")
        Canvas.instance().on_add_shape.connect(self.on_shape_add)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)   

    def on_shape_add(self, shape):
        self.shape_count.setText(f"Shape count: {len(Canvas.instance().shapes)}")

    def has_pressed(self): 
        if self.key_pressed.text() == "Key pressed: W":
            self.key_pressed.setText("Key pressed: None")
        else:
            self.key_pressed.setText("Key pressed: W")

    def update_frame(self):
        self.num_frames += 1

    def get_frame_rate(self):
        if self.num_frames % 60*5 == 0:
            self.start_time = time.monotonic()
            self.num_frames = 1
            return 1
        elapsed_time = time.monotonic() - self.start_time
        frame_rate = self.num_frames / elapsed_time
        return frame_rate

    def sizeHint(self) -> QSize:
        return QSize(200, 20)

    def on_timer_ends(self):
        try:
            canvas = Canvas.instance()
            cursor = Vector2Int(canvas.mapFromGlobal(QCursor.pos()))
            #relative_pos = helper.relative_pos(canvas.viewport.to_global(cursor), canvas.rect_to_draw.topLeft())
            relative_pos = canvas.viewport.pos() + cursor

            self.mousePos.setText(f"Mouse position: {cursor.x}, {cursor.y}")
            self.relativePos.setText(f"Mouse relative position: {relative_pos.x}, {relative_pos.y}")

            self.fps.setText(f"FPS: {self.get_frame_rate():.2f}")
        except Exception as e:
            print(e)