from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
)

class LanguageSelectorDialog(QDialog):
    def __init__(self, available_languages: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Language Column")

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Select a language to add:"))

        self.dropdown = QComboBox()
        for code, name in available_languages.items():
            self.dropdown.addItem(f"{name} ({code})", code)
        layout.addWidget(self.dropdown)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }

            QDialog {
                background-color: #293E6b;
                border-radius: 6px;
            }

            QLineEdit {
                background-color: white;
                color: #293E6b;
                padding: 6px;
                border: 1px solid white;
                border-radius: 4px;
            }

            QPushButton {
                background-color: white;
                color: #293E6b;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }

            QPushButton:hover {
                background-color: #f0f0f0;
            }

            QComboBox {
                background-color: white;
                color: #293E6b;
                padding: 6px;
                border: 1px solid white;
                border-radius: 4px;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: #293E6b;
                selection-background-color: #f0f0f0;
            }
        """)

    def selected_code(self):
        return self.dropdown.currentData()