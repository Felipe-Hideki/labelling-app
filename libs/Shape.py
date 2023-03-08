from PyQt5.QtCore import *
from PyQt5.QtGui import *

from libs.ShapePoints import ShapePoints
from libs.Vector import Vector2Int, Vector2
from libs.MyException import ShapeNoPointsException, InvalidVertexException
from libs.CoordinatesSystem import Position, TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT

    
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

    PEN_SIZE = 1
    
    def __init__(self, name: str, points: ShapePoints) -> None:
        assert points is not None, "Shape.__init__(): points must not be None"
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

        _min, _max = Vector2Int.get_min_max(self.__points)
        self.__size = QSize(_max.x - _min.x, _max.y - _min.y)
        self.__pos = Vector2(Vector2(self.__size) / 2 + _min)
        self.__scale = 1.0
        self.__scaled = [point.as_qpoint() for point in self.__points]

    def top_left(self) -> Vector2Int:
        return self.__points[TOP_LEFT]
    
    def bot_right(self) -> Vector2Int:
        return self.__points[BOTTOM_RIGHT]

    def width(self) -> int:
        return self.__size.width()
    
    def height(self) -> int:
        return self.__size.height()
    
    def size(self) -> QSize:
        return self.__size
    
    def __update(self) -> None:
        self.__update_size()
        self.__update_pos()
        self.__update_scale(self.__scale)

    def __update_size(self) -> None:
        self.__size = QSize(self.bot_right().x - self.top_left().x, self.bot_right().y - self.top_left().y)
    
    def __update_pos(self) -> None:
        self.__pos = Vector2(Vector2(self.__size) / 2 + self.top_left())

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
        self.__points[TOP_LEFT] = move_to
        self.__points[TOP_RIGHT] = Vector2Int(move_to.x + shape_size.width(), move_to.y)
        self.__points[BOTTOM_RIGHT] = move_to + shape_size
        self.__points[BOTTOM_LEFT] = Vector2Int(move_to.x, move_to.y + shape_size.width())

        self.__update()

    def unfill(self) -> None:
        self.fill = False

    def move_vertex(self, to: Vector2Int, index: Position | int) -> None:
        assert to is not None and index is not None, "Shape.move_vertex(): to and index must not be None"

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
            
        print(self.__points)

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
        size = Vector2(self.__size)
        _min, _max = Vector2Int.get_min_max(self.__points)
        _min = Vector2(_min)
        _max = Vector2(_max)
        scaled = [None] * 4
        scaled[TOP_LEFT] = round(_min * self.__scale)
        scaled[TOP_RIGHT] = round(Vector2(_max.x, _min.y) * self.__scale)
        scaled[BOTTOM_RIGHT] = round(_max * self.__scale)
        scaled[BOTTOM_LEFT] = round(Vector2(_min.x, _max.y) * self.__scale)

        # scaled[TOP_LEFT] = round((self.__pos - size / 2) * scale)
        # scaled[TOP_RIGHT] = round((self.__pos + Vector2Int(size.x, -size.y)  / 2) * scale)
        # scaled[BOTTOM_RIGHT] = round((self.__pos + size / 2) * scale)
        # scaled[BOTTOM_LEFT] = round((self.__pos + Vector2Int(-size.x, size.y) / 2) * scale)

        return [point.as_qpoint() for point in scaled]

    def __draw_square(self, painter: QPainter, scale: float):

        if self.selected:
            painter.setBrush(QBrush(self.selected_color, self.fill_pattern))
        elif self.fill:
            painter.setBrush(QBrush(self.fill_pattern_color, self.fill_pattern))
        else:
            painter.setBrush(QColor(0, 0, 0, 0))

        if self.get_highlighted_vertex() is not None and not self.selected:
            painter.setPen(self.__get_pen(scale, self.highlighted_color))
        else:
            painter.setPen(self.__get_pen(scale, self.lines_color))
        

        # Get the points and draw the shape
        points = self.__scaled
        _min, _max = Vector2Int.get_min_max(points)
        draw_rect = QRect(_min, _max)

        painter.fillRect(draw_rect, painter.brush().color())
        painter.drawRect(draw_rect)

        # line_path = QPainterPath(points[0])

        # index = 1
        # for point in points[1:]:
        #     line_path.lineTo(point)
        # line_path.lineTo(points[0])

        # painter.fillRect(line_path.boundingRect(), painter.brush().color())
        # painter.drawPath(line_path)

        self.__draw_vertex(painter, scale, points)

    def __draw_vertex(self, painter: QPainter, scale: float, points: list[QPoint]):
        # if self.fill or self.selected:
        #     self.__fill(painter, scale, points)

        # Get the highlighted vertex and points
        h_vertex = self.get_highlighted_vertex()
        # Set the pen and brush
        painter.setPen(self.__get_pen(scale, self.vertex_color))
        painter.setBrush(self.vertex_color)

        index = 0
        while index < len(points):
            p = points[index]
            if h_vertex is not None and h_vertex == index:
                # if the vertex is highlighted, draw a bigger circle around it with the highlighted color
                painter.setPen(self.__get_pen(scale, self.highlighted_color))
                painter.setBrush(self.highlighted_color)
                size = int((self.VERTEX_SIZE + self.VERTEX_HIGHLIGHT_GROWTH) * scale)
                painter.drawEllipse(p.x() - int(size / 2), p.y() - int(size / 2), size, size)
                painter.setBrush(self.vertex_color)
                painter.setPen(self.__get_pen(scale, self.vertex_color))
                index += 1
                continue
            size = int(self.VERTEX_SIZE * scale)
            painter.drawEllipse(p.x() - int(size / 2), p.y() - int(size / 2), size, size)
            index += 1

    def paint(self, painter: QPainter, scale: float):
        
        if scale != self.__scale:
            self.__update_scale(scale)

        self.__draw_square(painter, scale)
        s = self.__scale
        self.__scale = 1
        self.__draw_square(painter, scale)
        self.__scale = s