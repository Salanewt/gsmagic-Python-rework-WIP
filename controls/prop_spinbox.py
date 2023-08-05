from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtGui import QFont

class DataSpinbox(QDoubleSpinBox):
    def __init__(self, pnl, x, y, buffer, address, numOfBits):
        super().__init__(pnl)
        self.buf = buffer
        self.addr = address
        self.bits = numOfBits
        self.setRange(0, (1 << numOfBits) - 1)
        self.setDecimals(0)
        self.setSingleStep(1)
        self.setFont(QFont("Lucida Console", 8))
        self.move(x, y)
        self.valueChanged.connect(self.nudChanged)

    def nudChanged(self, value):
        for j in range(0, self.bits, 8):
            self.buf[self.addr + (j >> 3)] = int(value) & 0xFF
            value >>= 8
