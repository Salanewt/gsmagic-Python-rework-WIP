import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QToolBar, QAction, QFileDialog
from functions.binary import Bits
from eText import Text_Editor
from eAbility import Ability_Editor
from eClass import Class_Editor


class Main_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gsmagic")
        self.setGeometry(100, 100, 800, 600)
        self.rom = None
        self.romfn = ""
        self.version = -1
        self.filetable = -1
        self.language = None
        self.palPath = None
        self.init_ui()

    def openROMdialogue(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open a GBA ROM", "", "GBA files (*.gba)")
        if filename:
            self.openROM(filename)

    def openROM(self, filename):
        # TODO: If new filename is error/incompatible, revert to old file.
        # mainMem.setPath(filename)
        # vstr = "" #Dim vstr As String = ""
        if filename.lower().endswith(".gba"):  # Load entire ROM to buffer; GBA ROMs are maxed at 32 MB.
            rom = Bits.open_file(filename)
            if rom is None:
                print("Error reading ROM file.")
                return

            rom_header = Bits.get_string(rom, 0xA0, 15)
            if rom_header in ["Golden_Sun_AAGS", "GOLDEN_SUN_AAGS", "OugonTaiyo_AAGS"]:
                # (U) GS1
                # Italy GS1
                # (J) GS1
                version = 0
                filetable = 0x08320000
            elif rom_header in ["GOLDEN_SUN_BAGF", "OUGONTAIYO_BAGF"]:
                version = 1
                filetable = 0x08680000
            elif rom_header == "MARIOTENNISABTM":
                version = 11
                filetable = 0x08C28000
            elif rom_header == "MARIOGOLFGBABMG":
                version = 10
                filetable = 0x08800000
            else:
                # default:
                #     MessageBox.Show("Not a compatible ROM.");
                #     break;
                print("Not a compatible ROM.")
                return

            language = chr(rom[0xAF])
            if language == 'E' and version == 1:  # Chinese check
                if (Bits.get_int32(rom, 0x08090000 & 0x01FFFFFF) == 0xEA00002E and
                    Bits.get_int32(rom, 0x08090004 & 0x01FFFFFF) == 0x51AEFF24 and
                    Bits.get_int32(rom, 0x08090008 & 0x01FFFFFF) == 0x21A29A69 and
                    Bits.get_int32(rom, 0x0809000C & 0x01FFFFFF) == 0x0A82843D):
                    language = 'C'
            elif version == 0:
                if language in ['E', 'I']:
                    filetable = 0x08320000
                elif language == 'J':
                    filetable = 0x08317000
                elif language == 'D':
                    filetable = 0x0831FE00
                elif language in ['F', 'S']:
                    filetable = 0x08321800

            # File table verification.
            if ((Bits.get_int32(rom, filetable & 0x01FFFFFF) >> 24) != 8 or
                    Bits.get_int32(rom, (filetable + 4) & 0x01FFFFFF) != filetable):
                # Incompatible
                pass

            # TODO: Reorganize repointed data from Atrius's editor back into where they should belong.
            # Text data, filetable/map code data, Innate psys.
            # count_freespace()
            # init_globals
            # with (obj_MasterEditor) { sel=6*(global.version>=10); event_user(0); }

        romfn = filename
        # Properties.Settings.Default.LastRom = filename
        # Properties.Settings.Default.Save()
        # if palPath is None:
        #     palPath = os.path.join(os.path.dirname(filename), "palette.bin")

    def openFile(self, filename):
        try:
            with open(filename, "rb") as file:
                return file.read()
        except Exception as e:
            print("Error opening file:", str(e))
            return None

    def saveROMdialogue(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save ROM File", "", "GBA (*.gba)")
        if filename:
            self.saveROM(filename)

    def saveROM(self, filename):
        success = self.saveFile(filename, self.rom)
        if success:
            self.setWindowTitle("ROM saved successfully.")
        else:
            self.setWindowTitle("Error saving ROM.")

    def init_ui(self):
        # Create a File menu under the main menu bar
        file_menu = self.menuBar().addMenu("File")

        # Add "Open File" action to the File menu
        open_action = QAction("Open ROM", self)
        open_action.triggered.connect(self.openROMdialogue)
        file_menu.addAction(open_action)

        # Add "Save File" action to the File menu
        save_action = QAction("Save As...", self)
        save_action.triggered.connect(self.saveROMdialogue)
        file_menu.addAction(save_action)

        # Create a QTabWidget as the container for tabs
        tab_container = QTabWidget(self)
        self.setCentralWidget(tab_container)

        # Create tabs and add objects to them
        tab1 = Text_Editor()
        tab_container.addTab(tab1, "Text")

        tab2 = Ability_Editor()
        tab_container.addTab(tab2, "Abilities")

        tab3 = Class_Editor()
        tab_container.addTab(tab3, "Classes")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Main_Window()
    form.setFixedSize(form.size())
    form.show()
    sys.exit(app.exec_())
