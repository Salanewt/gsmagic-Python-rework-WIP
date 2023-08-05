from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from functions.binary import Bits
from controls.table_master import Table_Manager
from controls.prop_listpanel_b import ButtonL2

class Class_Editor(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

    def text(self):
        return "Classes"

    def load(self, tabControl1):
        self.tm.setTable(self.test.rom, 0xC15F4, 0x54)
        self.tm.setPanel(tabControl1.SelectedTab)
        w = tabControl1.SelectedTab.Width
        h = tabControl1.SelectedTab.Height

        ct = [0] * 256
        for i in range(2915 - 2915, 3159 - 2915):
            n = Bits.getInt32(self.test.rom, 0xC15F4 + i * 0x54)
            if n < 0x100:
                if ct[n] == 0:
                    ct[n] = 2915 + i

        ctstr = [None] * 256
        for i in range(0x100):
            if ct[i] != 0:
                ctstr[i] = f"{str(i).rjust(3, ' ')}|{Bits.getTextShort(self.txt, ct[i])}"
            else:
                ct[i] = -1
                ctstr[i] = f"{str(i).rjust(3, ' ')}|"

        items = list(range(2915, 3159))
        self.tm.doTableListbox(self.txt, items)

        pnlx = w // 2 - 135
        pnly = 160
        self.status = self.tm.doLabel(pnlx, pnly - 20, "")
        self.tm.doNamebox(pnlx, pnly, self.txt, 2915)

        psyNames = [f"{str(ind2).rjust(3, ' ')}|{Bits.getTextShort(self.txt, 1447 + ind2)}" for ind2 in range(734)]

        fi = self.tm.doLabel(pnlx, pnly + 40, "Class Type")
        self.tm.doCombo(pnlx, pnly + 60, self.txt, ct, 0, 32)

        eNames = ["Venus", "Mercury", "Mars", "Jupiter"]
        for i in range(4):
            self.tm.doLabel(pnlx, pnly + 100 + i * 20, eNames[i] + " Lv.")
            self.tm.doNud(pnlx + 120, pnly + 100 + i * 20, 4 + i, 8).Width = 60

        pnlx += 260
        self.tm.doLabel(pnlx + 20, pnly - 20, "Level")
        self.tm.doLabel(pnlx + 60 + 20, pnly - 20, "Ability")
        for i in range(16):
            lbln = self.tm.doLabel(pnlx, pnly + i * 20, str(i + 1))
            lbln.Width = 20
            lv = self.tm.doNud(pnlx + 20, pnly + i * 20, 0x10 + 2 + i * 4, 8)
            lv.Width = 60
            self.tm.doCombo(pnlx + 60 + 20, pnly + i * 20, Bits.textToBytes(psyNames), Bits.numList(734), 0x10 + 0 + i * 4, 16)

        pnlx -= 200
        lbl = self.tm.doLabel(pnlx, pnly + 330, "Effect Weaknesses (+25% chance for non-flat effects.)")
        lbl.Width = 400
        for i in range(3):
            self.tm.doNud(pnlx + i * 100, pnly + 350, 0x50 + i, 8)

        self.tm.sl.lv.SelectedIndexChanged += self.loadEntry
        pnly = 0

        tm2 = Table_Manager()
        text = ["Original", "1 Party System", "2 Party System", "PC Class Type Charts"]
        ctb = ButtonL2()
        ctb.doCombo(tabControl1.SelectedTab, pnlx + 115, pnly, Bits.textToBytes(text), Bits.numList(4), self.test.rom, tm2)

        tm2.setTable(self.test.rom, Bits.getInt32(self.test.rom, 0xB0280) & 0x1FFFFFF, 0x40)
        tm2.setPanel(tabControl1.SelectedTab)
        tm2.doLabel(pnlx, pnly, "Class Type Patch: ")
        pnly = 30
        for i in range(4):
            tm2.doLabel(pnlx + (i * 115), pnly, eNames[i])
        for j in range(4):
            tm2.doLabel(pnlx - 70, pnly + j * 20 + 20, eNames[j])
        pnly += 20

        for j in range(4):
            for i in range(4):
                ctrl = tm2.doCombo(pnlx + (i * 115), pnly + j * 20, self.txt, ct, (j * 4 + i) * 4, 32)
                ctrl.Width = 115

        tm2.loadEntry(None, None)

    def loadEntry(self, sender, e):
        self.status.Text = ""
        if sender is not None:
            lv = sender
            if lv.SelectedIndices.Count != 1:
                return
            rom = self.test.rom
            srcEntry = self.tm.sl.sItems[lv.SelectedIndices[0]]
            srcClassType = Bits.getInt32(rom, 0xC15F4 + srcEntry * 0x54)
            eVen = rom[0xC15F4 + srcEntry * 0x54 + 4]
            eMer = rom[0xC15F4 + srcEntry * 0x54 + 5]
            eMar = rom[0xC15F4 + srcEntry * 0x54 + 6]
            eJup = rom[0xC15F4 + srcEntry * 0x54 + 7]
            for i in range(243, srcEntry, -1):
                if srcClassType != Bits.getInt32(rom, 0xC15F4 + i * 0x54):
                    continue
                if eVen < rom[0xC15F4 + i * 0x54 + 4]:
                    continue
                if eMer < rom[0xC15F4 + i * 0x54 + 5]:
                    continue
                if eMar < rom[0xC15F4 + i * 0x54 + 6]:
                    continue
                if eJup < rom[0xC15F4 + i * 0x54 + 7]:
                    continue
                self.status.Text = Bits.getTextShort(self.txt, 2915 + i) + f" ({rom[0xC15F4 + i * 0x54 + 4]} {rom[0xC15F4 + i * 0x54 + 5]} {rom[0xC15F4 + i * 0x54 + 6]} {rom[0xC15F4 + i * 0x54 + 7]})"
                self.status.Width = 200
                break


class BoxWithPercentLabel:
    def __init__(self):
        self.numbox = None
        self.percentLabel = None

    def init(self, x, y, title, tm, offset):
        pnlx = x
        pnly = y
        boxw = 60
        tm.doLabel(pnlx, pnly, title)
        self.numbox = tm.doNud(pnlx + 80 + 40, pnly, offset, 8)
        self.numbox.Width = boxw
        self.percentLabel = tm.doLabel(pnlx + 80 + 40 + boxw, pnly + 2, "0%   ")
        self.numbox.ValueChanged += self.boxChange

    def boxChange(self, sender, e):
        self.percentLabel.Text = f"{self.numbox.Value * 10}%"
