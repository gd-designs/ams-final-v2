from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit
)
from PySide6.QtCore import Qt

class TranslateDetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translation Details")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Source Language
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source Language:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems([
            "IT", "DE", "FR", "EN", "ES", "NL", "PL", "PT", "RU", "JA", "ZH"
        ])
        source_layout.addWidget(self.source_combo)
        layout.addLayout(source_layout)

        # Target Language
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Language:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "DE", "EN", "FR", "IT", "ES", "NL", "PL", "PT", "RU", "JA", "ZH"
        ])
        target_layout.addWidget(self.target_combo)
        layout.addLayout(target_layout)

        # Glossary File
        glossary_layout = QHBoxLayout()
        glossary_layout.addWidget(QLabel("Glossary CSV:"))
        self.glossary_input = QLineEdit()
        glossary_btn = QPushButton("Browse")
        glossary_btn.clicked.connect(self.select_glossary_file)
        glossary_layout.addWidget(self.glossary_input)
        glossary_layout.addWidget(glossary_btn)
        layout.addLayout(glossary_layout)

        # Output Directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Folder:"))
        self.output_input = QLineEdit()
        output_btn = QPushButton("Browse")
        output_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)

        # OK / Cancel
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

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


    def select_glossary_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Glossary CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.glossary_input.setText(file_path)

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_input.setText(folder_path)

    def get_details(self):
        return {
            "source_lang": self.source_combo.currentText(),
            "target_lang": self.target_combo.currentText(),
            "glossary_path": self.glossary_input.text(),
            "output_folder": self.output_input.text()
        }
