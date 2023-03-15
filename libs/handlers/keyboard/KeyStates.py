from enum import Enum

class KeyStates(Enum):
    KEY_DOWN = 0
    KEY_UP = 1
    KEY_CHANGE = 2
    
    def __str__(self) -> str:
        return self.name
