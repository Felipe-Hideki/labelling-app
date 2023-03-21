from PyQt5.QtCore import *
from PyQt5.QtGui import *

from libs.widgets.ShapePoints import ShapePoints
from libs.standalones.Vector import Vector2Int
from libs.standalones.MyException import InvalidVertexException
from libs.standalones.Utils import utils

    
class Shape:
    #DEFAULT_VERTEX_COLOR = QColor(124, 252, 0, 255)
    DEFAULT_HIGHLIGHT_COLOR = QColor(242, 0, 0, 255)
    DEFAULT_SELECTED_COLOR = QColor(0, 60, 255, 100)
    DEFAULT_FILL_PATTERN = Qt.BDiagPattern

    VERTEX_SIZE = 4
    VERTEX_HIGHLIGHT_GROWTH = 3

    PEN_SIZE = 2
    
    def __init__(self, name: str, points: ShapePoints) -> None:
        assert points is not None, "Shape.__init__(): points must not be None"
        self.name = name
        self.__points = points
        self.isVisible = True
        self.highlighted_vertex = -1
        self.fill = False
        self.selected = False

        generated_color = utils.generate_color_by_text(self.name)
        generated_color.setAlpha(255)

        self.lines_color = QColor(generated_color)
        self.vertex_color = QColor(generated_color)
        self.highlighted_color = Shape.DEFAULT_HIGHLIGHT_COLOR
        self.selected_color = Shape.DEFAULT_SELECTED_COLOR
        self.fill_color = QColor(generated_color)
        self.fill_pattern = Shape.DEFAULT_FILL_PATTERN
        generated_color.setAlpha(100)
        self.fill_pattern_color = QColor(generated_color)

        _min, _max = Vector2Int.get_min_max(self.__points)
        self.__size = QSize(_max.x - _min.x, _max.y - _min.y)
        self.__scale = 1.0
        self.__scaled = [point.as_qpoint() for point in self.__points]

    def set_name(self, name: str):
        self.name = name

    def get_points(self) -> ShapePoints:
        return self.__points.copy()

    def top_left(self) -> Vector2Int:
        return self.__points[0]
    
    def bot_right(self) -> Vector2Int:
        return self.__points[2]

    def width(self) -> int:
        return self.__size.width()
    
    def height(self) -> int:
        return self.__size.height()
    
    def size(self) -> QSize:
        return self.__size
    
    def copy(self) -> 'Shape':
        return Shape(self.name, self.__points.copy())
    
    def __update(self) -> None:
        self.__update_size()
        self.__update_scale(self.__scale)

    def __update_size(self) -> None:
        self.__size = QSize(abs(self.bot_right().x - self.top_left().x), abs(self.bot_right().y - self.top_left().y))

    def __update_scale(self, scale: float):
        self.__scale = scale
        self.__scaled = self.__scale_points(scale)

    def closest_vertex(self, pos: Vector2Int, limit: float) -> tuple[int, float] | tuple[None, None]:
        closest = (None, None)
        for i, point in enumerate(self.__points):
            if (dist := Vector2Int.distance(pos, point)) < limit:
                if closest[0] is None or dist < closest[1]:
                    closest = (i, dist)
        return closest

    def move_by(self, amount: Vector2Int, clip_max: Vector2Int) -> None:
        self.move(self.top_left() + amount, clip_max)

    def move(self, to: Vector2Int, clip_max: Vector2Int) -> None:
        assert type(to) == Vector2Int, "Args[0] Need to be Vector2Int"
        assert type(clip_max) == Vector2Int, "Args[1] Need to be Vector2Int"

        # Get the size of the shape
        shape_size = self.size()

        # Adjust the clipping area to account for the size of the shape
        clip_max = Vector2Int(clip_max.x - shape_size.width(), clip_max.y - shape_size.height())

        # Initialize the point the shape will move to
        move_to = Vector2Int(to)

        # Ensure that the shape does not move outside the clipping area horizontally or vertically
        move_to.x = min(move_to.x, clip_max.x)
        move_to.y = min(move_to.y, clip_max.y)

        # Ensure that the shape does not move outside the canvas horizontally or vertically
        move_to.x = max(move_to.x, 0)
        move_to.y = max(move_to.y, 0)

        # Update the position of the shape's points
        self.__points[0] = move_to
        self.__points[1] = Vector2Int(move_to.x + shape_size.width(), move_to.y)
        self.__points[2] = move_to + shape_size
        self.__points[3] = Vector2Int(move_to.x, move_to.y + shape_size.height())

        self.__update()

    def unfill(self) -> None:
        self.fill = False

    def move_vertex(self, to: Vector2Int, index: int) -> None:
        assert to is not None and index is not None, "Shape.move_vertex(): to and index must not be None"

        match(index):
            case 0:
                self.__points[0] = Vector2Int(to)
                self.__points[1] = Vector2Int(self.__points[1].x, to.y)
                self.__points[3] = Vector2Int(to.x, self.__points[3].y)
            case 1:
                self.__points[1] = Vector2Int(to)
                self.__points[2] = Vector2Int(to.x, self.__points[2].y)
                self.__points[0] = Vector2Int(self.__points[0].x, to.y)
            case 2:
                self.__points[2] = Vector2Int(to)
                self.__points[3] = Vector2Int(self.__points[3].x, to.y)
                self.__points[1] = Vector2Int(to.x, self.__points[1].y)
            case 3:
                self.__points[3] = Vector2Int(to)
                self.__points[0] = Vector2Int(to.x, self.__points[0].y)
                self.__points[2] = Vector2Int(self.__points[2].x, to.y)
            case _:
                raise(InvalidVertexException(f"Tried to move vertex with index: {int(index)}"))

        self.__update()

    def is_within(self, pos: Vector2Int) -> bool:
        _min, _max = Vector2Int.get_min_max(self.__points)

        if (pos.x > _min.x and pos.x < _max.x) and (pos.y > _min.y and pos.y < _max.y):
            return True
        else:
            return False

    def get_highlighted_vertex(self) -> int | None:
        if self.highlighted_vertex < 0:
            return None
        return self.highlighted_vertex

    def __get_pen(self, scale: float, color: QColor, extra: int = 0) -> QPen:
        return QPen(color, int(Shape.PEN_SIZE + extra * scale))

    def __scale_points(self, scale: float) -> list[QPoint]:
        return [(point * scale).as_qpoint() for point in self.__points]

    def __vertex_size(self, increase: bool = False) -> int:
        scale = self.__scale if self.__scale >= 1 else self.__scale+abs(self.__scale - 1)
        if not increase:
            return int(Shape.VERTEX_SIZE * scale)
        return int((Shape.VERTEX_SIZE + Shape.VERTEX_HIGHLIGHT_GROWTH) * self.__scale)

    def __draw_square(self, painter: QPainter, scale: float):

        if self.selected:
            painter.setBrush(QBrush(self.selected_color, self.fill_pattern))
        elif self.fill:
            painter.setBrush(QBrush(self.fill_pattern_color, self.fill_pattern))
        else:
            painter.setBrush(utils.Empty_Brush)

        if self.get_highlighted_vertex() is not None:
            painter.setPen(self.__get_pen(scale, self.highlighted_color))
        else:
            painter.setPen(self.__get_pen(scale, self.lines_color))
        

        # Get the points and draw the shape
        points = self.__scaled
        _min, _max = Vector2Int.get_min_max(points)
        draw_rect = QRect(_min, _max)

        if self.fill or self.selected:
            painter.fillRect(draw_rect, painter.brush().color())
        painter.drawRect(draw_rect)

        self.__draw_vertex(painter, scale, points)

    def __draw_vertex(self, painter: QPainter, scale: float, points: list[QPoint]):
        # Get the highlighted vertex and points
        h_vertex = self.get_highlighted_vertex()
        # Set the pen and brush
        if h_vertex is None:
            painter.setPen(self.__get_pen(scale, self.vertex_color))
            painter.setBrush(self.vertex_color)
        else:
            painter.setPen(self.__get_pen(scale, self.highlighted_color))
            painter.setBrush(self.highlighted_color)

        index = 0
        while index < len(points):
            p = points[index]
            size = self.__vertex_size(h_vertex == index)
            if h_vertex is not None and h_vertex == index:
                painter.drawRect(p.x() - size // 2, p.y() - size // 2, size, size)
                index += 1
                continue
            painter.drawEllipse(p.x() - size // 2, p.y() - size // 2, size, size)
            index += 1

    def paint(self, painter: QPainter, scale: float):
        
        if scale != self.__scale:
            self.__update_scale(scale)

        self.__draw_square(painter, scale)