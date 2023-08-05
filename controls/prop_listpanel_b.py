import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QListView, QDialog, QHBoxLayout, QMessageBox, QComboBox, QHBoxLayout
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from functions.binary import Bits

class ButtonL2(QPushButton):
    def __init__(self):
        super().__init__()
        self.pnl = None
        self.buf = None
        self.txt = None
        self.items = None
        self.tm = None
        self.value = 0
        self.pcchart = 0
        self.pcchartbutton = None

    def doCombo(self, panel, x, y, textBank, items, buffer, tm):
        self.tm = tm
        self.pnl = panel
        self.setAutoEllipsis(True)
        self.move(x, y)
        self.resize(180, 20)
        self.setFont(QFont("Lucida Console", 8))
        self.pnl.layout().addWidget(self)
        self.buf = buffer
        self.txt = textBank
        self.items = items

        self.previewKeyDown.connect(self.comboKeyDown)
        self.clicked.connect(self.test)

        patch = [
            [0x58D6, 0x2E02, 0xD103, 0x2F05, 0xD101, 0x260D, 0xE004, 0x2E06, 0xD102, 0x2F07, 0xD100, 0x260E],
            [0x58D6, 0xE009, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
            [0x58D6, 0x2F04, 0xDB08, 0x3614, 0xE006, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
            [0x01B9, 0x185B, 0x58D6, 0xE007, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000]
        ]

        for j in range(4):
            i = 0
            while i < 12:
                if Bits.getInt16(self.buf, 0xB01BA + i * 2) != patch[j][i]:
                    break
                i += 1
            if i == 12:
                break
            self.value += 1

        if self.value < 4:
            self.setText(Bits.getTextShort(self.txt, self.items[self.value]))

        ok = QPushButton("0")
        ok.move(x + 180, y)
        ok.resize(20, 20)
        self.pnl.layout().addWidget(ok)
        ok.clicked.connect(self.PCChartButtonClick)
        self.pcchartbutton = ok

        return self

    def PCChartButtonClick(self):
        self.pcchart += 1
        if self.pcchart == 8:
            self.pcchart = 0
        if self.value != 3:
            self.pcchart = 0
        self.pcchartbutton.setText(str(self.pcchart))
        self.tm.loadEntry(None, (Bits.getInt32(self.buf, 0xB0280) & 0x1FFFFFF) + self.pcchart * 0x40)

    def test(self):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            return

        self.lpnl = QWidget()
        self.curList = self
        self.lpnl.show()

        layout = QVBoxLayout(self.lpnl)
        self.sl2 = QComboBox()
        self.sl2.addItems(Bits.getTextShort(self.txt, item) for item in self.items)
        layout.addWidget(self.sl2)

        ok = QPushButton("Ok")
        layout.addWidget(ok)
        ok.clicked.connect(self.okClick)

        cancel = QPushButton("Cancel")
        layout.addWidget(cancel)
        cancel.clicked.connect(self.cancelClick)

        self.pnl.layout().addWidget(self.lpnl)
        self.lpnl.raise_()
        self.sl2.setFocus()

    def okClick(self):
        self.lpnl.hide()
        self.setFocus()
        value2 = self.sl2.currentIndex()
        self.applyPatch(value2)
        self.setText(Bits.getTextShort(self.txt, self.sl2.itemText(value2)))

        if self.value != 3:
            self.pcchart = 0
            self.PCChartButtonClick()
            self.pcchartbutton.setEnabled(False)
        else:
            self.pcchartbutton.setEnabled(True)

    def applyPatch(self, value2):
        if value2 == 3:
            if self.value == 3:
                return
            dr = QMessageBox.question(self, "Requires repointing. Continue?", 
                                      "With this option, Class Type table will be repointed to 0xC6F70, to expand it for individual PCs. "
                                      "This may or may not overwrite important data. (On a clean ROM, it should be fine.) Continue?", 
                                      QMessageBox.Ok | QMessageBox.Cancel)

            if dr == QMessageBox.Cancel:
                return

            src = Bits.getInt32(self.buf, 0xB0280) & 0x1FFFFFF
            des = 0xC6F70
            Bits.setInt32(self.buf, 0xB0280, 0x08000000 | des)

            for i in range(0x40):
                self.buf[des + i] = self.buf[src + i]
                self.buf[des + 0x40 + i] = self.buf[src + i]
                self.buf[des + 0x80 + i] = self.buf[src + i]
                self.buf[des + 0xC0 + i] = self.buf[src + i]

            party2 = 0
            if self.value == 2:
                party2 = 20

            for i in range(0, 0x40, 4):
                Bits.setInt32(self.buf, des + 0x100 + i, Bits.getInt32(self.buf, src + i) + party2)
                Bits.setInt32(self.buf, des + 0x140 + i, Bits.getInt32(self.buf, src + i) + party2)
                Bits.setInt32(self.buf, des + 0x180 + i, Bits.getInt32(self.buf, src + i) + party2)
                Bits.setInt32(self.buf, des + 0x1C0 + i, Bits.getInt32(self.buf, src + i) + party2)

            if self.value == 0:
                Bits.setInt32(self.buf, des + 0x168, 13)
                Bits.setInt32(self.buf, des + 0x1D4, 14)

        patch = [
            [0x58D6, 0x2E02, 0xD103, 0x2F05, 0xD101, 0x260D, 0xE004, 0x2E06, 0xD102, 0x2F07, 0xD100, 0x260E],
            [0x58D6, 0xE009, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
            [0x58D6, 0x2F04, 0xDB08, 0x3614, 0xE006, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],
            [0x01B9, 0x185B, 0x58D6, 0xE007, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000]
        ]

        for i in range(12):
            Bits.setInt16(self.buf, 0xB01BA + i * 2, patch[value2][i])

        self.value = value2

        if self.value != 3:
            self.pcchart = 0

    def cancelClick(self):
        self.lpnl.hide()
        self.setFocus()

    def comboKeyDown(self, e):
        if e.key() == Qt.Key_Up:
            if self.value > 0:
                self.applyPatch(self.value - 1)
                self.setText(Bits.getTextShort(self.txt, self.items[self.value]))
        elif e.key() == Qt.Key_Down:
            if self.value < len(self.items) - 1:
                self.applyPatch(self.value + 1)
                self.setText(Bits.getTextShort(self.txt, self.items[self.value]))

class YourWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        # Your other widgets can be added to this layout

        # Example usage of ButtonL2
        button = ButtonL2()
        layout.addWidget(button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = YourWidget()
    widget.show()
    sys.exit(app.exec_())
