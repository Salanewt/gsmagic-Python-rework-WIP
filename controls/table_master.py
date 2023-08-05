from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox, QLineEdit, QApplication
from PyQt5.QtCore import Qt
from controls.prop_listpanel_a import ButtonL
from controls.prop_listpanel_b import ButtonL2
from controls.prop_searchbox import SearchList
from controls.prop_spinbox import DataSpinbox
from controls.prop_textbox import DataTextbox

class Table_Manager:
    def __init__(self):
        self.nuds = []
        self.butls = []
        self.dtbs = []
        self.buf = None
        self.pnl = None
        self.baseAddr = 0
        self.entryLen = 0
        self.entryAddr = 0
        self.cntAddr = None
        self.combo2numeric = 0

    def setPanel(self, panel):
        self.pnl = panel

    def setTable(self, buffer, baseA, eLen):
        self.buf = buffer
        self.baseAddr = baseA
        self.entryLen = eLen
        self.entryAddr = baseA

    def doLabel(self, x, y, text):
        lbl = QLabel(self.pnl)
        lbl.move(x, y)
        lbl.setText(text)
        return lbl

    def doNud(self, x, y, offset, numOfBits):
        dnud = DataSpinbox()
        nud = dnud.doNud(self.pnl, x, y, self.buf, self.entryAddr + offset, numOfBits)
        nud.mouseClickEvent = lambda event: self.nudrc2(dnud.addr - self.entryAddr, dnud.bits)
        self.nuds.append(dnud)
        return nud

    def nudrc2(self, offset, bits):
        if Qt.ControlModifier not in QApplication.keyboardModifiers():
            return

        if not self.sl:
            return

        for i in range(len(self.sl.sItems)):
            x = self.sl.sItems[i]
            value = self.getBits(self.buf, self.baseAddr + x * self.entryLen + offset, bits)
            j = i
            while j > 0 and self.getBits(self.buf, (self.baseAddr + self.sl.sItems[j - 1] * self.entryLen) + offset, bits) > value:
                self.sl.sItems[j] = self.sl.sItems[j - 1]
                j -= 1
            self.sl.sItems[j] = x

        self.sl.lv.update()

    def doCombo(self, x, y, txt, items, offset, numOfBits):
        if self.combo2numeric == 1:
            return self.doNud(x, y, offset, numOfBits)

        bn = ButtonL()
        bn.doCombo(self.pnl, x, y, txt, items, self.buf, self.entryAddr + offset, numOfBits)
        bn.currentIndexChanged = lambda index, addr=self.entryAddr + offset, num_bits=numOfBits: self.nudrc3(index, self.buf, addr, num_bits)
        self.butls.append(bn)
        return bn

    def nudrc3(self, index, buffer, addr, num_bits):
        bits = buffer[addr] & ~((1 << num_bits) - 1)
        new_value = index & ((1 << num_bits) - 1)
        buffer[addr] = bits | new_value

    def doNamebox(self, x, y, textBuf, index):
        tbx = DataTextbox()
        tbx.doTextbox(self.pnl, x, y, textBuf, index)
        tbx.tbx.editingFinished.connect(self.button_Click)
        self.dtbs.append(tbx)
        return tbx

    def button_Click(self):
        if not self.sl:
            return

        self.sl.lv.update()

    def doTableListbox(self, txt, items):
        self.sl = SearchList()
        self.sl.doTableListbox(self.pnl, txt, items)
        self.sl.lv.itemActivated.connect(self.loadEntry)

        if self.entryLen != 0:
            self.cntAddr = self.doLabel(240, 0, "        ")

    def doTableListbox2(self, txt, items):
        self.sl = SearchList()
        self.sl.doTableListbox2(self.pnl, txt, items)
        self.sl.lv.itemActivated.connect(self.loadEntry)

        if self.entryLen != 0:
            self.cntAddr = self.doLabel(240, 0, "        ")

    def loadEntry(self):
        srcEntry = 0

        if self.sl.lv.selectedItems():
            item = self.sl.lv.selectedItems()[0]
            srcEntry = self.sl.sItems[item.row()]
            entryAddr2 = self.baseAddr + srcEntry * self.entryLen

            if self.entryAddr != 0 and Qt.ControlModifier in QApplication.keyboardModifiers():
                if Qt.ShiftModifier in QApplication.keyboardModifiers():
                    for i in range(self.entryLen):
                        self.buf[entryAddr2 + i] = self.buf[self.entryAddr + i]

            if self.entryLen != 0:
                self.cntAddr.setText("0x{:X}".format(0x8000000 | entryAddr2))

        for dnud in self.nuds:
            dnud.addr = dnud.addr - self.entryAddr + entryAddr2
            dnud.setValue(self.getBits(self.buf, dnud.addr, dnud.bits))

        for bn in self.butls:
            bn.addr = bn.addr - self.entryAddr + entryAddr2
            try:
                bn.setCurrentIndex(self.getBits(self.buf, bn.addr, bn.bits))
            except:
                pass

        for tbx in self.dtbs:
            tbx.theIndex = tbx.baseIndex + srcEntry
            tbx.tbx.setText(tbx.getText())

        self.entryAddr = entryAddr2

    def getBits(self, buffer, addr, num_bits):
        return buffer[addr] & ((1 << num_bits) - 1)

    def setBits(self, buffer, addr, num_bits, value):
        bits = buffer[addr] & ~((1 << num_bits) - 1)
        new_value = value & ((1 << num_bits) - 1)
        buffer[addr] = bits | new_value