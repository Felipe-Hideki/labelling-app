from enum import IntEnum

from PyQt5.QtCore import QSize, pyqtSignal, QObject

from libs.Vector import Vector2Int
from libs.flag  import flags

class Position(IntEnum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_RIGHT = 2
    BOTTOM_LEFT = 3

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3

class CoordinatesSystem:
    '''
    Coordinates system is a class that represents a 2D coordinate system

    Args:
        size (Vector2Int | QSize): The size of the coordinate system
    '''

    def __init__(self, size: Vector2Int | QSize):
        self.__size = Vector2Int(size)
        self.__points: list[Vector2Int] = [None] * 4
        self.resize(self.__size)

    def get_vertice(self, pos: Position) -> Vector2Int:
        '''
        Get the vertice of the coordinate system

        Args:
            pos (Position): The position of the vertice
        '''
        return self.__points[pos]

    def size(self) -> Vector2Int:
        '''
        Get the size of the coordinate system
        '''
        return self.__size
    
    def resize(self, val: Vector2Int):
        '''
        Resize the coordinate system

        Args:
            val (Vector2Int): The new size of the coordinate system
        '''
        self.__points[TOP_LEFT] = Vector2Int(0, 0)
        self.__points[TOP_RIGHT] = Vector2Int(val.x, 0)
        self.__points[BOTTOM_RIGHT] = val
        self.__points[BOTTOM_LEFT] = Vector2Int(0, val.y)

        self.__size = val

    def center(self) -> Vector2Int:
        '''
        Get the center of the coordinate system
        '''
        return self.__points[TOP_LEFT] + self.size() / 2

    def to_global(self, pos: Vector2Int) -> Vector2Int:
        '''
        Convert a position from the coordinate system to the global coordinate system

        Args:
            pos (Vector2Int): The position to convert
        '''
        return pos + self.center()

class Transform(QObject):
    '''
    Transform is a class that represents a transform in the coordinate system

    Args:
        pos (Vector2Int): The position of the transform
        size (Vector2Int): The size of the transform
        cs (CoordinatesSystem): The coordinate system to use
    '''
    on_move = pyqtSignal(Vector2Int)

    def __init__(self, pos: Vector2Int, size: Vector2Int, cs: CoordinatesSystem):
        super().__init__()
        self.__global: CoordinatesSystem = cs
        self.__relative_pos = Vector2Int(pos)
        self.__size = Vector2Int(size)
 
    def to_global(self, pos: Vector2Int) -> Vector2Int:
        '''
        Convert a position relative to the transform to the global coordinate system
        
        Args:
            pos (Vector2Int): The position to convert
        '''
        return self.__global.to_global(pos + self.__relative_pos)

    def top_left(self) -> Vector2Int:
        return self.__relative_pos - self.__size/2
    
    def top_right(self) -> Vector2Int:
        return self.__relative_pos + Vector2Int(self.__size.x, -self.__size.y) / 2
    
    def bot_right(self) -> Vector2Int:
        return self.__relative_pos + self.__size/2
    
    def bot_left(self) -> Vector2Int:
        return self.__relative_pos + Vector2Int(-self.__size.x, self.__size.y) / 2

    def size(self) -> Vector2Int:
        '''
        Get the size of the transform
        '''
        return self.__size
    
    def resize(self, size: Vector2Int):
        '''
        Resize the transform

        Args:
            size (Vector2Int): The new size of the transform
        '''
        assert type(size) == Vector2Int, "Size must be a Vector2Int"
        self.__size = size
        # Move to the same position so the transform doesn't go out of the global coordinate system
        self.move_by(Vector2Int(0, 0))

    def pos(self) -> Vector2Int:
        '''
            Get the position of the transform relative to center of the global coordinate system
        '''
        return self.__relative_pos

    def paint_pos(self) -> Vector2Int:
        '''
        Get the position of the transform relative to the top left corner of the global coordinate system
        '''
        return self.__relative_pos + self.__global.center()

    def move_by(self, amount: Vector2Int):
        '''
        Move the transform by a certain amount

        Args:
            amount (Vector2Int): The amount to move the transform by
        '''
        self.move(self.__relative_pos + amount)

    def move(self, move_to: Vector2Int):
        '''
        Move the transform to a certain position

        Args:
            move_to (Vector2Int): The position to move the transform to
        '''

        to = Vector2Int(move_to)

        bigger_axis_flag: flags = flags(2)

        if self.__size.x > self.__global.size().x:
            bigger_axis_flag.set(0, True)
            self.__relative_pos.x = 0
            if abs(self.pos().x) < abs(to.x):
                to.x = 0
        if self.__size.y > self.__global.size().y:
            bigger_axis_flag.set(1, True)
            self.__relative_pos.y = 0
            if abs(self.pos().y) < abs(to.y):
                to.y = 0

        if bigger_axis_flag.all_true():
            return
        # Check if the position to move + size is outside of the global coordinates system
        # if so then move the position to the closest point inside the global coordinates system
        # then move the object to the position

        # Fictional point at the point `to` + half of the size of the object
        transform_border = to + self.size()/2
        global_border = self.__global.size()/2

        if transform_border.x > global_border.x and not bigger_axis_flag[0]:
            to.x -= transform_border.x - global_border.x
        if transform_border.y > global_border.y and not bigger_axis_flag[1]:
            to.y -= transform_border.y - global_border.y

        transform_border = to - self.size()/2

        if transform_border.x < -global_border.x and not bigger_axis_flag[0]:
            to.x += abs(transform_border.x + global_border.x)
        if transform_border.y < -global_border.y and not bigger_axis_flag[1]:
            to.y += abs(transform_border.y + global_border.y)

        self.__relative_pos = to
        self.on_move.emit(self.__relative_pos)