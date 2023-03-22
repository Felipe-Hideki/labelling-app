from typing import overload
from time import time

from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtWidgets import QWidget, QSizePolicy, QMenu, QAction, QApplication
from PyQt5.QtGui import QColor, QPalette, QPainter, QPaintEvent, QMouseEvent, QWheelEvent, QPixmap, QImage, QPen, QResizeEvent, QBrush

from libs.widgets.ShapePoints import ShapePoints
from libs.standalones.Vector import Vector2Int
from libs.widgets.EditWidget import EditWidget
from libs.standalones.Files_Manager import Files_Manager
from libs.standalones.pascal_voc_io import PascalVocReader, PascalVocWriter
from libs.canvas.Shape import Shape
from libs.canvas.CanvasHelper import CanvasHelper as helper
from libs.canvas.CanvasScrollManager import CanvasScrollManager as CanvasScroll
from libs.canvas.CoordinatesSystem import CoordinatesSystem, Transform
from libs.handlers.MouseManager import MouseManager
from libs.handlers.keyboard.KeyHandler import KeyHandler, ActionBind

CREATE, EDIT, MOVE, MOVING_SHAPE, MOVING_VERTEX, COPY = range(6)

class CanvasWin(QWidget):
    """
        Canvas is the widget that handles and contains all the shapes.

        Usage:
            Canvas.instance() -> Canvas\n
            Canvas(parent) -> Canvas
    """
    OnAddShape = pyqtSignal(Shape)
    OnRemoveShape = pyqtSignal(list)
    OnSelectShape = pyqtSignal(Shape)
    OnDeselectShape = pyqtSignal(Shape)

    OnChangedShapes = pyqtSignal(list)

    OnBeginEdit = pyqtSignal()
    OnEndEdit = pyqtSignal(str)

    __instance = None

    EDIT_AXIS_DEFAULT_COLOR = QColor(255, 255, 255, 200)
    NEW_SHAPE_DEFAULT_COLOR = QColor(255, 255, 255, 100)

    DEFAULT_BACKGROUND_COLOR = QColor(0, 0, 0, 255)

    @classmethod
    def instance(cls):
        '''
            Returns the instance of Canvas, if the instance is None then creates one,
        '''
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    @overload
    def __init__(self, parent: QWidget = None) -> None: ...

    def __init__(self, **kwargs) -> None:
        assert CanvasWin.__instance is None, "Tried to instantiate 'Canvas' class more than once"
        super(CanvasWin, self).__init__()

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.WheelFocus)

        if 'parent' in kwargs:
            self.mainWindow = kwargs['parent']

        self.scroll_manager = CanvasScroll(self)
        self.scroll_manager.scroll_changed.connect(self.on_scroll_change)

        self.background_color = CanvasWin.DEFAULT_BACKGROUND_COLOR

        pal = QPalette()
        pal.setColor(QPalette.Window, self.background_color)
        self.setAutoFillBackground(True)
        self.setPalette(pal) 

        self.left_pressed = False # if the left mouse button is pressed
        self.move_sensitivity = .5 # the multiplier of the mouse movement to move the viewport

        self.shapes: list[Shape] = [] # list of shapes
        self._painter = QPainter() # painter to draw canvas
        self.h_shapes: list[Shape] = [] # highlighted shape
        self.state = EDIT # current state of the canvas
        self.multi_select = False # if the user is selecting multiple shapes

        self.selected_shapes: list[Shape] = [] # selected shapes
        self.highlighted_vertex: tuple[Shape, int] = (None, None)
        self.filled_shape: Shape = None

        self.scale = 1.00 # scale of the canvas

        self.shape_copy: Shape = None

        self.creating_pos: Vector2Int = None # origin of the new shape
        self.mouse_offset = Vector2Int(0, 0) # offset of the mouse relative to the moving shape

        self.last_mouse_pos = Vector2Int(0, 0) # last mouse position to get the delta
        self.mouse_moved = 0. # the amount of pixels the mouse moved to allow moving the shape

        self.cur_img = -1 # current image index

        self.was_selected = False
        self.clicked_shape = None # the shape that was clicked
        self.shape_formation: list[(Shape, Vector2Int)] = [] # the difference between the shape's position and the clicked shape's position

        self.cs = CoordinatesSystem(Vector2Int(self.size() * self.scale)) # the coordinate system of the canvas
        self.viewport = Transform(Vector2Int(0, 0), Vector2Int(self.size()), self.cs) # the viewport of the canvas
        self.viewport.on_move.connect(self.update_rect) # update the rect to draw when the viewport moves
        self.viewport.on_move.connect(self.scroll_manager.on_viewport_move) # update the scroll bars when the viewport moves

        self.original_pixmap = QPixmap() # the original pixmap

        self.pixmap_offset = Vector2Int(100, 100)

        self.rect_to_draw: QRect = QRect() # the rect to draw the pixmap
        self.resized_pixmap: QPixmap = self.original_pixmap # the resized pixmap

        self.edit_widget = EditWidget()

        # Key bindings
        kh = KeyHandler.instance()
        kh.bind_to(ActionBind.create_shape, self.create_mode)
        kh.bind_to(ActionBind.delete_shape, self.delete)
        kh.bind_to(ActionBind.multi_select, self.multi_select_mode)
        kh.bind_to(ActionBind.move, self.move_mode)
        kh.bind_to(ActionBind.edit, self.edit_label_slot)
        self.OnBeginEdit.connect(self.edit_label)
        # Mouse bind
        self.mouseManager = MouseManager.instance()
        self.mouseManager.OnMove.connect(self.OnMouseMove)

        # On file load bind
        files_manager = Files_Manager.instance()
        files_manager.OnLoadImage.connect(self.load_shapes)
        files_manager.OnLoadImage.connect(self.load_pixmap)

        self.chosing_option = False # The user is chosing an option in the menu?

        # Right click Menu
        self.rclick_menu = QMenu(self)
        copy = QAction("Copy", self)
        copy.triggered.connect(self._create_copy)
        self.rclick_menu.addAction(copy)

        CanvasWin.__instance = self

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.scroll_manager.update()

        self.update_coordinates()
        self.update()

    def paintEvent(self, a0: QPaintEvent) -> None:
        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.drawPixmap(self.rect_to_draw, self.resized_pixmap)
        
        p.translate(self.rect_to_draw.topLeft())
        for shape in self.shapes:
            shape.paint(p, self.scale)
        if self.shape_copy is not None:
            self.shape_copy.paint(p, self.scale)
        p.translate(-self.rect_to_draw.topLeft())
        
        if self.state == CREATE:
            self.draw_new_shape(p)

        p.end()

    def load_shapes(self, filepath: str):
        if self.cur_img != -1:
            last_file = Files_Manager.instance().imgs()[self.cur_img]
            last_file_name = last_file.split('/')[-1]
            last_file_folder = last_file.split('/')[-2]

            writer = PascalVocWriter(last_file_folder, last_file_name, 
                                (self.original_pixmap.size().width(), self.original_pixmap.size().height(), 3), 
                                local_img_path=last_file)
            for shape in self.shapes:
                _min, _max = Vector2Int.get_min_max(shape.get_points())
                writer.add_bnd_box(_min.x, _min.y, _max.x, _max.y, shape.name)
            writer.save(last_file.replace("jpg", "xml"))
        reader = PascalVocReader(filepath)

        del self.shapes[:]
        self.shapes = reader.get_shapes()
        self.cur_img = Files_Manager.instance().img_index()
        self.OnChangedShapes.emit(self.shapes)

    def load_pixmap(self, path: str) -> None:
        assert len(path) > 0, "Path is empty"
        t0 = time()
        self.original_pixmap = QPixmap(QImage.fromData(open(path, "rb").read()))
        self.resized_pixmap: QPixmap = self.original_pixmap.scaled(self.original_pixmap.size() * self.scale, Qt.KeepAspectRatio, Qt.FastTransformation)
        print(f"Loaded image in {time() - t0}s")
        t0 = time()
        self.update_coordinates()
        self.update_rect(None)
        self.update()
        print(f"Updated canvas in {time() - t0}s")

    def add_shape(self, shape: Shape) -> None:
        '''
            Adds a shape to the canvas

            Args:
                shape: the shape to add
        '''
        self.shapes.append(shape)
        self.OnAddShape.emit(shape)
        self.update()

    def update_coordinates(self) -> None:
        '''
            Updates the coordinates system of the canvas
        '''
        if self.original_pixmap.isNull():
            return

        ratio = self.size().width() / self.size().height()
        self.cs.resize(Vector2Int(self.original_pixmap.size().width() + 50, self.original_pixmap.size().width() / ratio)* self.scale)

        self.viewport.resize(Vector2Int(self.size()))
        self.resized_pixmap: QPixmap = self.original_pixmap.scaled(self.original_pixmap.size() * self.scale, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.scroll_manager.on_scale(self.cs.size(), self.viewport.size(), self.viewport.pos())
        #self.viewport.resize(Vector2Int(self.size()) / self.scale)

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
        start_pos = self.creating_pos

        self.clip_to_pixmap(mouse_pos, self.rect_to_draw.topLeft())
        self.clip_to_pixmap(start_pos, self.rect_to_draw.topLeft())

        painter.drawRect(QRect(start_pos.as_qpoint(), mouse_pos.as_qpoint()))

    def on_scroll_change(self, orientation: Qt.Orientation, value: int) -> None:
        '''
            Called when the scroll value of the canvas is changed.

            Args:
                orientation: The orientation of the scroll bar
                value: The new value of the scroll bar
        '''
        if orientation == Qt.Horizontal:
            self.viewport.move(Vector2Int(value, self.viewport.pos().y))
        elif orientation == Qt.Vertical:
            self.viewport.move(Vector2Int(self.viewport.pos().x, value))

        self.update()    

    def unfill_shape(self) -> None:
        '''
            Unfills the filled shape
        '''
        if self.filled_shape is None:
            return
        
        self.filled_shape.unfill()
        self.filled_shape = None

    def sizeHint(self) -> QSize:
        '''
            Returns the size of the canvas in pixels as QSize. This is used by the layout system.
        '''
        parent_size: QSize = self.parent().size()
        size = QSize(parent_size.width(), parent_size.height())
        return size

    def set_state(self, state: int) -> None:
        '''
            Sets the state of the canvas

            Args:
                state: The new state of the canvas
        '''
        self.state = state
        self.update_cursor()

    def update_cursor(self) -> None:
        '''
            Sets the cursor of the canvas
        '''
        if not self.hasFocus():
            return
        if self.state == CREATE:
            QApplication.setOverrideCursor(Qt.CrossCursor)
        elif self.state == MOVE and self.left_pressed:
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
        elif self.state == MOVE:
            QApplication.setOverrideCursor(Qt.OpenHandCursor)
        elif self.state == MOVING_SHAPE or self.state == MOVING_VERTEX \
            or self.state == COPY:
            QApplication.setOverrideCursor(Qt.BlankCursor)
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)

    def set_scale(self, val: float) -> None:
        '''
            Sets the scale of the canvas.

            Args:
                val: The new scale of the canvas
        '''
        self.scale = max(0.5, min(val, helper.MAX_ZOOM))
        self.update_coordinates()
        self.update_rect(Vector2Int(0, 0))
        self.update()

    def pixmap_rel_pos(self) -> Vector2Int:
        '''
            Returns the relative position of the pixmap as Vector2Int
        '''
        return -self.viewport.pos() + self.rect().center() - self.resized_pixmap.size() / 2

    def unhighlight_vertex(self) -> None:
        '''
            Unhighlights all vertexes.
        '''
        if self.highlighted_vertex[0] is None:
            return
        self.highlighted_vertex[0].highlighted_vertex = -1
        self.highlighted_vertex = (None, None)

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
        self.set_state(MOVE if self.state != MOVE else EDIT)

    def edit_label_slot(self):
        self.OnBeginEdit.emit()

    @pyqtSlot()
    def edit_label(self) -> None:
        if len(self.selected_shapes) == 0:
            return
        name = self.edit_widget.get_name(self.selected_shapes[0].name, "Rename Shape")
        
        [shape.set_name(name) for shape in self.selected_shapes]

        self.OnEndEdit.emit(name)

    def create_mode(self) -> None:
        '''
            Sets the canvas to create mode.
        '''
        self.set_state(CREATE)

    def create(self) -> None:
        '''
            Creates a new shape based on the position of the first click and the actual position of the mouse.
        '''
        if not self.creating_pos:
            return
        
        mousepos = self.get_mouse()

        if Vector2Int.distance(mousepos, self.creating_pos) < helper.MIN_DIST_CREATE:
            self.creating_pos = None
            self.set_state(EDIT)
            self.update()
            return
        
        shape_name = self.edit_widget.get_name("Create Shape")

        if shape_name != "":
            relative_pos = self.pixmap_rel_pos()

            _min = self.creating_pos - relative_pos
            _max = mousepos - relative_pos

            self.clip_to_pixmap(_min)
            self.clip_to_pixmap(_max)

            shapepos = ShapePoints.square(_min / self.scale, _max / self.scale)
            shape = Shape(shape_name, shapepos)

            print(f"Created shape with min: {shape.top_left()} and max: {shape.bot_right()} with name: {shape_name}")

            self.add_shape(shape)
        self.creating_pos = None
        self.set_state(EDIT)
        self.update()

    def _create_copy(self) -> None:
        if self.shape_copy is None:
            return
        
        self.add_shape(self.shape_copy)
        self.select(self.shape_copy, True, False)
        self.shape_copy = None
        self.set_state(EDIT)

    def delete(self) -> None:
        '''
            Deletes all selected shapes.
        '''
        print(f"Deleting {len(self.selected_shapes)} shapes from total shapes {len(self.shapes)}")
        print(f"differences = {set(self.selected_shapes) - set(self.shapes)}")
        self.OnRemoveShape.emit(self.selected_shapes)
        while len(self.selected_shapes) > 0:
            shape = self.selected_shapes[0]
            shape.selected = False
            del self.shapes[self.shapes.index(shape)], self.selected_shapes[0]
        self.selected_shapes = []
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
        assert shape in self.selected_shapes, "Shape not found in selected shapes list"
        shape.selected = False
        self.selected_shapes.remove(shape)
        self.OnDeselectShape.emit(shape)
        self.update()

    def __select(self, shape: Shape):
        self.selected_shapes.append(shape)
        shape.selected = True
        self.OnSelectShape.emit(shape)
        self.update()

    def select(self, shape: Shape, force: bool = False, multi_select: bool = None) -> None:
        '''
            Selects a shape.

            Args:
                shape: The shape to select
                force: If true the shape will be selected even if it is already selected
                multi_select: If false the selected list will be reset, default value is \
                the multi_select field
        '''
        if multi_select is None:
            multi_select = self.multi_select

        if not multi_select and len(self.selected_shapes) > 1:
            self.deselect_all()
            self.__select(shape)
            return

        if shape in self.selected_shapes and not force:
            if not multi_select:
                self.deselect_all()
                return
            self.deselect(shape)
            return
        
        if force and shape in self.selected_shapes:
            self.was_selected = True
        else:
            self.was_selected = False

        if not multi_select or shape is None:
            self.deselect_all()

        if shape not in self.selected_shapes:
            self.__select(shape)
    
    def select_multiple(self, shapes: list[Shape], force: bool = False) -> None:
        '''
            Selects multiple shapes.

            Args:
                shapes: The shapes to select
        '''
        for shape in shapes:
            self.select(shape, force)

    def auto_fill_shape(self, shape: Shape = None) -> bool:
        '''
            Auto fills a shape if the mouse is within a shape.
        '''
        if shape is not None:
            if self.filled_shape:
                self.filled_shape.unfill()
            self.filled_shape = shape
            shape.fill = True
            self.update()
            self.last_mouse_pos = self.get_mouse()
            return True
        return False

    def get_mouse(self) -> Vector2Int: 
        '''
            Returns the mouse position in pixels as Vector2Int.
        '''
        return Vector2Int(self.mapFromGlobal(self.mouseManager.current_pos))

    def get_mouse_relative(self):
        '''
            Returns the mouse position relative to the pixmap.
        '''
        return (self.get_mouse() - self.pixmap_rel_pos()) / self.scale

    def clip_to_pixmap(self, mousePos: Vector2Int, offset: Vector2Int = Vector2Int(0, 0)) -> None:
        pix_min = Vector2Int() + offset
        pix_max = Vector2Int(self.resized_pixmap.size()) + offset

        mousePos.clip(pix_min, pix_max)

    def wheelEvent(self, a0: QWheelEvent) -> None:
        if self.scale + a0.angleDelta().y() / 120 * .3 > helper.MAX_ZOOM:
            if self.scale < helper.MAX_ZOOM:
                self.set_scale(helper.MAX_ZOOM)
            return
        self.set_scale(a0.angleDelta().y() / 120 * .3 + self.scale)

    def OnMouseMove(self) -> None:
        if self.original_pixmap.isNull() or self.chosing_option:
            return
        mousePos = self.get_mouse_relative()

        # IF MOVING
        if self.state == MOVE and self.left_pressed:
            delta = self.get_mouse() - self.last_mouse_pos
            self.viewport.move_by(-delta * self.move_sensitivity * min(self.scale, 1))
            self.update()
            self.last_mouse_pos = self.get_mouse()
            self.update_cursor()
            return

        # IF COPYING
        if self.state == COPY:
            self.unfill_shape()

            mousePos -= self.mouse_offset

            self.shape_copy.move(mousePos, Vector2Int(self.original_pixmap.size()))
            self.update()
            return

        # IF MOVING VERTEX
        if self.state == MOVING_VERTEX:
            self.unfill_shape()

            self.selected_shapes[0].move_vertex(mousePos, self.highlighted_vertex[1])
            self.update()
            self.update_cursor()
            return

        # IF MOVING SHAPE
        if self.state == MOVING_SHAPE and self.mouse_moved > helper.MIN_DIST_TO_MOVE:
            self.unfill_shape()

            mousePos -= self.mouse_offset
            helper.move_shapes(mousePos, self.clicked_shape, self.shape_formation, Vector2Int(self.original_pixmap.size()))
            self.update()
            self.update_cursor()
            return

        self.mouse_moved += Vector2Int.distance(mousePos, (self.last_mouse_pos- self.pixmap_rel_pos()) / self.scale)

        # IF CREATING
        if self.state == CREATE:
            if self.left_pressed:
                self.update()
            return

        # HIGHLIGHT VERTEX
        closest_shape, closest_vertex = helper.get_within(mousePos, self.shapes)
        if closest_vertex[0] is not None:
            self.unfill_shape()
            self.unhighlight_vertex()
            closest_vertex[0].highlighted_vertex = closest_vertex[1]
            self.highlighted_vertex = closest_vertex
            self.update()
            return

        # HIGHLIGHT SHAPE
        if self.auto_fill_shape(closest_shape):
            self.unhighlight_vertex()
            return

        # ELSE
        if len(self.h_shapes) > 0 or self.highlighted_vertex[0] is not None or self.filled_shape is not None:
            self.unhighlight_vertex()
            self.unfill_shape()
            self.h_shapes = []
            self.update()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if self.chosing_option:
            return
        mousePos = self.get_mouse_relative()

        if a0.button() == Qt.RightButton:
            # IF COPYING
            closest_shape = helper.get_shape_within(mousePos, self.shapes)
            if closest_shape is not None:
                self.shape_copy = closest_shape.copy()
                self.set_state(COPY)
                self.mouse_offset = mousePos - closest_shape.top_left()
                self.mouse_moved = 0
                self.deselect_all()
                self.select(closest_shape, True, True)
                self.select(self.shape_copy, True, True)

        if a0.button() == Qt.LeftButton and self.state == COPY:
            self.set_state(EDIT)
            self.mouse_offset = Vector2Int()
            self.mouse_moved = 0
            self.deselect_all()
            self.shape_copy = None
            return

        if a0.button() != Qt.LeftButton:
            return
        
        self.left_pressed = True

        # IF MOVING
        if self.state == MOVE:
            self.last_mouse_pos = self.get_mouse()
            return

        # IF CREATE
        if self.state == CREATE:
            self.creating_pos = self.get_mouse()
            return

        # MOVE VERTEX
        closest_shape, vertex_index = helper.get_closest_shape_vertex(mousePos, self.shapes)
        if closest_shape is not None:
            self.deselect_all()
            self.select(closest_shape, True)
            #Start moving vertex

            self.set_state(MOVING_VERTEX)
            closest_shape.highlighted_vertex = vertex_index

            closest_shape.move_vertex(mousePos, closest_shape.highlighted_vertex)

            self.update()
            return
        
        # MOVE SHAPE
        closest_shape = helper.get_shape_within(mousePos, self.shapes)
        if closest_shape is not None:
            self.select(closest_shape, True)
            #Start moving shape
            self.mouse_offset = mousePos - closest_shape.top_left()
            self.clicked_shape = closest_shape

            self.set_state(MOVING_SHAPE)

            self.shape_formation.clear()
            self.shape_formation = helper.get_formation(self.clicked_shape, self.selected_shapes)

            self.mouse_moved = 0
            return

        self.deselect_all()
        self.update()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.RightButton and self.state == COPY:
            if self.mouse_moved <= helper.MIN_DIST_TO_MOVE:
                self.chosing_option = True
                if self.rclick_menu.exec_(self.mapToGlobal(a0.pos())) is None:
                    self.set_state(EDIT)
                    self.mouse_offset = Vector2Int()
                    self.mouse_moved = 0
                    self.deselect_all()
                    self.shape_copy = None
                self.chosing_option = False
        if a0.button() != Qt.LeftButton:
            return
        
        self.left_pressed = False

        self.update_cursor()

        if self.state == CREATE:
            self.create()

        if self.state == MOVING_SHAPE and self.mouse_moved <= helper.MIN_DIST_TO_MOVE \
            and self.was_selected:
            self.deselect(self.clicked_shape)

        if self.state == MOVING_VERTEX or self.state == MOVING_SHAPE:
            self.set_state(EDIT)
            self.clicked_shape = None
            shape = helper.get_shape_within(self.get_mouse_relative(), self.shapes)
            self.auto_fill_shape(shape)
        
        self.update()