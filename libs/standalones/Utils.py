import re
import hashlib

from PyQt5.QtGui import QBrush, QColor

from libs.standalones.MyException import InvalidInstantiation

class utils:
    Empty_Brush = QBrush(QColor(0, 0, 0, 0))

    def __new__(cls: type['utils']) -> 'utils':
        raise InvalidInstantiation("Tried to instantiate 'Utils' class, a data only class.")

    @staticmethod
    def generate_color_by_text(text):
        s = text
        hash_code = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16)
        r = int((hash_code / 255) % 255)
        g = int((hash_code / 65025) % 255)
        b = int((hash_code / 16581375) % 255)
        return QColor(r, g, b, 100)

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