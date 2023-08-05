import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QListView, QDialog, QHBoxLayout
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from functions.binary import Bits

class ButtonL(QPushButton):
    def __init__(self, panel, x, y, text_bank, items, buffer, address, num_of_bits):
        super().__init__(panel)
        self.pnl = panel
        self.buf = buffer
        self.addr = address
        self.bits = num_of_bits
        self.txt = text_bank
        self.items = items

        self.setAutoDefault(True)
        self.setFixedWidth(180)
        self.setFont(QFont("Lucida Console", 8))

        self.pnl.setFocusPolicy(0x2)  # Set focus policy to accept focus when clicked
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.pnl and event.type() == 6:  # FocusIn event
            self.pnl.setStyleSheet("background-color: brown")
            self.create_popup_list()
            return True
        return super().eventFilter(obj, event)

    def create_popup_list(self):
        lpnl = QDialog(self.pnl)
        lpnl.setWindowTitle('Popup List')
        lpnl.setGeometry(300, 20, 250, self.pnl.height() - 40)
        layout = QVBoxLayout()

        sl2 = QListView()
        layout.addWidget(sl2)
        model = QStandardItemModel()
        for item in self.items:
            model.appendRow(QStandardItem(self.get_text_short(item)))
        sl2.setModel(model)

        ok = QPushButton('Ok')
        layout.addWidget(ok)
        ok.clicked.connect(lambda: self.on_ok_click(sl2))
        
        cancel = QPushButton('Cancel')
        layout.addWidget(cancel)
        cancel.clicked.connect(lpnl.reject)

        lpnl.setLayout(layout)
        lpnl.exec()

    def on_ok_click(self, list_view):
        index = list_view.currentIndex().row()
        if 0 <= index < len(self.items):
            self.set_bits(self.items[index])
            self.setText(self.get_text_short(self.items[index]))

    def set_bits(self, value):
        Bits.set_bits(self.buf, self.addr, self.bits, value)

    def get_text_short(self, item):
        # Implement your method to get the short text representation from the item
        # For example, if item is an integer, you could return str(item)
        pass

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.panel = QWidget(self)
        self.setCentralWidget(self.panel)

        layout = QHBoxLayout()
        self.panel.setLayout(layout)

        button_l = ButtonL(self.panel, 20, 20, b'text_bank', [1, 2, 3], bytearray(8), 0, 3)
        layout.addWidget(button_l)

        self.setWindowTitle('PyQt Example')
        self.setGeometry(100, 100, 400, 200)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
