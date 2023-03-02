from dataclasses import dataclass
from typing import overload

from PyQt5.QtCore import QPointF

from libs.Vector import Vector2Int
from libs.Utils import Utils as utils

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

    @staticmethod
    @overload
    def square(pos: Vector2Int, size=int) -> 'ShapePoints' : ...
    @overload
    @staticmethod
    def square(min: Vector2Int, max:Vector2Int) -> 'ShapePoints': ...
    @staticmethod
    def square(*args, **kwargs) -> 'ShapePoints':
        vertexes = [None] * 4
        extracted_args = utils.extract_vals(args, kwargs, ['pos', 'size'], [Vector2Int, int], 2)

        if extracted_args:
            pos: Vector2Int = Vector2Int(extracted_args[0])
            size: float = extracted_args[1]

            vertexes[TOP_LEFT] = pos
            vertexes[TOP_RIGHT] = pos + Vector2Int(size, 0)
            vertexes[BOTTOM_RIGHT] = pos + (Vector2Int.one() * size)
            vertexes[BOTTOM_LEFT] = pos + Vector2Int(0, size)

            return ShapePoints(vertexes)
        
        extracted_args = utils.extract_vals(args, kwargs, ['min', 'max'], [Vector2Int, Vector2Int], 2)

        if extracted_args:
            min = extracted_args[0]
            max = extracted_args[1]

            vertexes = [None] * 4
            vertexes[TOP_LEFT] = Vector2Int(min)
            vertexes[TOP_RIGHT] = Vector2Int(max.x, min.y)
            vertexes[BOTTOM_RIGHT] = Vector2Int(max)
            vertexes[BOTTOM_LEFT] = Vector2Int(min.x, max.y)

            return ShapePoints(vertexes)

    def __getitem__(self, index: int) -> Vector2Int:
        return self.points[index]

    def __setitem__(self, index: int, val: Vector2Int):
        self.points[index] = val

    def __len__(self):
        return len(self.points)

    def __repr__(self) -> str:
        return self.points.__repr__()