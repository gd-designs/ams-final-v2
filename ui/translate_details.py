from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit
)
from PySide6.QtCore import Qt
from pathlib import Path

class TranslateDetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dettagli Traduzione")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Source Language
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Lingua di Origine:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems([
            "IT", "DE", "FR", "EN", "ES", "NL", "PL", "PT", "RU", "JA", "ZH"
        ])
        source_layout.addWidget(self.source_combo)
        layout.addLayout(source_layout)

        # Target Language
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Lingua di Destinazione:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "DE", "EN", "FR", "IT", "ES", "NL", "PL", "PT", "RU", "JA", "ZH"
        ])
        target_layout.addWidget(self.target_combo)
        layout.addLayout(target_layout)

        # Output Directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Cartella di Output:"))
        self.output_input = QLineEdit()
        output_btn = QPushButton("Sfoglia")
        output_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)

        desktop = str(Path.home() / "Desktop")
        self.output_input.setText(desktop)

        # OK / Cancel
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("Avvia")
        cancel_btn = QPushButton("Cancella")
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


    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleziona Cartella di Output")
        if folder_path:
            self.output_input.setText(folder_path)

    def get_details(self):
        from functions.paths import get_glossary_dir
        glossary_dir = get_glossary_dir()
        glossary_path = glossary_dir / "glossario_tecnico.csv"
        
        return {
            "source_lang": self.source_combo.currentText(),
            "target_lang": self.target_combo.currentText(),
            "glossary_path": glossary_path,  # Auto-attached
            "output_folder": self.output_input.text()
        }
