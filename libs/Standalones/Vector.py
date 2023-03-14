from PyQt5.QtCore import QPointF, QPoint, QSize, QRect

from dataclasses import dataclass
from math import sqrt, floor
from typing import overload, Union

from libs.standalones.Utils import Utils as utils

@dataclass
class Vector2:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, qsize: QSize) -> None: ...

    @overload
    def __init__(self, x: int | float, y: int | float) -> None: ...

    @overload
    def __init__(self, vec2: 'Vector2Int') -> None: ...

    @overload
    def __init__(self, qpoint: QPoint | QPointF) -> None: ...

    def __init__(self, *args) -> None:
        args_size = len(args)
        if args_size == 0:
            self.x = 0
            self.y = 0
        elif args_size == 2:
            assert utils.is_type(args[0], int, float) and utils.is_type(args[0], int, float), \
                "Vector2Int.__init__(): args[0] and args[1] must be int or float"
            self.x = float(args[0])
            self.y = float(args[1])
        elif args_size == 1 and type(args[0]) == QSize:
            self.__from_QSize(args[0])
        elif args_size == 1 and (type(args[0]) == QPoint or type(args[0]) == QPointF):
            self.__from_QPoint(args[0])
        elif args_size == 1 and type(args[0]) == Vector2Int or type(args[0]) == Vector2:
            self.__from_Vec2(args[0])
        else:
            raise TypeError(f"{len(args)} arguments given, {[type(arg) for arg in args]}")

    def __from_QPoint(self, qpointf: QPointF | QPoint) -> None:
        self.x = qpointf.x()
        self.y = qpointf.y()

    def __from_QSize(self, qsize: QSize) -> None:
        self.x = qsize.width()
        self.y = qsize.height()

    def __from_Vec2(self, vec2: 'Vector2Int') -> None:
        self.x = vec2.x
        self.y = vec2.y

    def __add__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> 'Vector2':
        if type(coord) == QPoint or type(coord) == QPointF:
            return Vector2(self.x + coord.x(), self.y + coord.y())
        elif type(coord) == Vector2Int or type(coord) == Vector2:
            return Vector2(self.x + coord.x, self.y + coord.y)
        elif type(coord) == QSize:
            return Vector2(self.x + coord.width(), self.y + coord.height())
        else:
            raise TypeError(__class__)

    def __radd__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> 'Vector2':
        return self.__add__(coord)

    def __sub__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> 'Vector2':
        if type(coord) == QPoint or type(coord) == QPointF:
            return Vector2(self.x - coord.x(), self.y - coord.y())
        elif type(coord) == Vector2Int or type(coord) == Vector2:
            return Vector2(self.x - coord.x, self.y - coord.y)
        elif type(coord) == QSize:
            return Vector2(self.x - coord.width(), self.y - coord.height())
        else:
            raise TypeError(__class__)
    
    def __rsub__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> 'Vector2':
        if type(coord) == QPoint or type(coord) == QPointF:
            return Vector2(coord.x() - self.x, coord.y() - self.y)
        elif type(coord) == Vector2Int or type(coord) == Vector2:
            return Vector2(coord.x - self.x, coord.y - self.y)
        elif type(coord) == QSize:
            return Vector2(coord.width() - self.x, coord.height() - self.y)
        else:
            raise TypeError(__class__)

    def __mul__(self, num: int | float) -> 'Vector2Int':
        return Vector2(self.x * num, self.y * num)

    def __rmul__(self, num: int | float) -> 'Vector2Int':
        return self.__mul__(num)

    def __truediv__(self, val: int | float) -> 'Vector2Int':
        return Vector2(self.x / val, self.y / val)

    def __floordiv__(self, val: int | float) -> 'Vector2Int':
        return Vector2(self.x // val, self.y // val)

    def __neg__(self) -> 'Vector2Int':
        return Vector2(-self.x, -self.y)

    def __gt__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> bool:
        if type(coord) == QPoint or type(coord) == QPointF:
            return self.x > coord.x() and self.y > coord.y()
        elif type(coord) == Vector2Int or type(coord) == Vector2:
            return self.x > coord.x and self.y > coord.y
        elif type(coord) == QSize:
            return self.x > coord.width() and self.y > coord.height()
        else:
            raise TypeError(__class__)

    def __lt__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> bool:
        if type(coord) == QPoint or type(coord) == QPointF:
            return self.x < coord.x() and self.y < coord.y()
        elif type(coord) == Vector2Int or type(coord) == Vector2:
            return self.x < coord.x and self.y < coord.y
        elif type(coord) == QSize:
            return self.x < coord.width() and self.y < coord.height()
        else:
            raise TypeError(__class__)
    
    def __ge__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> bool:
        return self.__gt__(coord) or self.__eq__(coord)

    def __le__(self, coord: Union[QPoint, QPointF, 'Vector2Int', 'Vector2', QSize]) -> bool:
        return self.__lt__(coord) or self.__eq__(coord)

    def __eq__(self, coord: Union[QPointF, 'Vector2']) -> bool:
        if type(coord) == QPointF:
            return self.x == coord.x() and self.y == coord.y()
        elif type(coord) == Vector2:
            return self.x == coord.x and self.y == coord.y
        else:
            raise TypeError(__class__)

    def __ne__(self, coord: Union[QPointF, 'Vector2']) -> bool:
        return not self.__eq__(coord)

    def __abs__(self) -> 'Vector2':
        return Vector2(abs(self.x), abs(self.y))

    def __round__(self) -> 'Vector2':
        return Vector2(round(self.x), round(self.y))
    
    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"

    @staticmethod
    def one() -> 'Vector2':
        '''
            Returns a Vector2(1, 1)
        '''
        return Vector2(1, 1)
    @staticmethod
    def right() -> 'Vector2':
        '''
            Returns a Vector2(1, 0)
        '''
        return Vector2(1, 0)
    @staticmethod
    def left() -> 'Vector2':
        '''
            Returns a Vector2(-1, 0)
        '''
        return Vector2(-1, 0)
    @staticmethod
    def up() -> 'Vector2':
        '''
            Returns a Vector2(0, -1)
        '''
        return Vector2(0, -1)
    @staticmethod
    def down() -> 'Vector2':
        '''
            Returns a Vector2(0, 1)
        '''
        return Vector2(0, 1)

    @staticmethod
    def distance(p1: 'Vector2', p2: 'Vector2') -> float:
        diff = p1 - p2
        return diff.magnitude()
    
    @staticmethod
    def normalize(point: 'Vector2') -> 'Vector2':
        mag = point.magnitude()
        if mag > 0:
            return Vector2(point.x / mag, point.y / mag)
        return Vector2(0, 0)

    def as_qpointf(self) -> QPointF:
        return QPointF(self.x, self.y)

    def as_qpoint(self) -> QPoint:
        return QPoint(round(self.x), round(self.y))
    
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

    def scaled(self, scale: float) -> 'Vector2':
        '''
            Inverse scale the vector by the given scale

            Args:
                scale (float): The scale to divide the vector by
        '''
        return self / scale
    
    @overload
    def clip(self, rect: QRect) -> None: ...

    @overload
    def clip(self, _min: Union['Vector2Int', 'Vector2'], _max: Union['Vector2Int', 'Vector2']) -> None: ...

    def clip(self, *args) -> None:
        if len(args) == 1 and type(args[0]) == QRect:
            rect: QRect = args[0]
            self.x = min(rect.bottomRight().x(), max(self.x, rect.topLeft().x()))
            self.y = min(rect.bottomRight().y(), max(self.y, rect.topLeft().y()))
        elif len(args) == 2 and type(args[0]) == Vector2Int or type(args[0]) == Vector2\
              and type(args[1]) == Vector2Int or type(args[1]) == Vector2:
            _min: Vector2Int = args[0]
            _max: Vector2Int = args[1]
            self.x = min(_max.x, max(self.x, _min.x))
            self.y = min(_max.y, max(self.y, _min.y))
        else:
            raise TypeError(__class__)
@dataclass
class Vector2Int:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, qsize: QSize) -> None: ...

    @overload
    def __init__(self, x: int | float, y: int | float) -> None: ...

    @overload
    def __init__(self, vec2: 'Vector2Int') -> None: ...

    @overload
    def __init__(self, qpoint: QPoint | QPointF) -> None: ...

    def __init__(self, *args) -> None:
        args_size = len(args)
        if args_size == 0:
            self.x = 0
            self.y = 0
        elif args_size == 2:
            assert utils.is_type(args[0], int, float) and utils.is_type(args[0], int, float), \
                "Vector2Int.__init__(): args[0] and args[1] must be int or float"
            self.x = args[0]
            self.y = args[1]
        elif args_size == 1 and type(args[0]) == QSize:
            self.__from_QSize(args[0])
        elif args_size == 1 and (type(args[0]) == QPoint or type(args[0]) == QPointF):
            self.__from_QPoint(args[0])
        elif args_size == 1 and type(args[0]) == Vector2Int:
            self.__from_Vec2(args[0])
        else:
            raise TypeError(__class__)

    def __from_QPoint(self, qpointf: QPointF | QPoint) -> None:
        self.x = int(qpointf.x())
        self.y = int(qpointf.y())

    def __from_QSize(self, qsize: QSize) -> None:
        self.x = qsize.width()
        self.y = qsize.height()

    def __from_Vec2(self, vec2: 'Vector2Int') -> None:
        self.x = int(vec2.x)
        self.y = int(vec2.y)

    def __add__(self, coord: Union[QPoint, 'Vector2Int', 'Vector2', QSize]) -> 'Vector2Int':
        if type(coord) == QPoint:
            return Vector2Int(self.x + coord.x(), self.y + coord.y())
        elif type(coord) == Vector2Int:
            return Vector2Int(self.x + coord.x, self.y + coord.y)
        elif type(coord) == Vector2:
            return Vector2(self.x + coord.x, self.y + coord.y)
        elif type(coord) == QSize:
            return Vector2Int(self.x + coord.width(), self.y + coord.height())
        else:
            raise TypeError(__class__)

    def __radd__(self, coord: Union[QPoint, 'Vector2Int', QSize]) -> 'Vector2Int':
        return self.__add__(coord)

    def __sub__(self, coord: Union[QPoint, 'Vector2Int', 'Vector2', QSize]) -> 'Vector2Int':
        if type(coord) == QPoint:
            return Vector2Int(self.x - coord.x(), self.y - coord.y())
        elif type(coord) == Vector2Int:
            return Vector2Int(self.x - coord.x, self.y - coord.y)
        elif type(coord) == Vector2:
            return Vector2(self.x + coord.x, self.y + coord.y)
        elif type(coord) == QSize:
            return Vector2Int(self.x - coord.width(), self.y - coord.height())
        else:
            raise TypeError(__class__)
    
    def __rsub__(self, coord: Union[QPoint, 'Vector2Int', Vector2, QSize]) -> 'Vector2Int':
        if type(coord) == QPoint:
            return Vector2Int(coord.x() - self.x, coord.y() - self.y)
        elif type(coord) == Vector2Int:
            return Vector2Int(coord.x - self.x, coord.y - self.y)
        elif type(coord) == Vector2:
            return Vector2(self.x + coord.x, self.y + coord.y)
        elif type(coord) == QSize:
            return Vector2Int(coord.width() - self.x, coord.height() - self.y)
        else:
            raise TypeError(__class__)

    def __mul__(self, num: int | float) -> 'Vector2Int':
        return Vector2Int(round(self.x * num), round(self.y * num))

    def __rmul__(self, num: int | float) -> 'Vector2Int':
        return self.__mul__(num)

    def __truediv__(self, val: int | float) -> 'Vector2Int':
        return Vector2Int(round(self.x / val), round(self.y / val))

    def __floordiv__(self, val: int | float) -> 'Vector2Int':
        return Vector2Int(self.x // val, self.y // val)

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
    @overload
    def get_min_max(points: list[QPoint]) -> tuple[QPoint, QPoint]: ...

    @staticmethod
    def get_min_max(points: list['Vector2Int']) -> tuple['Vector2Int', 'Vector2Int']:
        assert len(points) > 0, "Cannot get min/max of empty list"
        assert type(points[0]) == Vector2Int or type(points[0]) == QPoint, "Cannot get min/max of list of non-Vector2Ints or QPoints"

        if type(points[0]) == QPoint:
            _min_x = min([p.x() for p in points])
            _min_y = min([p.y() for p in points])
            _max_x = max([p.x() for p in points])
            _max_y = max([p.y() for p in points])

            _min = QPoint(_min_x, _min_y)
            _max = QPoint(_max_x, _max_y)
            
        else:
            _min_x = min([p.x for p in points])
            _min_y = min([p.y for p in points])
            _max_x = max([p.x for p in points])
            _max_y = max([p.y for p in points])

            _min = Vector2Int(_min_x, _min_y)
            _max = Vector2Int(_max_x, _max_y)
        return _min, _max

    @staticmethod
    def one() -> 'Vector2Int':
        '''
            Returns a Vector2(1, 1)
        '''
        return Vector2Int(1, 1)
    @staticmethod
    def right() -> 'Vector2Int':
        '''
            Returns a Vector2(1, 0)
        '''
        return Vector2Int(1, 0)
    @staticmethod
    def left() -> 'Vector2Int':
        '''
            Returns a Vector2(-1, 0)
        '''
        return Vector2Int(-1, 0)
    @staticmethod
    def up() -> 'Vector2Int':
        '''
            Returns a Vector2(0, -1)
        '''
        return Vector2Int(0, -1)
    @staticmethod
    def down() -> 'Vector2Int':
        '''
            Returns a Vector2(0, 1)
        '''
        return Vector2Int(0, 1)

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