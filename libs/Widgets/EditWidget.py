from fast_autocomplete import AutoComplete

from PyQt5.QtWidgets import QWidget, QLineEdit, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QListWidgetItem
from PyQt5.QtCore import QEventLoop, Qt
from PyQt5.QtGui import QKeyEvent, QCloseEvent, QCursor, QFocusEvent

class EditWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.__name_list: dict[str, dict] = {
            "teste1": {},
            "teste2": {},
            "t3": {},
        }
        self.__autocomplete = AutoComplete(words=self.__name_list)
        
        self.loop = QEventLoop()

        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.__on_ok_clicked)
        self.cancel_button.clicked.connect(self.__on_cancel_clicked)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        
        self.buttons_container = QWidget()
        self.buttons_container.setLayout(self.buttons_layout)

        self.v_layout = QVBoxLayout()

        self.input_label = QLabel(self)
        self.input_label.setText("Name:")

        self.input = QLineEdit(self)

        self.input.textChanged.connect(self.__on_text_changed)

        self.list_widget = QListWidget()
        self.list_widget.setSortingEnabled(True)
        self.list_widget.itemDoubleClicked.connect(self.__on_item_double_clicked)
        self.populate_list(self.__name_list.keys())

        self.setWindowModality(Qt.ApplicationModal)

        self.v_layout.addWidget(self.input_label)
        self.v_layout.addWidget(self.input)
        self.v_layout.addWidget(self.list_widget)
        self.v_layout.addWidget(self.buttons_container)

        self.setLayout(self.v_layout)

        super().hide()

    def add_name(self, name: str) -> None:
        self.__name_list[name] = {}
        self.__autocomplete = AutoComplete(words=self.__name_list)

    def get_name(self, title_name="labelling") -> str:
        self.setWindowTitle(title_name)
        self.show()
        self.loop.exec()
        self.clearFocus()
        return self.input.text()
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.__on_cancel_clicked()
        return super().closeEvent(a0)

    def show(self) -> None:
        mousepos = QCursor.pos()
        self.move(mousepos.x(), mousepos.y())
        self.input.setText("")
        self.input.setFocus()
        return super().show()

    def hide(self) -> None:
        self.loop.quit()
        return super().hide()
    
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if (a0.key() == Qt.Key_Enter or a0.key() == Qt.Key_Return) and self.input.hasFocus():
            self.__on_ok_clicked()

    def populate_list(self, dictionary: list[str]) -> None:
        self.list_widget.clear()
        for elem in dictionary:
            self.list_widget.addItem(elem)

    def __on_item_double_clicked(self, item: QListWidgetItem) -> None:
        self.input.setText(item.text())
        self.__on_ok_clicked()

    def __on_text_changed(self, text: str) -> None:
        if self.__autocomplete is None:
            return
        
        if text == "":
            self.populate_list(self.__name_list.keys())
            return

        self.populate_list([found[0] for found in self.__autocomplete.search(text)])

    def __on_ok_clicked(self) -> None:
        if self.list_widget.currentItem() is not None and self.input.text() == "":
            self.input.setText(self.list_widget.currentItem().text())
        if self.input.text() not in self.__name_list:
            self.add_name(self.input.text())
        self.hide()
    
    def __on_cancel_clicked(self) -> None:
        self.input.setText("")
        self.hide()