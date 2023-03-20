from enum import Enum

class ActionBind(Enum):
    next_image = 0
    prev_image = 1
    create_shape = 2
    delete_shape = 3
    multi_select = 4
    move = 5
    edit = 6

    def __str__(self) -> str:
        return self.name