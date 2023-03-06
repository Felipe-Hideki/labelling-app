from typing import overload

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt

from libs.MyException import InvalidInstantiation

class Utils:
    def __new__(cls: type['Utils']) -> 'Utils':
        raise InvalidInstantiation("Tried to instantiate 'Utils' class, a data only class.")

    @staticmethod
    @overload
    def is_type(value, type: type = ...) -> bool: ...
    @staticmethod
    def is_type(*args):
        if type(args[0]) in args[1:]:
            return True
        return False

    @staticmethod
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