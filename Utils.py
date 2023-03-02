from typing import overload
from libs.MyException import InvalidInstantiation

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt

class Utils:
    def __new__(cls: type['Utils']) -> 'Utils':
        raise InvalidInstantiation("Tried to instantiate 'Utils' class, a data only class.")

    @staticmethod
    def type_equals(val: object, **types: type ) -> bool:
        return val in types

    @staticmethod
    def extract_vals(args: tuple, kwargs: dict, keys: list[str], match_types: list[type] = [], rlen = 1) -> list | None:
        '''
        Extract wanted value from args and kwargs if it has, else None
        Usage: extract_vals(args, kwargs, [KeyI])
        '''
        index = 0
        matched = []
        if len(args) < rlen:
            for key in keys:
                if key in kwargs and (len(match_types) == 0 or match_types[index] == type(kwargs[key])):
                    matched.append(kwargs[key])
                    continue
                return None
            return matched if len(matched) > 0 else None
        for i in range(rlen):
            if len(match_types) == 0 or type(args[i]) == match_types[index]:
                matched.append(args[i])
                index += 1
        return matched if len(matched) == len(match_types) else None

    def modifiers_to_string(modifiers: Qt.KeyboardModifiers) -> str | None:
        mod_string = ''
        if modifiers & Qt.ShiftModifier:
            mod_string += 'Shift+'
        if modifiers & Qt.ControlModifier:
            mod_string += 'Ctrl+'
        if modifiers & Qt.AltModifier:
            mod_string += 'Alt+'
        if modifiers & Qt.MetaModifier:
            mod_string += 'Meta+'
        return mod_string[:-1] if mod_string else None

    @staticmethod
    def get_mainWindow() -> QMainWindow:
        print(f"{QApplication.instance()=} | {QApplication.instance().activeWindow()=}")
        return QApplication.instance().activeWindow()