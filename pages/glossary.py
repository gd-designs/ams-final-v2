from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QHBoxLayout, QAbstractItemView,
    QFileDialog, QCheckBox, QMessageBox, QDialog, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
import csv
import os
import shutil
from datetime import datetime
from ui.language_selector import LanguageSelectorDialog


class GlossaryManagerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_languages = []
        self.language_options = ["PT", "NL", "PL", "SV", "NO", "DA", "FI", "ZH"]
        self.selected_checkboxes = []

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        # === Current Glossary Group ===
        self.current_group = QGroupBox("📘 Current Glossary")
        current_layout = QHBoxLayout()

        self.current_glossary_label = QLabel("Glossario_Tecnico.csv")
        self.view_current_btn = QPushButton("🔍 View Glossary")
        self.view_current_btn.clicked.connect(self.show_glossary_table)

        current_layout.addWidget(self.current_glossary_label)
        current_layout.addStretch()
        current_layout.addWidget(self.view_current_btn)

        self.current_group.setLayout(current_layout)
        layout.addWidget(self.current_group)

        # === Previous Versions Section ===
        self.prev_label = QLabel("📁 Previous Glossary Versions")
        layout.addWidget(self.prev_label)

        # Table setup
        self.previous_table = QTableWidget(0, 4)
        self.previous_table.setMaximumHeight(300)

        # Column 0 (checkbox): no label, right aligned
        header_checkbox = QTableWidgetItem("")
        header_checkbox.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.previous_table.setHorizontalHeaderItem(0, header_checkbox)

        # Column 1: Filename (right aligned)
        header_filename = QTableWidgetItem("Filename")
        header_filename.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.previous_table.setHorizontalHeaderItem(1, header_filename)

        # Column 2: Actions (right aligned)
        header_timestamp = QTableWidgetItem("Timestamp")
        header_timestamp.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.previous_table.setHorizontalHeaderItem(2, header_timestamp)

        # Column 3: Actions (right aligned)
        header_actions = QTableWidgetItem("Actions")
        header_actions.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.previous_table.setHorizontalHeaderItem(3, header_actions)

        self.previous_table.setColumnWidth(0, 40)  # Checkbox
        self.previous_table.setColumnWidth(2, 120)  # Timestamp
        self.previous_table.setColumnWidth(3, 160)  # Actions
        self.previous_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.previous_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.previous_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.previous_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.previous_table)

        # === Back + Table + Toolbar ===
        self.back_button = QPushButton("🔙 Back to Glossary Manager")
        self.back_button.clicked.connect(self.hide_glossary_table)
        self.back_button.hide()
        layout.addWidget(self.back_button)

        self.toolbar = QHBoxLayout()

        self.add_row_btn = QPushButton("➕ Add Row")
        self.add_row_btn.clicked.connect(self.add_row)

        self.delete_selected_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_btn.clicked.connect(self.delete_selected_rows)
        self.delete_selected_btn.hide()

        self.add_column_btn = QPushButton("➕ Add Column")
        self.add_column_btn.clicked.connect(self.prompt_add_column)

        self.import_btn = QPushButton("📥 Import CSV")
        self.import_btn.clicked.connect(self.import_csv)

        self.export_btn = QPushButton("📤 Export CSV")
        self.export_btn.clicked.connect(self.export_csv)

        self.save_btn = QPushButton("💾 Save Glossary")
        self.save_btn.clicked.connect(self.save_glossary)

        for w in [
            self.add_row_btn, self.add_column_btn,
            self.delete_selected_btn, self.import_btn, self.export_btn, self.save_btn
        ]:
            self.toolbar.addWidget(w)

        toolbar_wrapper = QWidget()
        toolbar_wrapper.setLayout(self.toolbar)
        toolbar_wrapper.hide()
        self.toolbar_widget = toolbar_wrapper
        layout.addWidget(toolbar_wrapper)

        self.glossary_table = QTableWidget()
        self.glossary_table.hide()
        layout.addWidget(self.glossary_table)

        self.load_current_glossary()
        self.load_previous_versions()

        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid white;
                border-radius: 8px;
                margin-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px;
                background-color: white;
                border-radius: 4px;
                color: #293E6b;
            }
        """)


    def load_current_glossary(self):
        glossary_path = os.path.join("glossaries", "glossary_current_converted.csv")
        if os.path.exists(glossary_path):
            try:
                with open(glossary_path, newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    headers = reader.fieldnames or []
                    self.current_languages = headers
                    self.selected_checkboxes.clear()
                    self.glossary_table.setColumnCount(len(headers) + 1)
                    self.glossary_table.setHorizontalHeaderLabels(["✔"] + headers)
                    self.glossary_table.setRowCount(0)

                    for row in reader:
                        row_data = [row.get(h, "") for h in headers]
                        self.add_row_to_table(row_data)

                    self.current_glossary_label.setText(f"Current Glossary (Languages: {', '.join(headers)})")
            except Exception as e:
                QMessageBox.warning(self, "Glossary Load Error", str(e))

    def load_previous_versions(self):
        self.previous_table.setRowCount(0)
        versions_dir = os.path.join("glossaries", "versions")
        os.makedirs(versions_dir, exist_ok=True)

        for filename in sorted(os.listdir(versions_dir), reverse=True):
            if filename.lower().endswith(".csv"):
                file_path = os.path.join(versions_dir, filename)
                row = self.previous_table.rowCount()
                self.previous_table.insertRow(row)

                # Filename
                file_item = QTableWidgetItem(filename)
                file_item.setData(Qt.UserRole, file_path)
                self.previous_table.setItem(row, 0, file_item)

                # Timestamp
                timestamp = os.path.getmtime(file_path)
                formatted = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                self.previous_table.setItem(row, 1, QTableWidgetItem(formatted))

                # Actions
                action_widget = QWidget()
                layout = QHBoxLayout(action_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                view_btn = QPushButton("View")
                reinstate_btn = QPushButton("Reinstate")
                view_btn.clicked.connect(lambda _, f=file_path: self.load_from_csv(f))
                reinstate_btn.clicked.connect(lambda _, f=file_path: self.reinstate_glossary(f))
                layout.addWidget(view_btn)
                layout.addWidget(reinstate_btn)
                self.previous_table.setCellWidget(row, 2, action_widget)

    def reinstate_glossary(self, file_path):
        glossary_dir = "glossaries"
        current_path = os.path.join(glossary_dir, "Glossario_Tecnico.csv")
        shutil.copy2(file_path, current_path)
        self.load_current_glossary()
        QMessageBox.information(self, "Reinstated", f"{os.path.basename(file_path)} reinstated as current glossary.")


    def create_previous_version_widget(self, filename):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(QLabel(filename))
        layout.addStretch()
        view_btn = QPushButton("View")
        reinstate_btn = QPushButton("Reinstate")
        layout.addWidget(view_btn)
        layout.addWidget(reinstate_btn)
        widget.setLayout(layout)
        return widget

    def show_glossary_table(self):
        self.current_group.hide()
        self.prev_label.hide()
        self.previous_table.hide()
        self.back_button.show()
        self.toolbar_widget.show()
        self.glossary_table.show()

    def hide_glossary_table(self):
        self.back_button.hide()
        self.toolbar_widget.hide()
        self.glossary_table.hide()
        self.current_group.show()
        self.prev_label.show()
        self.previous_table.show()

    def add_row_to_table(self, row_data=None):
        row = self.glossary_table.rowCount()
        self.glossary_table.insertRow(row)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.toggle_delete_button_visibility)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.glossary_table.setCellWidget(row, 0, container)

        self.selected_checkboxes.append(checkbox)

        for col, text in enumerate(row_data or [""] * len(self.current_languages)):
            item = QTableWidgetItem(text)
            self.glossary_table.setItem(row, col + 1, item)

        self.glossary_table.scrollToItem(self.glossary_table.item(row, 1), QAbstractItemView.PositionAtCenter)


    def add_row(self):
        self.add_row_to_table()

    def delete_selected_rows(self):
        for i in reversed(range(self.glossary_table.rowCount())):
            container = self.glossary_table.cellWidget(i, 0)
            if container:
                checkbox = container.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    self.glossary_table.removeRow(i)
                    self.selected_checkboxes.pop(i)
        self.toggle_delete_button_visibility()


    def toggle_delete_button_visibility(self):
        any_selected = any(cb.isChecked() for cb in self.selected_checkboxes)
        self.delete_selected_btn.setVisible(any_selected)

    def toggle_all_rows(self, state):
        check = state == Qt.Checked
        for cb in self.selected_checkboxes:
            cb.blockSignals(True)
            cb.setChecked(check)
            cb.blockSignals(False)
        self.toggle_delete_button_visibility()

    def prompt_add_column(self):
        remaining = {
            "EN": "English", "FR": "French", "ES": "Spanish", "PT": "Portuguese", "NL": "Dutch",
            "PL": "Polish", "SV": "Swedish", "NO": "Norwegian", "DA": "Danish",
            "FI": "Finnish", "ZH": "Chinese", "CS": "Czech"
        }
        available = {code: name for code, name in remaining.items() if code not in self.current_languages}
        if not available:
            QMessageBox.information(self, "No Languages Left", "All language columns are already added.")
            return

        dialog = LanguageSelectorDialog(available, self)
        if dialog.exec() == QDialog.Accepted:
            selected_code = dialog.selected_code()
            self.current_languages.append(selected_code)
            self.refresh_table_headers()

    def refresh_table_headers(self):
        col_count = len(self.current_languages) + 1
        self.glossary_table.setColumnCount(col_count)
        self.glossary_table.setHorizontalHeaderLabels(["✔"] + self.current_languages)

    def save_glossary(self):
        glossary_dir = "glossaries"
        os.makedirs(glossary_dir, exist_ok=True)

        current_path = os.path.join(glossary_dir, "Glossario_Tecnico.csv")
        versions_dir = os.path.join(glossary_dir, "versions")
        os.makedirs(versions_dir, exist_ok=True)

        if os.path.exists(current_path):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_path = os.path.join(versions_dir, f"Glossario_Tecnico_{timestamp}.csv")
            shutil.copy2(current_path, backup_path)

        with open(current_path, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(self.current_languages)
            for row in range(self.glossary_table.rowCount()):
                row_data = []
                for col in range(1, self.glossary_table.columnCount()):
                    item = self.glossary_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        QMessageBox.information(self, "Saved", f"Glossary saved to {current_path}")
        self.load_previous_versions()

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import CSV", "", "CSV files (*.csv)")
        if not file_path:
            return
        self.load_from_csv(file_path)

    def export_csv(self):
        os.makedirs("glossaries", exist_ok=True)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "glossaries/Glossario_Export.csv",
            "CSV files (*.csv)"
        )
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"

        with open(path, "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(self.current_languages)
            for row in range(self.glossary_table.rowCount()):
                row_data = []
                for col in range(1, self.glossary_table.columnCount()):
                    item = self.glossary_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        QMessageBox.information(self, "Exported", f"Exported to {os.path.basename(path)}")

    def load_from_csv(self, file_path):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            headers = reader.fieldnames
            if not headers:
                QMessageBox.warning(self, "Error", "No headers found.")
                return

            self.current_languages = headers
            self.selected_checkboxes.clear()
            self.glossary_table.setColumnCount(len(headers) + 1)
            self.glossary_table.setHorizontalHeaderLabels(["✔"] + headers)
            self.glossary_table.setRowCount(0)

            for row in reader:
                row_data = [row.get(h, "") for h in headers]
                self.add_row_to_table(row_data)

        self.load_previous_versions()