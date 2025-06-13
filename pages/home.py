from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QCheckBox, QHBoxLayout, QHeaderView, QMenu, QFileDialog,
    QPushButton, QSizePolicy, QGridLayout, QDialog, QMessageBox, QLabel as QLabelWidget
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
import os
import shutil
from workers.tr_worker import TranslationWorker
from ui.translate_details import TranslateDetailsDialog
from functions.file_utils import ensure_translated_folder
from functions.glossary_utils import parse_glossary_to_map
from ui.translation_log_dialog import TranslationLogDialog
from datetime import datetime
from functools import partial


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        outer_layout = QVBoxLayout(self)

        # Inner layout aligned to top
        inner_container = QWidget()
        inner_layout = QVBoxLayout(inner_container)
        inner_layout.setAlignment(Qt.AlignTop)

        # File queue label
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("assets/icons/IconoirMultiplePages.svg").pixmap(20, 20))
        icon_label.setAlignment(Qt.AlignVCenter)

        text_label = QLabel("File Queue")
        text_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")

        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(icon_label)
        left_layout.addWidget(text_label)

        # ➡️ Right: Add + Remove Buttons
        file_drop_btn = QPushButton("  Add DWG Files")
        file_drop_btn.setIcon(QIcon("assets/icons/IconoirAddCircledOutline.svg"))
        file_drop_btn.setIconSize(QSize(20, 20))
        file_drop_btn.clicked.connect(self.open_file_dialog)

        self.remove_all_btn = QPushButton("  Remove All")
        self.remove_all_btn.setIcon(QIcon("assets/icons/IconoirTrash.svg"))
        self.remove_all_btn.setIconSize(QSize(20, 20))
        self.remove_all_btn.clicked.connect(self.remove_all_files)
        self.remove_all_btn.setVisible(False)

        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignRight)
        right_layout.addWidget(file_drop_btn)
        right_layout.addWidget(self.remove_all_btn)

        # Combine left + right in one row
        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.addWidget(left_container)
        top_row_layout.addStretch()  # 💡 This creates spacing between left and right
        top_row_layout.addWidget(right_container)

        # Add to your main inner_layout
        inner_layout.addWidget(top_row)

        # Table setup
        self.table = QTableWidget(0, 3)
        self.table.setMaximumHeight(300)
        
        # Column 0 (checkbox): no label, right aligned
        header_checkbox = QTableWidgetItem("")
        header_checkbox.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setHorizontalHeaderItem(0, header_checkbox)

        # Column 1: Filename (right aligned)
        header_filename = QTableWidgetItem("Filename")
        header_filename.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setHorizontalHeaderItem(1, header_filename)

        # Column 2: Actions (right aligned)
        header_actions = QTableWidgetItem("Actions")
        header_actions.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setHorizontalHeaderItem(2, header_actions)

        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(2, 60)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.table.cellClicked.connect(self.handle_table_click)
        self.table.itemSelectionChanged.connect(self.update_remove_all_visibility)
        inner_layout.addWidget(self.table)

        # Bottom action buttons row
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 10, 0, 0)
        actions_layout.setSpacing(15)
        actions_layout.setAlignment(Qt.AlignLeft)

        translate_all_btn = QPushButton("  Translate All")
        translate_all_btn.setIcon(QIcon("assets/icons/IconoirTranslate.svg"))
        translate_all_btn.setIconSize(QSize(20, 20))
        translate_all_btn.clicked.connect(self.start_translation)

        check_all_btn = QPushButton("  Check All")
        check_all_btn.setIcon(QIcon("assets/icons/IconoirPageSearch.svg"))
        check_all_btn.setIconSize(QSize(20, 20))
        check_all_btn.clicked.connect(self.check_all)

        convert_all_btn = QPushButton("  Convert All")
        convert_all_btn.setIcon(QIcon("assets/icons/IconoirRepeat.svg"))
        convert_all_btn.setIconSize(QSize(20, 20))
        convert_all_btn.clicked.connect(self.convert_all)

        actions_layout.addWidget(translate_all_btn)
        actions_layout.addWidget(check_all_btn)
        actions_layout.addWidget(convert_all_btn)

        inner_layout.addWidget(actions_container)

        # Recent activity section (3 columns)
        recent_container = QWidget()
        recent_layout = QGridLayout(recent_container)
        recent_layout.setContentsMargins(0, 20, 0, 0)
        recent_layout.setSpacing(15)

        def create_log_table(title):
            wrapper = QWidget()
            layout = QVBoxLayout(wrapper)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)

            label = QLabel(title)
            label.setStyleSheet("font-weight: bold; font-size: 14px; color: white;")
            layout.addWidget(label)

            table = QTableWidget(0, 3)
            table.setHorizontalHeaderLabels(["Filename", "Timestamp", "Actions"])


            # Align both headers to left
            filename_header = QTableWidgetItem("Filename")
            filename_header.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setHorizontalHeaderItem(0, filename_header)

            timestamp_header = QTableWidgetItem("Timestamp")
            timestamp_header.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setHorizontalHeaderItem(1, timestamp_header)

            actions_header = QTableWidgetItem("Actions")
            actions_header.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            table.setHorizontalHeaderItem(2, actions_header)
            table.setColumnWidth(2, 60)

            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setMaximumHeight(120)
            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout.addWidget(table)

            return wrapper, table


        translated_widget, self.translated_table = create_log_table("Recently Translated")
        checked_widget, self.checked_table = create_log_table("Recently Checked")
        converted_widget, self.converted_table = create_log_table("Recently Converted")

        recent_layout.addWidget(translated_widget, 0, 0)
        recent_layout.addWidget(checked_widget, 0, 1)
        recent_layout.addWidget(converted_widget, 0, 2)

        inner_layout.addWidget(recent_container)

        # Add inner layout to main layout
        outer_layout.addWidget(inner_container)

        self.load_existing_files()
        self.load_recently_translated_files()


    def add_files_to_queue(self, files):
        for file in files:
            self.add_file_to_queue(file)

    def add_file_to_queue(self, filepath):
        queue_dir = os.path.abspath("queue")
        os.makedirs(queue_dir, exist_ok=True)

        filename = os.path.basename(filepath)
        queue_path = os.path.join(queue_dir, filename)

        # Copy file only if not already in queue
        if not os.path.exists(queue_path):
            try:
                shutil.copy2(filepath, queue_path)
            except Exception as e:
                print(f"❌ Failed to copy {filepath}: {e}")
                return

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column 0: Checkbox
        checkbox = QCheckBox()
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 0, checkbox_widget)
        checkbox.stateChanged.connect(self.update_remove_all_visibility)

        # Column 1: Filename (shown) + full path (stored as data)
        filename_item = QTableWidgetItem(filename)
        filename_item.setData(Qt.UserRole, queue_path)  # <-- Save full path here
        self.table.setItem(row, 1, filename_item)

        # Column 2: Menu Icon
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("assets/icons/IconoirMenu.svg").pixmap(20, 20))
        icon_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setCellWidget(row, 2, icon_label)


    def load_existing_files(self):
        queue_dir = "queue"
        if not os.path.exists(queue_dir):
            os.makedirs(queue_dir)

        for filename in os.listdir(queue_dir):
            file_path = os.path.join(queue_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(".dwg"):
                self.add_file_to_queue(file_path)

    def remove_all_files(self):
        queue_dir = "queue"
        for row in reversed(range(self.table.rowCount())):
            filepath_item = self.table.item(row, 1)
            if filepath_item:
                try:
                    os.remove(os.path.join(queue_dir, filepath_item.text()))
                except Exception as e:
                    print(f"⚠️ Could not delete file: {e}")
            self.table.removeRow(row)

    def update_remove_all_visibility(self):
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    self.remove_all_btn.setVisible(True)
                    return
        self.remove_all_btn.setVisible(False)

    def open_file_dialog(self):
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select DWG Files",
            "",
            "DWG Files (*.dwg);;All Files (*)"
        )
        if filepaths:
            self.add_files_to_queue(filepaths)


    def handle_table_click(self, row, column):
        if column == 2:
            self.table.setCurrentCell(row, column)
            self.show_file_menu(row)

    def show_file_menu(self, row):
        menu = QMenu()
        menu.addAction("Translate", lambda: self.handle_action("translate", self.get_filepath_from_row(row)))
        menu.addAction("Check Linguistic Integrity", lambda: self.handle_action("check_linguistic_integrity", self.get_filepath_from_row(row)))
        menu.addAction("Convert File", lambda: self.handle_action("convert", self.get_filepath_from_row(row)))
        menu.addSeparator()
        menu.addAction("Remove from Queue", lambda: self.delete_file_and_row(row))

        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #293E6b;
                border: 1px solid #293E6b;
                padding: 5px;
                border-radius: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #293E6b;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #293E6b;
                margin: 5px 10px;
            }
        """)

        cell_widget = self.table.cellWidget(row, 2)
        if cell_widget:
            menu.exec_(cell_widget.mapToGlobal(cell_widget.rect().bottomLeft()))

    def get_filepath_from_row(self, row):
        item = self.table.item(row, 1)
        return item.text() if item else None

    def delete_file_and_row(self, row):
        filepath_item = self.table.item(row, 1)
        if filepath_item:
            try:
                os.remove(os.path.join("queue", filepath_item.text()))
            except Exception as e:
                print(f"⚠️ Could not delete file: {e}")
        self.table.removeRow(row)

    def handle_action(self, action_type, file_path):
        if action_type == "translate":
            self.selected_files = [os.path.join("queue", file_path)]
            self.start_translation()
        # other actions...


    def translate_all(self):
        for row in range(self.table.rowCount()):
            path = self.get_filepath_from_row(row)
            if path:
                self.handle_action("translate", path)

    def check_all(self):
        for row in range(self.table.rowCount()):
            path = self.get_filepath_from_row(row)
            if path:
                self.handle_action("check_linguistic_integrity", path)

    def convert_all(self):
        for row in range(self.table.rowCount()):
            path = self.get_filepath_from_row(row)
            if path:
                self.handle_action("convert", path)

    def get_selected_files(self):
        selected = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    filename_item = self.table.item(row, 1)
                    if filename_item:
                        filepath = os.path.join("queue", filename_item.text())
                        selected.append(filepath)
        return selected
        
    def load_recently_translated_files(self):
        self.translated_table.setRowCount(0)  # Clear existing rows

        translated_dir = ensure_translated_folder()
        for lang_folder in sorted(os.listdir(translated_dir)):
            lang_path = os.path.join(translated_dir, lang_folder)
            if os.path.isdir(lang_path):
                for file in sorted(os.listdir(lang_path), reverse=True):
                    if file.lower().endswith(".dwg"):
                        full_path = os.path.join(lang_path, file)

                        row = self.translated_table.rowCount()
                        self.translated_table.insertRow(row)

                        # Column 0: Filename
                        file_item = QTableWidgetItem(file)
                        file_item.setData(Qt.UserRole, full_path)
                        self.translated_table.setItem(row, 0, file_item)

                        # Column 1: Timestamp (use last modified time)
                        timestamp = os.path.getmtime(full_path)
                        from datetime import datetime
                        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
                        timestamp_item = QTableWidgetItem(formatted_time)
                        self.translated_table.setItem(row, 1, timestamp_item)

                        # Column 2: Menu Icon
                        icon_label = QLabel()
                        icon_label.setPixmap(QIcon("assets/icons/IconoirMenu.svg").pixmap(20, 20))
                        icon_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.translated_table.setCellWidget(row, 2, icon_label)

                        # Connect menu click
                        icon_label.mousePressEvent = lambda event, row=row, path=full_path: self.show_translated_file_menu(event, row, path)


    def on_translation_finished(self, path, lang):
        self.load_recently_translated_files()

    def start_translation(self):
        self.selected_files = self.get_selected_files()

        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select DWG files to translate.")
            return

        dialog = TranslateDetailsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        details = dialog.get_details()
        print(details)

        self.source_lang = details["source_lang"]
        self.target_lang = details["target_lang"]
        self.output_dir = details["output_folder"]
        glossary_path = details.get("glossary_path")

        try:
            if glossary_path:
                self.glossary_map = parse_glossary_to_map(
                    glossary_path,
                    self.source_lang,
                    self.target_lang
                )
            else:
                self.glossary_map = {}
        except Exception as e:
            QMessageBox.warning(self, "Glossary Error", str(e))
            self.glossary_map = {}

        self.active_workers = []

        # ✅ Create and show log dialog
        self.log_dialog = TranslationLogDialog(self)
        self.log_dialog.show()

        def log_output(msg):
            print(msg)
            self.log_dialog.append_log(msg)

        for file_path in self.selected_files:
            abs_path = os.path.abspath(file_path)

            worker = TranslationWorker(
                abs_path,
                self.source_lang,
                self.target_lang,
                self.glossary_map,
                self.output_dir
            )

            worker.log_signal.connect(log_output)
            worker.finished.connect(lambda path: self.log_dialog.mark_finished())
            worker.finished.connect(partial(self.on_translation_finished, lang=self.target_lang))
            worker.finished.connect(lambda path: print(f"✅ Done: {path}"))
            worker.failed.connect(lambda path, err: print(f"❌ Failed: {path} - {err}"))

            self.active_workers.append(worker)
            worker.start()

    def show_translated_file_menu(self, event, row, file_path):
        menu = QMenu()
        menu.addAction("Open File", lambda: os.startfile(file_path))
        menu.addAction("Check Linguistic Integrity", lambda: self.check_linguistic_integrity(file_path))
        menu.addAction("Show in Folder", lambda: os.startfile(os.path.dirname(file_path)))
        menu.addSeparator()
        menu.addAction("Delete", lambda: self.delete_translated_file(row, file_path))

        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                color: #293E6b;
                border: 1px solid #293E6b;
                padding: 5px;
                border-radius: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                background-color: transparent;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #293E6b;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #293E6b;
                margin: 5px 10px;
            }
        """)

        menu.exec_(event.globalPosition().toPoint())

    def delete_translated_file(self, row, file_path):
        try:
            os.remove(file_path)
            self.translated_table.removeRow(row)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete file:\n{e}")