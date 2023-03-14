from PyQt5.QtCore import QRunnable

class Funcs(QRunnable):
    def __init__(self, funcs: set[any]):
        super().__init__()
        self.funcs = funcs

        self.setAutoDelete(False)

    def run(self):
        for func in self.funcs:
            func()