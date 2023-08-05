from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import QRect

class Text_Editor(QWidget):
    def __init__(self):
        super().__init__()

        # Create a vertical layout for the Text Editor widget
        layout = QVBoxLayout(self)

        # Create a QTextEdit widget for text editing
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # Set the geometry of the widgets
        self.setGeometry(0, 0, 400, 300)
        self.text_edit.setGeometry(QRect(0, 0, 300, 200))
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)