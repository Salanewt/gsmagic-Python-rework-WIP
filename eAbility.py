from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout

class Ability_Editor(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        self.label = QLabel("Target:", self)
        self.combo_box = QComboBox(self)
        self.combo_box.setFixedWidth(150)  # Set the fixed width of the combo box

        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)

        # Connect the combo box signal to the update_value_slot method
        self.combo_box.currentIndexChanged.connect(self.update_value_slot)

    def load_target(self, value):
        self.combo_box.addItem("N/A", 0)
        self.combo_box.addItem("Enemy", 1)
        self.combo_box.addItem("Ally", 2)
        self.combo_box.addItem("Field", 3)
        self.combo_box.addItem("User", 4)
        self.combo_box.addItem("Not User Ally", 5)

    def add_option(self, display_name, value):
        # Check if the maximum limit has been reached
        if self.current_options < self.max_options:
            self.combo_box.addItem(display_name, value)
            self.current_options += 1

    def update_value(self, value):
        # Find the item index based on the underlying value and set it as the current selection
        index = self.combo_box.findData(value)
        if index != -1:
            self.combo_box.setCurrentIndex(index)

    def update_value_slot(self):
        # Get the currently selected value from the combo box and update the value at address 0x080B7C14
        new_value = self.combo_box.currentData()
        print(f"Updating value to: {new_value}")