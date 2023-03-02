from PyQt5.QtCore import QPointF, QPoint, QSize, QRect

from dataclasses import dataclass
from math import sqrt
from typing import overload, Union

from libs.Utils import Utils as utils

@dataclass
class Vector2Int:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, qsize: QSize) -> None: ...

    @overload
    def __init__(self, x: int, y: int) -> None: ...

    @overload
    def __init__(self, vec2: 'Vector2Int') -> None: ...

    @overload
    def __init__(self, qpoint: QPoint) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        size = utils.extract_vals(args, kwargs, ['qsize'], [QSize])

        if size:
            self.__from_QSize(size[0])
            return

        vec2 = utils.extract_vals(args, kwargs, ['vec2'], [Vector2Int])
        
        if vec2:
            self.__from_Vec2(vec2[0])
            return

        qpoint = utils.extract_vals(args, kwargs, ['qpoint'], [QPoint])

        if qpoint:
            self.__from_QPointF(qpoint[0])
            return

        properties = utils.extract_vals(args, kwargs, ['x', 'y'], [int, int], 2)

        if properties:
            self.x = int(properties[0])
            self.y = int(properties[1])
            return
        
        properties = utils.extract_vals(args, kwargs, ['x', 'y'], [float, float], 2)

        if properties:
            self.x = int(properties[0])
            self.y = int(properties[1])
            return

        self.x = 0
        self.y = 0

    def __from_QPointF(self, qpointf: QPointF | QPoint) -> None:
        self.x = int(qpointf.x())
        self.y = int(qpointf.y())

    def __from_QSize(self, qsize: QSize) -> None:
        self.x = qsize.width()
        self.y = qsize.height()

    def __from_Vec2(self, vec2: 'Vector2Int') -> None:
        self.x = int(vec2.x)
        self.y = int(vec2.y)

    def __add__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> 'Vector2Int':
        if type(coord) == QPoint:
            return Vector2Int(self.x + coord.x(), self.y + coord.y())
        elif type(coord) == Vector2Int:
            return Vector2Int(self.x + coord.x, self.y + coord.y)
        elif type(coord) == QSize:
            return Vector2Int(self.x + coord.width(), self.y + coord.height())
        else:
            raise TypeError(__class__)

    def __sub__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> 'Vector2Int':
        if type(coord) == QPoint:
            return Vector2Int(self.x - coord.x(), self.y - coord.y())
        elif type(coord) == Vector2Int:
            return Vector2Int(self.x - coord.x, self.y - coord.y)
        elif type(coord) == QSize:
            return Vector2Int(self.x - coord.width(), self.y - coord.height())
        else:
            raise TypeError(__class__)
    
    def __mul__(self, num: int | float) -> 'Vector2Int':
        return Vector2Int(int(self.x * num), int(self.y * num))

    def __truediv__(self, val: int | float) -> 'Vector2Int':
        return Vector2Int(int(self.x / val), int(self.y / val))

    def __neg__(self) -> 'Vector2Int':
        return Vector2Int(-self.x, -self.y)

    def __gt__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> bool:
        if type(coord) == QPoint:
            return self.x > coord.x() and self.y > coord.y()
        elif type(coord) == Vector2Int:
            return self.x > coord.x and self.y > coord.y
        elif type(coord) == QSize:
            return self.x > coord.width() and self.y > coord.height()
        else:
            raise TypeError(__class__)

    def __lt__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> bool:
        if type(coord) == QPoint:
            return self.x < coord.x() and self.y < coord.y()
        elif type(coord) == Vector2Int:
            return self.x < coord.x and self.y < coord.y
        elif type(coord) == QSize:
            return self.x < coord.width() and self.y < coord.height()
        else:
            raise TypeError(__class__)
    
    def __ge__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> bool:
        return self.__gt__(coord) or self.__eq__(coord)

    def __le__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> bool:
        return self.__lt__(coord) or self.__eq__(coord)

    def __eq__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> bool:
        if type(coord) == QPoint:
            return self.x == coord.x() and self.y == coord.y()
        elif type(coord) == Vector2Int:
            return self.x == coord.x and self.y == coord.y
        elif type(coord) == QSize:
            return self.x == coord.width() and self.y == coord.height()
        else:
            raise TypeError(__class__)

    def __ne__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> bool:
        return not self.__eq__(coord)

    def __abs__(self) -> 'Vector2Int':
        return Vector2Int(abs(self.x), abs(self.y))

    def __repr__(self) -> str:
        return f"Vector2Int({self.x}, {self.y})"

    @staticmethod
    def get_min_max(points: list['Vector2Int']) -> tuple['Vector2Int', 'Vector2Int']:
        max = Vector2Int(vec2=points[0])
        min = Vector2Int(vec2=points[0])
        for p in points:
            if p.y > max.y:
                max.y = p.y
            if p.x > max.x:
                max.x = p.x
            if p.y < min.y:
                min.y = p.y
            if p.x < min.x:
                min.x = p.x
        return min, max

    @staticmethod
    def one() -> 'Vector2Int':
        '''
            Returns a Vector2(1, 1)
        '''
        return Vector2Int(1, 1)

    @staticmethod
    def distance(p1: 'Vector2Int', p2: 'Vector2Int') -> float:
        diff = p1 - p2
        return diff.magnitude()
    
    @staticmethod
    def normalize(point: 'Vector2Int') -> QPointF:
        mag = point.magnitude()
        if mag > 0:
            return QPointF(point.x / mag, point.y / mag)
        return QPointF(0, 0)

    def as_qpoint(self) -> QPoint:
        return QPoint(self.x, self.y)

    def magnitude(self) -> float:
        return sqrt(abs(self.x) * abs(self.x) + abs(self.y) * abs(self.y))
    
    def scale(self, scale: float) -> None:
        '''
            Inverse scale the vector by the given scale

            Args:
                scale (float): The scale to divide the vector by
        '''
        self.x = int(self.x / scale)
        self.y = int(self.y / scale)

    def normalized(self) -> QPointF:
        mag = self.magnitude()
        if mag > 0:
            return QPointF(self.x / mag, self.y / mag)
        return QPointF(0, 0)

    def scaled(self, scale: float) -> 'Vector2Int':
        '''
            Inverse scale the vector by the given scale

            Args:
                scale (float): The scale to divide the vector by
        '''
        return self / scale
    
    @overload
    def clip(self, rect: QRect) -> None: ...

    @overload
    def clip(self, _min: 'Vector2Int', _max: 'Vector2Int') -> None: ...

    def clip(self, *args) -> None:
        if len(args) == 1 and type(args[0]) == QRect:
            rect: QRect = args[0]
            self.x = min(rect.bottomRight().x(), max(self.x, rect.topLeft().x()))
            self.y = min(rect.bottomRight().y(), max(self.y, rect.topLeft().y()))
        elif len(args) == 2 and type(args[0]) == Vector2Int and type(args[1]) == Vector2Int:
            _min: Vector2Int = args[0]
            _max: Vector2Int = args[1]
            self.x = min(_max.x, max(self.x, _min.x))
            self.y = min(_max.y, max(self.y, _min.y))
        else:
            raise TypeError(__class__)