from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QLine, QPoint, QSize, QRect
from PyQt5.QtGui import QCursor

from libs.Canvas.Shape import Shape
from libs.Standalones.Vector import Vector2Int
from libs.Standalones.MyException import InvalidInstantiation

class CanvasHelper:
    """
    A data only class, containing static methods for interacting with the canvas.
    """
    MIN_DIST_HIGHLIGHT = 8.00
    MIN_DIST_CREATE = 10.00
    MIN_DIST_TO_MOVE = 1.3
    MAX_ZOOM = 5.00

    def __new__(cls: type['CanvasHelper']) -> 'CanvasHelper':
        raise InvalidInstantiation("Tried to instantiate 'CanvasHelper' class, a data only class.")

    @staticmethod
    def get_rect(min: Vector2Int, max: Vector2Int) -> QRect:
        """
        Returns a QRect from a minimum and maximum position.

        Args:
            min (Vector2Int): The minimum position.
            max (Vector2Int): The maximum position.
        """
        return QRect(min.x, min.y, max.x - min.x, max.y - min.y)

    @staticmethod
    def get_formation(center: Shape, shapes: list[Shape]) -> list[(Shape, Vector2Int)]:
        """
        Returns a list of tuples, containing the shape and the offset from the center shape.

        Args:
            center (Shape): The center shape.
            shapes (list[Shape]): The list of shapes to get the formation of.
        """
        formation: list[(Shape, Vector2Int)] = []
        for shape in shapes:
            formation.append((shape, center.top_left() - shape.top_left()))
        return formation

    @staticmethod
    def move_shapes(mouse_pos: Vector2Int, clicked_shape: Shape, shapes_formation: list[tuple[Shape, Vector2Int]], _max: Vector2Int) -> None:
        """
        Move a list of shapes by a certain amount, based on the position of the mouse.
        
        Args:
            mouse_pos (Vector2Int): The current position of the mouse on the canvas.
            clicked_shape (Shape): The shape that was clicked.
            shapes_formation (list[tuple[Shape, Vector2Int]]): The formation of the shapes.
            _min (Vector2Int): The minimum position of the pixmap.
            _max (Vector2Int): The maximum position of the pixmap.
        """
        
        move_by = mouse_pos - clicked_shape.top_left()
        clicked_shape.move_by(move_by, _max)

        for shape, offset in shapes_formation:
            if shape == clicked_shape:
                continue
            shape.move(clicked_shape.top_left() - offset, _max)

    @staticmethod
    def get_crosshair(mouse_pos: Vector2Int, win_width: int, win_height: int) -> tuple[QLine, QLine]:
        """
        Returns a tuple of 2 QLines, representing the crosshair.

        Args:
            mouse_pos (Vector2Int): The current position of the mouse on the canvas.
            win_width (int): The width of the canvas.
            win_height (int): The height of the canvas.
        """
        hor_pos_left = Vector2Int(0, mouse_pos.y)
        hor_pos_right = Vector2Int(win_width, mouse_pos.y)

        ver_pos_top = Vector2Int(mouse_pos.x, 0)
        ver_pos_bot = Vector2Int(mouse_pos.x, win_height)

        #QLine(Vector2(Left.x, Left.y), Vector2(Right.x, Right.y))
        hor_line = QLine(hor_pos_left.x, hor_pos_left.y, hor_pos_right.x, hor_pos_right.y)
        ver_line = QLine(ver_pos_top.x, ver_pos_top.y, ver_pos_bot.x, ver_pos_bot.y)
        return hor_line, ver_line

    @staticmethod
    def middle_point(size: QSize) -> QPoint:
        """
        Returns the middle point of a QSize.

        Args:
            size (QSize): The size to get the middle point of.
        """
        return QPoint(int(size.width() / 2), int(size.height() / 2))
    
    @staticmethod
    def relative_pos(pos: Vector2Int | QPoint, center: Vector2Int | QPoint) -> Vector2Int:
        if isinstance(pos, QPoint):
            pos = Vector2Int(pos)
        elif isinstance(pos, Vector2Int):
            pos = pos
        else:
            raise TypeError(f"Expected QPoint or Vector2Int, got {type(pos)}")
        
        if isinstance(center, QPoint):
            center = Vector2Int(center)
        elif isinstance(center, Vector2Int):
            center = center
        else:
            raise TypeError(f"Expected QPoint or Vector2Int, got {type(center)}")
        
        return pos - center       

    @staticmethod
    def invert_qpoint(point: QPoint) -> QPoint:
        """
        Returns the inverted QPoint.

        Args:
            point (QPoint): The QPoint to invert.
        """
        return QPoint(-point.x(), -point.y())

    @staticmethod
    def get_within(pos: Vector2Int, shapes: list[Shape]) -> tuple[Shape, tuple[Shape, int]]:
        found = False
        selected_shape = None

        min_dist = CanvasHelper.MIN_DIST_HIGHLIGHT+1
        closest = (None, None)

        for shape in shapes:
            within = shape.is_within(pos)
            if within and not shape.selected and not found:
                found = True
                selected_shape = shape
            if within and shape.selected and not found:
                selected_shape = shape
            index, dist = shape.closest_vertex(pos, min_dist)
            if index is not None and dist < min_dist:
                min_dist = dist
                closest = (shape, index)

        return selected_shape, closest


    @staticmethod
    def get_shape_within(pos: Vector2Int, shapes: list[Shape]) -> Shape | None:
        """
        Returns the shape that contains the point 'pos', or None if no shape contains the point.

        Args:
            pos (Vector2Int): The point to check.
            shapes (list[Shape]): The list of shapes to check.
        """
        selected = None
        for shape in shapes:
            if shape.is_within(pos) and not shape.selected:
                return shape
            elif shape.is_within(pos) and shape.selected:
                selected = shape
        return selected

    @staticmethod
    def get_closest_shape_vertex(pos: Vector2Int, shapes: list[Shape]) -> tuple[Shape, int] | tuple[None, None]:
        """
            Returns a tuple with the closest shape and vertex index to the point 'pos', or an None tuple if no shape vertex is close enough.

            Args:
                pos (Vector2Int): The point to check.
                shapes (list[Shape]): The list of shapes to check.
        """
        min_dist = CanvasHelper.MIN_DIST_HIGHLIGHT+1
        closest = (None, None)
            
        for s in shapes:
            index, dist = s.closest_vertex(pos, min_dist)
            if index is not None and dist < min_dist:
                min_dist = dist
                closest = (s, index)
                
        return closest