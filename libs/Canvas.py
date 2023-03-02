from typing import overload

from PyQt5.QtCore import Qt, QSize, QPointF, QPoint
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QColor, QPalette, QPainter, QPaintEvent, QMouseEvent, QPixmap, QImage, QPen

from libs.ShapePoints import ShapePoints
from libs.Shape import Shape
from libs.Vector import Vector2Int
from libs.CanvasHelper import CanvasHelper as helper
from libs.keyHandler import keyHandler

CREATE = 0
EDIT = 1
MOVING_SHAPE = 2
MOVING_VERTEX = 3

class Canvas(QWidget):
    """
        Canvas is the widget that handles and contains all the shapes.

        Usage:
            Canvas.instance() -> Canvas
    """

    _instance = None

    EDIT_AXIS_DEFAULT_COLOR = QColor(255, 255, 255, 200)
    NEW_SHAPE_DEFAULT_COLOR = QColor(255, 255, 255, 100)

    @overload
    def __init__(self, parent: QWidget = None) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        super(Canvas, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

        if 'parent' in kwargs:
            self.setParent(kwargs['parent'])

        pal = QPalette()
        pal.setColor(QPalette.Window, Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.shapes: list[Shape] = []
        self._painter = QPainter()
        self.h_shapes: list[Shape] = [] # highlighted shape
        self.state = EDIT
        self.multi_select = False

        self.selected_shapes: list[Shape] = []

        self.scale = 1.00

        self.creating_pos = None # origin of the new shape
        self.mouse_offset = Vector2Int(0, 0)

        self.last_mouse_pos = Vector2Int(0, 0)
        self.mouse_moved = 0.

        self.clicked_shape = None
        self.shape_formation: list[(Shape, Vector2Int)] = []
        
        kh: keyHandler = keyHandler.instance()

        kh.bind_to("create-shape", self.create_mode)
        kh.bind_to("delete-shape", self.delete)
        kh.bind_to("multi-select", self.multi_select_mode)

        self.pixmap = QPixmap()
        self.pixmap.convertFromImage(QImage.fromData(open("./Screenshot_1.png", "rb").read()))

        Canvas._instance = self

    @classmethod
    def instance(cls):
        '''
            Returns the instance of Canvas, if the instance is None then creates one,
        '''
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def paintEvent(self, a0: QPaintEvent) -> None:
        '''
            Paints the canvas and all the shapes on it.
            
            Args:
                a0: The QPaintEvent
        '''
        origin = self.get_origin().as_qpoint()

        p = self._painter
        p.begin(self)
        p.scale(self.scale, self.scale)

        # Translate the painter to the top left of the pixmap
        p.translate(origin)

        p.drawPixmap(QPoint(0, 0), self.pixmap)

        for shape in self.shapes:
            if shape.isVisible:
                shape.paint(p)

        p.setPen(QPen(Qt.white, 5))
        p.drawPoint((self.get_mouse(True)).as_qpoint())

        # Draw the new shape if the state is CREATE and the mouse button has been pressed
        if self.state == CREATE and self.creating_pos:
            p.setPen(Canvas.NEW_SHAPE_DEFAULT_COLOR)
            p.setBrush(Canvas.NEW_SHAPE_DEFAULT_COLOR)

            mouse_pos = self.get_mouse(True)
            self.clip_to_pixmap(mouse_pos)

            sp = ShapePoints.square(self.creating_pos, mouse_pos)
            min, max = Vector2Int.get_min_max(sp.points)

            width = max.x - min.x
            height = max.y - min.y

            p.drawRect(min.x,  min.y, width, height)
        # Draw the crosshair if the state is CREATE and the mouse button has not been pressed
        elif self.state == CREATE:
            p.translate(-origin)
            p.setPen(Canvas.EDIT_AXIS_DEFAULT_COLOR)
            p.setBrush(Canvas.EDIT_AXIS_DEFAULT_COLOR)

            size = self.sizeHint()
            mouse_pos = self.get_mouse()

            hor_line, ver_line = helper.get_crosshair(mouse_pos, size.width(), size.height())

            # Spawn 2 lines one horizontal and one vertical that intersects at mouse position
            p.drawLine(hor_line)
            p.drawLine(ver_line)
            p.translate(origin)
        p.end()

    def get_origin(self) -> Vector2Int:
        '''
            Returns the top left of the pixmap as Vector2Int
        '''
        pixmap_max = QPoint(self.pixmap.width(), self.pixmap.height())
        return Vector2Int(self.rect().center() - pixmap_max / 2)

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
        self.scale = val
        self.update()

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
        m_pos = self.get_mouse(True)
        return (m_pos.x < 0 or m_pos.y < 0) or (m_pos.x > self.pixmap.width() or m_pos.y > self.pixmap.height())

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
        
        mousepos = self.get_mouse(True)
        self.clip_to_pixmap(mousepos)

        if Vector2Int.distance(mousepos, self.creating_pos) < helper.MIN_DIST_CREATE:
            self.creating_pos = None
            self.state = EDIT
            self.update()
            return

        _min = self.creating_pos
        _max = mousepos

        shapepos = ShapePoints.square(_min, _max)
        shape = Shape("", shapepos)

        print(f"Created shape with min: {shape.top_left()} and max: {shape.bot_right()}")

        self.shapes.append(shape)
        self.creating_pos = None
        self.state = EDIT
        self.update()

    def delete(self) -> None:
        '''
            Deletes all selected shapes.
        '''
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
        mousePos = self.get_mouse(True)

        shape = helper.get_shape_within(mousePos, self.shapes)
        if shape is not None:
            shape.fill = True
            self.update()
            self.last_mouse_pos = mousePos
            return True
        return False

    def get_mouse(self, relative: bool=False) -> Vector2Int:
        '''
            Returns the mouse position in pixels as Vector2Int.
        '''
        if relative:
            return helper.relative_pos(helper.get_mouse(self.scale, self), self.get_origin())
        return helper.get_mouse(self.scale, self)

    def clip_to_pixmap(self, mousePos: Vector2Int) -> None:
        pix_min = Vector2Int()
        pix_max = Vector2Int(self.pixmap.size())

        mousePos.clip(pix_min, pix_max)

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        mousePos = self.get_mouse(True)
        self.clip_to_pixmap(mousePos)

        # IF MOVING VERTEX
        if self.state == MOVING_VERTEX:
            self.unfill_all_shapes()

            self.selected_shapes[0].move_vertex(mousePos)
            self.update()
            return

        # IF MOVING SHAPE
        if self.state == MOVING_SHAPE and self.mouse_moved > helper.MIN_DIST_TO_MOVE:
            self.unfill_all_shapes()

            mousePos -= self.mouse_offset
            helper.move_shapes(mousePos, self.clicked_shape, self.shape_formation, Vector2Int(self.pixmap.size()))
            self.update()
            return

        self.mouse_moved += Vector2Int.distance(mousePos, self.last_mouse_pos)

        # IF CREATING
        if self.state == CREATE:
            self.h_shapes = []
            self.update()
            self.last_mouse_pos = mousePos
            return

        # HIGHLIGHT VERTEX
        closest_shape, vertex_index = helper.get_closest_shape_vertex(mousePos, self.shapes)
        if closest_shape is not None:
            self.unfill_all_shapes()
            closest_shape.highlighted_vertex = vertex_index
            self.update()
            return
        
        self.unhighlight_vertexes()

        self.unfill_all_shapes()

        # HIGHLIGHT SHAPE
        if self.auto_fill_shape():
            return

        # ELSE
        self.h_shapes = []
        self.update()
        self.last_mouse_pos = mousePos

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        mousePos = self.get_mouse(True)
        self.clip_to_pixmap(mousePos)

        if a0.button() != Qt.LeftButton:
            return

        # IF CREATE
        if self.state == CREATE:
            self.creating_pos = mousePos
            self.update()
            return

        # MOVE VERTEX
        closest_shape, vertex_index = helper.get_closest_shape_vertex(mousePos, self.shapes)
        if closest_shape is not None:
            self.deselect_all()
            self.select(closest_shape, True)
            #Start moving vertex

            self.state = MOVING_VERTEX
            closest_shape.highlighted_vertex = vertex_index

            self.selected_shapes[0].move_vertex(mousePos)

            self.update()
            return
        
        # MOVE SHAPE
        closest_shape = helper.get_shape_within(mousePos, self.shapes)
        if closest_shape is not None:
            self.select(closest_shape, True)
            #Start moving shape
            self.mouse_offset = mousePos - closest_shape.top_left()
            self.clicked_shape = closest_shape

            self.state = MOVING_SHAPE

            self.shape_formation.clear()
            self.shape_formation = helper.get_formation(self.clicked_shape, self.selected_shapes)

            self.mouse_moved = 0
            return

        self.deselect_all()
        self.update()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() != Qt.LeftButton:
            return

        if self.state == CREATE:
            self.create()

        if self.state == MOVING_VERTEX or self.state == MOVING_SHAPE:
            self.state = EDIT
            self.clicked_shape = None
            self.auto_fill_shape()
        
        self.update()