from PyQt5.QtWidgets import QWidget, QLineEdit, QListWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class SearchList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mItems = []
        self.sItems = []
        self.txt = None

        layout = QVBoxLayout(self)

        self.tb = QLineEdit(self)
        self.tb.setPlaceholderText("Search...")
        self.tb.textChanged.connect(self.tb_textChanged)
        layout.addWidget(self.tb)

        self.lv = QListWidget(self)
        layout.addWidget(self.lv)

        self.lv.itemActivated.connect(self.lv_itemActivated)
        self.lv.setAlternatingRowColors(True)

    def doTableListbox(self, textBank, items):
        self.txt = textBank
        self.mItems = items
        self.lv.itemCount = len(self.mItems)
        self.tb_textChanged()

    def tb_textChanged(self):
        self.sItems = [index for index, item in enumerate(self.mItems) if self.tb.text().lower() in item.lower()]
        self.lv.clear()
        for index in self.sItems:
            item_text = f"{str(index).rjust(5)} | {self.getText(index)}"
            self.lv.addItem(item_text)

    def getText(self, index):
        return self.txt[self.mItems[index]].decode("utf-8")

    def lv_itemActivated(self, item):
        index = int(item.text().split('|')[0].strip())
        if index in self.mItems:
            # You can do something here with the selected index
            print(f"Selected Index: {index}")