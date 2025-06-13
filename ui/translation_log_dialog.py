# ui/translation_log_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import Qt

class TranslationLogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Translation Progress")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.ok_btn = QPushButton("Close")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)
        layout.addWidget(self.ok_btn)

    def append_log(self, message):
        self.text_area.append(message)

    def mark_finished(self):
        self.ok_btn.setEnabled(True)
        self.append_log("\n✅ Translation complete.")
