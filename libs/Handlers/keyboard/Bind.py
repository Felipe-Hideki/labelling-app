import keyboard

from libs.handlers.keyboard.Key import Key
from libs.handlers.keyboard.KeyStates import KeyStates
from libs.handlers.keyboard.Funcs import Funcs

class bind:
    def __init__(self, key: Key, state_type: KeyStates, toggle: bool, funcs: list[any] = None, state: bool = False):
        if funcs is None:
            funcs = []

        self.key = key
        self.state_type = state_type
        self.toggle = toggle
        self.funcs = set(funcs)
        self.state = state
        self.runnable = Funcs(self.funcs)

    def add_func(self, func: any):
        self.funcs.add(func)
        self.runnable.funcs.add(func)