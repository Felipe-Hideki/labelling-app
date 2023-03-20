from typing import overload
import re

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

from libs.standalones.MyException import InvalidInstantiation

class Utils:
    Empty_Brush = QBrush(QColor(0, 0, 0, 0))

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
    def natural_sort(list, key=lambda s:s):
        """
        Sort the list into natural alphanumeric order.
        """
        def get_alphanum_key_func(key):
            convert = lambda text: int(text) if text.isdigit() else text
            return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]
        sort_key = get_alphanum_key_func(key)
        list.sort(key=sort_key)


    @staticmethod
    def get_mainWindow() -> QMainWindow:
        print(f"{QApplication.instance()=} | {QApplication.instance().activeWindow()=}")
        return QApplication.instance().activeWindow()