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
from functions.paths import resource_path, get_glossary_dir, queue_dir, translated_dir
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def default_glossary_path() -> Path | None:
    gpath = get_glossary_dir() / "glossario_tecnico.csv"
    return gpath if gpath.exists() else None

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
        icon_label.setPixmap(QIcon(resource_path("assets/icons/IconoirMultiplePages.svg")).pixmap(20, 20))
        icon_label.setAlignment(Qt.AlignVCenter)

        text_label = QLabel("Coda file")
        text_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")

        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)
        left_layout.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(icon_label)
        left_layout.addWidget(text_label)

        # ➡️ Right: Add + Remove Buttons
        file_drop_btn = QPushButton("  Aggiungi file DWG")
        file_drop_btn.setIcon(QIcon(resource_path("assets/icons/IconoirAddCircledOutline.svg")))
        file_drop_btn.setIconSize(QSize(20, 20))
        file_drop_btn.clicked.connect(self.open_file_dialog)

        self.remove_all_btn = QPushButton("  Rimuovi tutto")
        self.remove_all_btn.setIcon(QIcon(resource_path("assets/icons/IconoirTrash.svg")))
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
        header_filename = QTableWidgetItem("Nome file")
        header_filename.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table.setHorizontalHeaderItem(1, header_filename)

        # Column 2: Actions (right aligned)
        header_actions = QTableWidgetItem("Azioni")
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

        translate_all_btn = QPushButton("  Traduci tutto")
        translate_all_btn.setIcon(QIcon(resource_path("assets/icons/IconoirTranslate.svg")))
        translate_all_btn.setIconSize(QSize(20, 20))
        translate_all_btn.clicked.connect(self.start_translation)

        check_all_btn = QPushButton("  Controlla tutto")
        check_all_btn.setIcon(QIcon(resource_path("assets/icons/IconoirPageSearch.svg")))
        check_all_btn.setIconSize(QSize(20, 20))
        check_all_btn.clicked.connect(self.check_all)

        convert_all_btn = QPushButton("  Converti tutto")
        convert_all_btn.setIcon(QIcon(resource_path("assets/icons/IconoirRepeat.svg")))
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
            table.setHorizontalHeaderLabels(["Nome file", "Timestamp", "Azioni"])


            # Align both headers to left
            filename_header = QTableWidgetItem("Nome file")
            filename_header.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setHorizontalHeaderItem(0, filename_header)

            timestamp_header = QTableWidgetItem("Timestamp")
            timestamp_header.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setHorizontalHeaderItem(1, timestamp_header)

            actions_header = QTableWidgetItem("Azioni")
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


        translated_widget, self.translated_table = create_log_table("Recentemente Tradotto")
        checked_widget, self.checked_table = create_log_table("Recentemente Controllato")
        converted_widget, self.converted_table = create_log_table("Recentemente Convertito")

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

    def add_file_to_queue(self, filepath: str):
        qdir = queue_dir()                             # ➋
        filename   = os.path.basename(filepath)
        queue_path = qdir / filename                   # pathlib.Path

        if not queue_path.exists():                    # copy only once
            try:
                shutil.copy2(filepath, queue_path)
            except OSError as err:
                logger.error(f"copy failed: {err}")
                return

        row = self.table.rowCount()
        self.table.insertRow(row)

        # store the ABSOLUTE path in the table (so we never rebuild it later)
        fn_item = QTableWidgetItem(filename)
        fn_item.setData(Qt.UserRole, str(queue_path))  # ➌
        self.table.setItem(row, 1, fn_item)

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
        icon_label.setPixmap(QIcon(resource_path("assets/icons/IconoirMenu.svg")).pixmap(20, 20))
        icon_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.table.setCellWidget(row, 2, icon_label)


    # LOAD existing queue
    def load_existing_files(self):
        for fp in queue_dir().glob("*.dwg"):
            self.add_file_to_queue(str(fp))


    # REMOVE ALL
    def remove_all_files(self):
        for row in reversed(range(self.table.rowCount())):
            path = Path(self.table.item(row, 1).data(Qt.UserRole))
            try:
                path.unlink()
            except OSError as err:
                logger.warning(f"delete failed: {err}")
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
        menu.addAction("Traduci", lambda: self.handle_action("translate", self.get_filepath_from_row(row)))
        menu.addAction("Controlla Integrità Linguistica", lambda: self.handle_action("check_linguistic_integrity", self.get_filepath_from_row(row)))
        menu.addAction("Converti File", lambda: self.handle_action("convert", self.get_filepath_from_row(row)))
        menu.addSeparator()
        menu.addAction("Rimuovi dalla Coda", lambda: self.delete_file_and_row(row))

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
        return item.data(Qt.UserRole) if item else None

    # ───────────────────────────── delete_file_and_row ─────────────────────────
    def delete_file_and_row(self, row: int):
        path = self.table.item(row, 1).data(Qt.UserRole)
        try:
            os.remove(path)
        except OSError as err:
            logger.warning(f"delete failed: {err}")
        self.table.removeRow(row)


    def handle_action(self, action_type, file_path):
        if action_type == "translate":
            self.selected_files = [file_path]
            self.start_translation()


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
    # ───────────────────────────── get_selected_files ──────────────────────────
    def get_selected_files(self) -> list[str]:
        selected: list[str] = []
        for row in range(self.table.rowCount()):
            box = self.table.cellWidget(row, 0).findChild(QCheckBox)
            if box.isChecked():
                selected.append(self.table.item(row, 1).data(Qt.UserRole))   # ➎
        return selected

            
    # ─────────────────────────────────────────────────────────────
    # 2. load_recently_translated_files
    # ─────────────────────────────────────────────────────────────
    def load_recently_translated_files(self) -> None:
        """
        Rebuilds the “Recentemente Tradotto” table from the Desktop folder.
        """

        self.translated_table.setRowCount(0)
        root = translated_dir()
        if not root.exists():
            return

        # newest first
        for dwg in sorted(root.glob("*.dwg"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True):
            row = self.translated_table.rowCount()
            self.translated_table.insertRow(row)

            # col 0 – nome file
            item = QTableWidgetItem(dwg.name)
            item.setData(Qt.UserRole, str(dwg))
            self.translated_table.setItem(row, 0, item)

            # col 1 – timestamp
            ts = datetime.fromtimestamp(dwg.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            self.translated_table.setItem(row, 1, QTableWidgetItem(ts))

            # col 2 – menu icona
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(resource_path("assets/icons/IconoirMenu.svg")).pixmap(20, 20))
            icon_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.translated_table.setCellWidget(row, 2, icon_label)

            # contextual menu
            icon_label.mousePressEvent = (
                lambda ev, r=row, p=str(dwg): self.show_translated_file_menu(ev, r, p)
            )



    def on_translation_finished(self, file_path: str) -> None:
        """
        • Assumes DWG is already saved in AMS-Applicazione-Tradotto
        • Refreshes the “Recentemente Tradotto” table
        """

        logger.info(f"✅ Traduzione completata: {file_path}")
        self.log_dialog.append_log(f"✅ Traduzione completata: {file_path}")

        self.load_recently_translated_files()  # ← that's all you need now



    def show_translated_file_menu(self, event, row, file_path):
        menu = QMenu()
        menu.addAction("Apri", lambda: os.startfile(file_path))
        menu.addAction("Controlla Integrità Linguistica", lambda: self.check_linguistic_integrity(file_path))
        menu.addAction("Mostra nella Cartella", lambda: os.startfile(os.path.dirname(file_path)))
        menu.addSeparator()
        menu.addAction("Elimina", lambda: self.delete_translated_file(row, file_path))

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
            QMessageBox.critical(self, "Errore", f"Impossibile eliminare il file:\n{e}")

    def start_translation(self):
        self.selected_files = self.get_selected_files()
        if not self.selected_files:
            QMessageBox.warning(self, "Nessun file", "Seleziona file DWG da tradurre.")
            return

        dialog = TranslateDetailsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return

        details = dialog.get_details()
        logger.info(f"Starting translation with details: {details}")

        # Load glossary
        glossary_map = {}
        if details["glossary_path"] and os.path.exists(details["glossary_path"]):
            try:
                glossary_map = parse_glossary_to_map(
                    details["glossary_path"],
                    details["source_lang"],
                    details["target_lang"]
                )
                logger.info(f"Loaded glossary with {len(glossary_map)} terms")
            except Exception as e:
                logger.error(f"Failed to load glossary: {e}")
                QMessageBox.warning(self, "Glossary Error", str(e))

        # Setup log window
        self.log_dialog = TranslationLogDialog(self)
        self.log_dialog.show()

        def log_message(msg):
            self.log_dialog.append_log(msg)
            logger.info(msg)

        # Start workers
        self.active_workers = []
        for file_path in self.selected_files:
            abs_path = Path(file_path).resolve()  # ← ensures absolute full path

            worker = TranslationWorker(
                abs_path,
                details["source_lang"],
                details["target_lang"],
                glossary_map,
                details["output_folder"],
            )

            worker.log_signal.connect(log_message)
            worker.finished.connect(self.on_translation_finished)
            worker.failed.connect(lambda p, e: log_message(f"❌ Failed: {p} - {e}"))

            self.active_workers.append(worker)
            worker.start()
            log_message(f"🚀 Started translation for: {abs_path.name}\n📁 Full path: {abs_path}")