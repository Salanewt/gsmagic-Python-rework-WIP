from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QFont
from functions.compression import Compression
from functions.binary import Bits

class DataTextbox(QWidget):
    def __init__(self):
        super().__init__()
        self.pnl = None
        self.txt = None
        self.baseIndex = 0
        self.theIndex = 0
        self.tbx = QLineEdit()
        self.bn = QPushButton("Edit")
        self.bn.clicked.connect(self.button_click)

        # Set the font manually (Consolas, size 8)
        font = QFont("Consolas", 8)
        self.tbx.setFont(font)
        self.bn.setFont(font)

    def do_textbox(self, panel, x, y, text_buf, index):
        self.pnl = panel

        self.tbx.move(x, y)
        self.tbx.setFixedWidth(120)
        self.pnl.layout().addWidget(self.tbx)

        self.txt = text_buf
        self.baseIndex = index
        self.theIndex = index

        self.bn.move(x + self.tbx.width(), y)
        self.bn.setFixedWidth(50)
        self.bn.setFixedHeight(20)
        self.pnl.layout().addWidget(self.bn)

    def button_click(self):
        # Implement the logic of the button_Click method here in Python
        str_data = self.tbx.text()
        bytes_data = bytearray(0x200)
        a = 0
        b = 0
        while a < len(str_data):
            if str_data[a] == '[':
                num = 0
                a += 1
                while str_data[a] != ']':
                    num = num * 10 + int(str_data[a]) - 0x30
                    a += 1
                a += 1
                bytes_data[b] = num
                b += 1
            elif str_data[a:a+2] == '\r\n':
                a += 2
            else:
                bytes_data[b] = ord(str_data[a])
                a += 1
                b += 1
        b += 1  # Add null character at the end

        src_entry = self.theIndex * 4
        neaddr = 0xC300 + Bits.getInt32(self.txt, src_entry + 4)
        lendif = Bits.getInt32(self.txt, src_entry) - Bits.getInt32(self.txt, src_entry + 4) + b
        c = src_entry + 4
        while Bits.getInt32(self.txt, c) != 0:
            Bits.setInt32(self.txt, c, Bits.getInt32(self.txt, c) + lendif)
            c += 4
        c = 0xC300 + Bits.getInt32(self.txt, c - 4) - lendif
        while self.txt[c] != 0:
            c += 1
        if Bits.getInt32(self.txt, src_entry + 4) != 0:
            self.txt[neaddr:neaddr+c] = self.txt[0xC300 + Bits.getInt32(self.txt, src_entry + 4):0xC300 + Bits.getInt32(self.txt, src_entry + 4) + c]
        d = 0xC300 + Bits.getInt32(self.txt, src_entry)
        while b > 0:
            self.txt[d] = bytes_data[d - (0xC300 + Bits.getInt32(self.txt, src_entry))]
            d += 1
            b -= 1

        Compression.comptext(self.txt, self.rom)
        # Perform any other operations related to listView1 here
