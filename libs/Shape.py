from enum import IntEnum

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from libs.ShapePoints import ShapePoints
from libs.Vector import Vector2Int
from libs.MyException import ShapeNoPointsException, InvalidVertexException

class Position(IntEnum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_RIGHT = 2
    BOTTOM_LEFT = 3

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3
    
class Shape:
    DEFAULT_LINE_COLOR = QColor(255, 255, 255, 255)
    DEFAULT_VERTEX_COLOR = QColor(124, 252, 0, 255)
    DEFAULT_HIGHLIGHT_COLOR = QColor(242, 0, 0, 255)
    DEFAULT_SELECTED_COLOR = QColor(0, 60, 255, 100)
    DEFAULT_FILL_COLOR = QColor(100, 100, 100, 100)
    DEFAULT_FILL_PATTERN_COLOR = QColor(100, 100, 100, 150)
    DEFAULT_FILL_PATTERN = Qt.BDiagPattern

    VERTEX_SIZE = 3
    VERTEX_HIGHLIGHT_GROWTH = 2
    
    def __init__(self, name: str, points: ShapePoints) -> None:
        self.name = name
        self.__points = points
        self.isVisible = True
        self.highlighted_vertex = -1
        self.fill = False
        self.selected = False

        self.lines_color = Shape.DEFAULT_LINE_COLOR
        self.vertex_color = Shape.DEFAULT_VERTEX_COLOR
        self.highlighted_color = Shape.DEFAULT_HIGHLIGHT_COLOR
        self.selected_color = Shape.DEFAULT_SELECTED_COLOR
        self.fill_color = Shape.DEFAULT_FILL_COLOR
        self.fill_pattern = Shape.DEFAULT_FILL_PATTERN
        self.fill_pattern_color = Shape.DEFAULT_FILL_PATTERN_COLOR

        if points is None:
            self.__points = ShapePoints([])

    def get_middle(self) -> Vector2Int:
        return self.top_left() + self.size() / 2

    def top_left(self) -> Vector2Int:
        return Vector2Int.get_min_max(self.__points)[0]
    
    def bot_right(self) -> Vector2Int:
        return Vector2Int.get_min_max(self.__points)[1]
    
    def width(self) -> int:
        min, max = Vector2Int.get_min_max(self.__points)
        return max.x - min.x
    
    def height(self) -> int:
        min, max = Vector2Int.get_min_max(self.__points)
        return max.y - min.y
    
    def size(self) -> Vector2Int:
        min, max = Vector2Int.get_min_max(self.__points)
        width = max.x - min.x
        height = max.y - min.y

        return Vector2Int(width, height)

    def closest_vertex(self, pos: Vector2Int, limit: float) -> tuple[int, float] | tuple[None, None]:
        index = 0
        while index < len(self.__points):
            dist = Vector2Int.distance(self.__points[index], pos)
            if dist <= limit:
                return index, dist
            index += 1
        return None, None
    
    def has_points(self) -> bool:
        return len(self.__points) > 0

    def move_by(self, amount: Vector2Int, clip_max: Vector2Int) -> None:
        self.move(self.top_left() + amount, clip_max)

    def move(self, to: Vector2Int, clip_max: Vector2Int) -> None:
        # Get the size of the shape
        shape_size = self.size()

        # Adjust the clipping area to account for the size of the shape
        clip_max = Vector2Int(clip_max.x - shape_size.x, clip_max.y - shape_size.y)

        # Initialize the point the shape will move to
        move_to = Vector2Int(to)

        # Ensure that the shape does not move outside the clipping area horizontally or vertically
        move_to.x = min(move_to.x, clip_max.x)
        move_to.y = min(move_to.y, clip_max.y)

        # Ensure that the shape does not move outside the canvas horizontally or vertically
        move_to.x = max(move_to.x, 0)
        move_to.y = max(move_to.y, 0)

        # Update the position of the shape's points
        self.__points[TOP_LEFT] = move_to
        self.__points[TOP_RIGHT] = Vector2Int(move_to.x + shape_size.x, move_to.y)
        self.__points[BOTTOM_RIGHT] = move_to + shape_size
        self.__points[BOTTOM_LEFT] = Vector2Int(move_to.x, move_to.y + shape_size.y)

    def unfill(self) -> None:
        self.fill = False

    def move_vertex(self, to: Vector2Int = None, index: Position | int = None) -> None:
        index = self.get_highlighted_vertex() if index is None else index
        to = self.__points[index] if to is None else to
        assert index is not None

        match(index):
            case Position.TOP_LEFT:
                self.__points[TOP_LEFT] = Vector2Int(to)
                self.__points[TOP_RIGHT] = Vector2Int(self.__points[TOP_RIGHT].x, to.y)
                self.__points[BOTTOM_LEFT] = Vector2Int(to.x, self.__points[BOTTOM_LEFT].y)
            case Position.TOP_RIGHT:
                self.__points[TOP_RIGHT] = Vector2Int(to)
                self.__points[BOTTOM_RIGHT] = Vector2Int(to.x, self.__points[BOTTOM_RIGHT].y)
                self.__points[TOP_LEFT] = Vector2Int(self.__points[TOP_LEFT].x, to.y)
            case Position.BOTTOM_RIGHT:
                self.__points[BOTTOM_RIGHT] = Vector2Int(to)
                self.__points[BOTTOM_LEFT] = Vector2Int(self.__points[BOTTOM_LEFT].x, to.y)
                self.__points[TOP_RIGHT] = Vector2Int(to.x, self.__points[TOP_RIGHT].y)
            case Position.BOTTOM_LEFT:
                self.__points[BOTTOM_LEFT] = Vector2Int(to)
                self.__points[TOP_LEFT] = Vector2Int(to.x, self.__points[TOP_LEFT].y)
                self.__points[BOTTOM_RIGHT] = Vector2Int(self.__points[BOTTOM_RIGHT].x, to.y)
            case _:
                raise(InvalidVertexException(f"Tried to move vertex with index: {int(index)}"))

    def is_within(self, pos: Vector2Int) -> bool:
        min, max = Vector2Int.get_min_max(self.__points)
        
        if (pos.x > min.x and pos.x < max.x) and (pos.y > min.y and pos.y < max.y):
            return True
        else:
            return False

    def get_highlighted_vertex(self) -> int | None:
        if self.highlighted_vertex < 0:
            return None
        return self.highlighted_vertex

    def _draw_lines(self, painter: QPainter):
        if not self.has_points():
            raise ShapeNoPointsException()

        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(self.lines_color)

        if self.fill:
            painter.setBrush(QBrush(self.fill_pattern_color, self.fill_pattern))

        if self.get_highlighted_vertex() is not None and not self.selected:
            painter.setPen(self.highlighted_color)
        
        if self.selected:
            painter.setBrush(QBrush(self.selected_color, self.fill_pattern))

        points = self.__points.to_QPointF()
        line_path = QPainterPath(points[0])

        index = 1
        while index < len(points):
            line_path.lineTo(points[index])
            index += 1
        line_path.lineTo(points[0])

        painter.drawPath(line_path)

    def _draw_vertex(self, painter: QPainter):
        if not self.has_points():
            raise ShapeNoPointsException()
        h_vertex = self.get_highlighted_vertex()
        points = self.__points.to_QPointF()
        painter.setPen(self.vertex_color)
        painter.setBrush(self.vertex_color)

        index = 0
        while index < len(points):
            p = points[index]
            if h_vertex is not None and h_vertex == index:
                painter.setPen(self.highlighted_color)
                painter.setBrush(self.highlighted_color)
                painter.drawEllipse(p, Shape.VERTEX_SIZE + Shape.VERTEX_HIGHLIGHT_GROWTH, Shape.VERTEX_SIZE + Shape.VERTEX_HIGHLIGHT_GROWTH)
                painter.setBrush(self.vertex_color)
                painter.setPen(self.vertex_color)
                index += 1
                continue
            painter.drawEllipse(p, Shape.VERTEX_SIZE, Shape.VERTEX_SIZE)
            index += 1

    def _fill(self, painter: QPainter):
        if not self.has_points():
            raise ShapeNoPointsException()

        painter.setPen(self.fill_color)
        painter.setBrush(QBrush(self.fill_color))

        if self.selected:
            painter.setPen(self.lines_color)
            painter.setBrush(QBrush(self.selected_color))

        min, max = Vector2Int.get_min_max(self.__points)

        painter.drawRect(min.x, min.y, self.width(), self.height())

    def paint(self, painter: QPainter):
        if not self.has_points():
            raise ShapeNoPointsException()
        
        self._draw_lines(painter)
        if self.fill or self.selected:
            self._fill(painter)
        self._draw_vertex(painter)  