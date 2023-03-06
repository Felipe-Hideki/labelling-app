from pympler import asizeof
from typing import overload

from PyQt5.QtCore import Qt, QSize, QPointF, QPoint, QRect, pyqtSignal
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QColor, QPalette, QPainter, QPaintEvent, QMouseEvent, QWheelEvent, QPixmap, QImage, QPen, QResizeEvent, QCursor, QBrush

from libs.ShapePoints import ShapePoints
from libs.Shape import Shape
from libs.Vector import Vector2Int
from libs.CanvasHelper import CanvasHelper as helper
from libs.keyHandler import keyHandler
from libs.CanvasScrollArea import CanvasScrollManager as CanvasScroll
from libs.CoordinatesSystem import CoordinatesSystem, Transform

sizeof = asizeof.asizeof

CREATE, EDIT, MOVE, MOVING_SHAPE, MOVING_VERTEX = range(5)

class Canvas(QWidget):
    """
        Canvas is the widget that handles and contains all the shapes.

        Usage:
            Canvas.instance() -> Canvas\n
            Canvas(parent) -> Canvas
    """
    on_add_shape = pyqtSignal(Shape)
    on_remove_shape = pyqtSignal(list)

    _instance = None

    EDIT_AXIS_DEFAULT_COLOR = QColor(255, 255, 255, 200)
    NEW_SHAPE_DEFAULT_COLOR = QColor(255, 255, 255, 100)

    @classmethod
    def instance(cls):
        '''
            Returns the instance of Canvas, if the instance is None then creates one,
        '''
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


    @overload
    def __init__(self, parent: QWidget = None) -> None: ...

    def __init__(self, **kwargs) -> None:
        assert Canvas._instance is None, "Tried to instantiate 'Canvas' class more than once"
        super(Canvas, self).__init__()

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

        if 'parent' in kwargs:
            self.mainWindow = kwargs['parent']

        self.scroll_manager = CanvasScroll(self)
        self.scroll_manager.scroll_changed.connect(self.on_scroll_change)

        pal = QPalette()
        pal.setColor(QPalette.Window, Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(pal) 

        self.left_pressed = False # if the left mouse button is pressed
        self.move_sensibility = .7 # the multiplier of the mouse movement to move the viewport

        self.shapes: list[Shape] = [] # list of shapes
        self._painter = QPainter() # painter to draw canvas
        self.h_shapes: list[Shape] = [] # highlighted shape
        self.state = EDIT # current state of the canvas
        self.multi_select = False # if the user is selecting multiple shapes

        self.selected_shapes: list[Shape] = [] # selected shapes

        self.scale = 1.00 # scale of the canvas

        self.creating_pos = None # origin of the new shape
        self.mouse_offset = Vector2Int(0, 0) # offset of the mouse relative to the moving shape

        self.last_mouse_pos = Vector2Int(0, 0) # last mouse position to get the delta
        self.mouse_moved = 0. # the amount of pixels the mouse moved to allow moving the shape

        self.clicked_shape = None # the shape that was clicked
        self.shape_formation: list[(Shape, Vector2Int)] = [] # the difference between the shape's position and the clicked shape's position

        self.cs = CoordinatesSystem(Vector2Int(self.size() * self.scale)) # the coordinate system of the canvas
        self.viewport = Transform(Vector2Int(0, 0), Vector2Int(self.size()), self.cs) # the viewport of the canvas
        self.viewport.on_move.connect(self.update_rect) # update the rect to draw when the viewport moves

        self.original_pixmap = QPixmap() # the original pixmap
        self.original_pixmap.convertFromImage(QImage.fromData(open("./Screenshot_1.png", "rb").read()))

        self.pixmap_offset = Vector2Int(100, 100)

        self.rect_to_draw: QRect = QRect() # the rect to draw the pixmap
        self.resized_pixmap: QPixmap = self.original_pixmap # the resized pixmap

        kh: keyHandler = keyHandler.instance()

        kh.bind_to("create-shape", self.create_mode)
        kh.bind_to("delete-shape", self.delete)
        kh.bind_to("multi-select", self.multi_select_mode)
        kh.bind_to("move", self.move_mode)

        Canvas._instance = self

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.scroll_manager.update()

        self.cs.resize(Vector2Int(self.original_pixmap.size() * self.scale) + self.pixmap_offset * min((self.scale - 1), 1))
        self.viewport.resize(Vector2Int(self.size()) / self.scale)

        self.resized_pixmap: QPixmap = self.original_pixmap.scaled(self.original_pixmap.size() * self.scale, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.rect_to_draw.setRect(self.pixmap_rel_pos().x, self.pixmap_rel_pos().y, self.resized_pixmap.width(), self.resized_pixmap.height())

    def paintEvent(self, a0: QPaintEvent) -> None:
        p = self._painter
        p.begin(self)
        #p.setRenderHint(QPainter.Antialiasing)

        p.drawPixmap(self.rect_to_draw, self.resized_pixmap)
        
        p.translate(self.rect_to_draw.topLeft())
        for shape in self.shapes:
            shape.paint(p, self.scale)
        p.translate(-self.rect_to_draw.topLeft())
        
        if self.state == CREATE:
            self.draw_new_shape(p)

        p.setPen(QPen(Qt.white, 5))
        p.drawPoint(self.get_mouse().as_qpoint())
        p.drawPoint(self.rect().center())

        p.end()

    def add_shape(self, shape: Shape) -> None:
        '''
            Adds a shape to the canvas

            Args:
                shape: the shape to add
        '''
        self.shapes.append(shape)
        self.on_add_shape.emit(shape)
        self.update()

    def update_rect(self, _: Vector2Int):
        '''
            Updates the rect to draw the pixmap

            Args:
                _: the new position of the viewport
        '''
        self.rect_to_draw.setRect(self.pixmap_rel_pos().x, self.pixmap_rel_pos().y, self.resized_pixmap.width(), self.resized_pixmap.height())

    def draw_new_shape(self, painter: QPainter) -> None:
        '''
            Draws the new shape that is being created

            Args:
                painter: The painter to draw the new shape
        '''
        if not self.creating_pos:
            return
        
        painter.setPen(QPen(self.NEW_SHAPE_DEFAULT_COLOR, 2))
        painter.setBrush(QBrush(self.NEW_SHAPE_DEFAULT_COLOR))

        mouse_pos = self.get_mouse()
        painter.drawRect(QRect(self.creating_pos.as_qpoint(), mouse_pos.as_qpoint()))

    def on_scroll_change(self, orientation: Qt.Orientation, value: int) -> None:
        '''
            Called when the scroll value of the canvas is changed.

            Args:
                orientation: The orientation of the scroll bar
                value: The new value of the scroll bar
        '''
        
        self.update()    

    def unfill_all_shapes(self) -> None:
        '''
            Unfills all shapes
        '''
        for shape in self.shapes:
            shape.unfill()

    def sizeHint(self) -> QSize:
        '''
            Returns the size of the canvas in pixels as QSize. This is used by the layout system.
        '''
        parent_size: QSize = self.parent().size()
        size = QSize(parent_size.width(), parent_size.height())
        return size

    def set_scale(self, val: float) -> None:
        '''
            Sets the scale of the canvas.

            Args:
                val: The new scale of the canvas
        '''
        self.scale = max(0.5, min(val, helper.MAX_ZOOM))
        self.scroll_manager.on_scale(self.scale, Vector2Int(self.original_pixmap.size()))

        self.resized_pixmap: QPixmap = self.original_pixmap.scaled(self.original_pixmap.size() * self.scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.cs.resize(Vector2Int(self.original_pixmap.size() * self.scale) + self.pixmap_offset * min(min(self.scale - 1, 0), 1))
        self.viewport.resize(Vector2Int(self.size()) / self.scale)

        self.rect_to_draw = QRect(self.pixmap_rel_pos().x, self.pixmap_rel_pos().y, self.resized_pixmap.width(), self.resized_pixmap.height())


        self.update()

    def pixmap_rel_pos(self) -> Vector2Int:
        '''
            Returns the relative position of the pixmap as Vector2Int
        '''
        return -self.viewport.pos() + self.rect().center() - self.resized_pixmap.size() / 2

    def unhighlight_vertexes(self) -> None:
        '''
            Unhighlights all vertexes.
        '''
        for s in self.shapes:
            s.highlighted_vertex = -1

    def multi_select_mode(self) -> None:
        '''
            Toggles multi select mode.
        '''
        self.multi_select = not self.multi_select

    def mouse_out_of_bounds(self) -> bool:
        '''
            Returns true if the mouse is out of bounds.
        '''
        m_pos = self.get_mouse()
        return (m_pos.x < 0 or m_pos.y < 0) or (m_pos.x > self.original_pixmap.width() or m_pos.y > self.original_pixmap.height())
  
    def move_mode(self) -> None:
        '''
            Sets the canvas to move mode.
        '''
        self.state = MOVE if self.state != MOVE else EDIT
        self.update()

    def create_mode(self) -> None:
        '''
            Sets the canvas to create mode.
        '''
        self.state = CREATE
        self.update()

    def create(self) -> None:
        '''
            Creates a new shape based on the position of the first click and the actual position of the mouse.
        '''
        if not self.creating_pos:
            return
        
        mousepos = self.get_mouse()
        # self.clip_to_pixmap(mousepos)

        if Vector2Int.distance(mousepos, self.creating_pos) < helper.MIN_DIST_CREATE:
            self.creating_pos = None
            self.state = EDIT
            self.update()
            return

        _min = self.viewport.pos() + self.creating_pos
        _max = self.viewport.pos() + mousepos

        shapepos = ShapePoints.square(_min, _max)
        shape = Shape("", shapepos)

        print(f"Created shape with min: {shape.top_left()} and max: {shape.bot_right()}")

        self.add_shape(shape)
        self.creating_pos = None
        self.state = EDIT
        self.update()

    def delete(self) -> None:
        '''
            Deletes all selected shapes.
        '''
        self.on_remove_shape.emit(self.selected_shapes)
        while len(self.selected_shapes) > 0:
            shape = self.selected_shapes[0]
            self.shapes.remove(shape)
            self.deselect(shape)
            del shape
        self.update()

    def deselect_all(self) -> None:
        '''
            Deselects all selected shapes.
        '''
        while len(self.selected_shapes) > 0:
            self.deselect(self.selected_shapes[0])

    def deselect(self, shape: Shape) -> None:
        '''
            Deselects a shape.

            Args:
                shape: The shape to deselect
        '''
        shape.selected = False
        self.selected_shapes.remove(shape)
        self.update()

    def select(self, shape: Shape, force: bool = False) -> None:
        '''
            Selects a shape.

            Args:
                shape: The shape to select
                force: If true the shape will be selected even if it is already selected
        '''

        if shape in self.selected_shapes and not force:
            self.deselect(shape)
            return

        if not self.multi_select or shape is None:
            self.deselect_all()

        if shape not in self.selected_shapes:
            self.selected_shapes.append(shape)
            shape.selected = True
            self.update()
    
    def select_multiple(self, shapes: list[Shape]) -> None:
        '''
            Selects multiple shapes.

            Args:
                shapes: The shapes to select
        '''
        for shape in shapes:
            self.select(shape)

    def auto_fill_shape(self) -> bool:
        '''
            Auto fills a shape if the mouse is within a shape.
        '''
        mousePos = self.get_mouse()

        shape = helper.get_shape_within(mousePos, self.shapes)
        if shape is not None:
            shape.fill = True
            self.update()
            self.last_mouse_pos = self.get_mouse()
            return True
        return False

    def get_mouse(self) -> Vector2Int: 
        '''
            Returns the mouse position in pixels as Vector2Int.
        '''
        return Vector2Int(self.mapFromGlobal(QCursor.pos()))
    
    def clip_to_pixmap(self, mousePos: Vector2Int) -> None:
        pix_min = Vector2Int()
        pix_max = Vector2Int(self.original_pixmap.size())

        mousePos.clip(pix_min, pix_max)

    def wheelEvent(self, a0: QWheelEvent) -> None:
        self.set_scale(a0.angleDelta().y() / 120 * .1 + self.scale)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        mousePos = self.get_mouse()
        self.clip_to_pixmap(mousePos)

        # IF MOVING
        if self.state == MOVE and self.left_pressed:
            delta = self.get_mouse() - self.last_mouse_pos
            self.viewport.move_by(-delta)
            self.repaint()
            self.last_mouse_pos = self.get_mouse()
            return

        # IF MOVING VERTEX
        if self.state == MOVING_VERTEX:
            self.unfill_all_shapes()

            self.selected_shapes[0].move_vertex(mousePos)
            self.repaint()
            return

        # IF MOVING SHAPE
        if self.state == MOVING_SHAPE and self.mouse_moved > helper.MIN_DIST_TO_MOVE:
            self.unfill_all_shapes()

            mousePos -= self.mouse_offset
            helper.move_shapes(mousePos, self.clicked_shape, self.shape_formation, Vector2Int(self.original_pixmap.size()))
            self.repaint()
            return

        self.mouse_moved += Vector2Int.distance(mousePos, self.last_mouse_pos)

        # IF CREATING
        if self.state == CREATE:
            self.h_shapes = []
            self.repaint()
            self.last_mouse_pos = self.get_mouse()
            return

        # HIGHLIGHT VERTEX
        closest_shape, vertex_index = helper.get_closest_shape_vertex(mousePos, self.shapes)
        if closest_shape is not None:
            self.unfill_all_shapes()
            closest_shape.highlighted_vertex = vertex_index
            self.repaint()
            return
        
        self.unhighlight_vertexes()

        self.unfill_all_shapes()

        # HIGHLIGHT SHAPE
        if self.auto_fill_shape():
            return

        # ELSE
        self.h_shapes = []
        self.repaint()
        self.last_mouse_pos = self.get_mouse()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        mousePos = self.get_mouse()
        self.clip_to_pixmap(mousePos)

        if a0.button() != Qt.LeftButton:
            return
        
        self.state = CREATE
        
        self.left_pressed = True

        # IF MOVING
        if self.state == MOVE:
            return

        # IF CREATE
        if self.state == CREATE:
            self.creating_pos = self.get_mouse()
            self.update()
            return

        # MOVE VERTEX
        # closest_shape, vertex_index = helper.get_closest_shape_vertex(mousePos, self.shapes)
        # if closest_shape is not None:
        #     self.deselect_all()
        #     self.select(closest_shape, True)
        #     #Start moving vertex

        #     self.state = MOVING_VERTEX
        #     closest_shape.highlighted_vertex = vertex_index

        #     self.selected_shapes[0].move_vertex(mousePos)

        #     self.update()
        #     return
        
        # # MOVE SHAPE
        # closest_shape = helper.get_shape_within(mousePos, self.shapes)
        # if closest_shape is not None:
        #     self.select(closest_shape, True)
        #     #Start moving shape
        #     self.mouse_offset = mousePos - closest_shape.top_left()
        #     self.clicked_shape = closest_shape

        #     self.state = MOVING_SHAPE

        #     self.shape_formation.clear()
        #     self.shape_formation = helper.get_formation(self.clicked_shape, self.selected_shapes)

        #     self.mouse_moved = 0
        #     return

        self.deselect_all()
        self.update()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() != Qt.LeftButton:
            return
        
        self.left_pressed = False

        if self.state == CREATE:
            self.create()

        if self.state == MOVING_VERTEX or self.state == MOVING_SHAPE:
            self.state = EDIT
            self.clicked_shape = None
            self.auto_fill_shape()
        
        self.update()