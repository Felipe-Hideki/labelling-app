from dataclasses import dataclass
from typing import overload

from PyQt5.QtCore import QPointF

from libs.standalones.Vector import Vector2Int
from libs.standalones.Utils import Utils as utils

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3

@dataclass
class ShapePoints:
    points = []
    
    def __init__(self, points: list[Vector2Int]) -> None:
        self.points = list(points)

    def to_QPointF(self) -> list[QPointF]:
        qpointfs: list[QPointF] = []
        index = 0
        try:
            while index < len(list(self.points)):
                qpointfs.append(QPointF(self.points[index].x, self.points[index].y))
                index += 1

            return qpointfs
        except Exception as e:
            print(f"{type(self.points[index])=}")
            raise(e)

    def copy(self) -> 'ShapePoints':
        return ShapePoints(self.points)

    @staticmethod
    @overload
    def square(pos: Vector2Int, size: int) -> 'ShapePoints' : ...
    @overload
    @staticmethod
    def square(min: Vector2Int, max:Vector2Int) -> 'ShapePoints': ...
    @staticmethod
    def square(*args) -> 'ShapePoints':
        assert len(args) == 2, "ShapePoints.square(): args must be 2"
        assert utils.is_type(args[0], Vector2Int) and utils.is_type(args[1], Vector2Int, int), \
            "ShapePoints.square(): args[0] must be Vector2Int and args[1] must be Vector2Int or int"
        vertexes = [None] * 4
        if type(args[1]) == int:
            pos: Vector2Int = Vector2Int(args[0])
            size: float = args[1]

            vertexes[TOP_LEFT] = pos
            vertexes[TOP_RIGHT] = pos + Vector2Int(size, 0)
            vertexes[BOTTOM_RIGHT] = pos + (Vector2Int.one() * size)
            vertexes[BOTTOM_LEFT] = pos + Vector2Int(0, size)

            return ShapePoints(vertexes)
        elif type(args[1]) == Vector2Int:
            _min = args[0]
            _max = args[1]

            vertexes = [None] * 4
            vertexes[TOP_LEFT] = Vector2Int(_min)
            vertexes[TOP_RIGHT] = Vector2Int(_max.x, _min.y)
            vertexes[BOTTOM_RIGHT] = Vector2Int(_max)
            vertexes[BOTTOM_LEFT] = Vector2Int(_min.x, _max.y)

            return ShapePoints(vertexes)

    def __getitem__(self, index: int) -> Vector2Int:
        return self.points[index]

    def __setitem__(self, index: int, val: Vector2Int):
        self.points[index] = val

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)
    
    def __next__(self):
        return next(self.points)

    def __repr__(self) -> str:
        return self.points.__repr__()