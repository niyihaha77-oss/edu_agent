from enum import Enum
from enum import StrEnum,auto

class Direction(str,Enum):
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'

print(Direction.UP.value)


class Color(StrEnum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
print(Color.RED)