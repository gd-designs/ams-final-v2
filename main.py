from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QStackedWidget,
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QIcon
import os
import sys

from pages.home import HomePage
from pages.glossary import GlossaryManagerPage

from functions.paths import resource_path

class MainWindow(QMainWindow):
    files_dropped = Signal(list)  # ✅ signal to send dropped files

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AMS Applicazione v2")
        self.setWindowIcon(QIcon(resource_path("assets/logo/ams-logo-sfondo-blu-32.ico")))
        self.setMinimumSize(1000, 700)
        self.setAcceptDrops(True)

        self.stack = QStackedWidget()
        self.pages = {}
        self.page_actions = {}

        # Add Home Page
        self.home_widget = HomePage(self)
        self.pages["Home"] = self.home_widget
        self.stack.addWidget(self.home_widget)

        # Add Glossary Page
        self.glossary_widget = GlossaryManagerPage()
        self.pages["Glossari"] = self.glossary_widget
        self.stack.addWidget(self.glossary_widget)

        for name in ["Log", "Impostazioni"]:
            self.add_blank_page(name)

        self.setCentralWidget(self.stack)

        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        for name in self.pages:
            action = QAction(name, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, n=name: self.switch_page(n))
            toolbar.addAction(action)
            self.page_actions[name] = action

        self.setStatusBar(QStatusBar(self))
        self.switch_page("Home")

        # Overlay for drag feedback
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("background-color: rgba(255, 255, 255, 0.25); border: 2px dashed white;")
        self.overlay.setVisible(False)
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.overlay.resize(self.size())

        # ✅ Centered label inside overlay
        self.overlay_label = QLabel("📂 Trascina i file qui per aggiungerli alla coda", self.overlay)
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.overlay_label.setStyleSheet("color: #293E6b; font-size: 18px; font-weight: bold;")
        self.overlay_label.setGeometry(0, 0, self.overlay.width(), self.overlay.height())

        self.files_dropped.connect(self.home_widget.add_files_to_queue)  # ✅ connect signal to HomePage

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.size())  # keep overlay full-screen

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.overlay.setVisible(True)

    def dragLeaveEvent(self, event):
        self.overlay.setVisible(False)

    def dropEvent(self, event: QDropEvent):
        self.overlay.setVisible(False)
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls if os.path.isfile(url.toLocalFile())]
        if files:
            self.files_dropped.emit(files)


    def add_blank_page(self, name):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{name} Pagina - in costruzione"))
        widget.setLayout(layout)
        self.pages[name] = widget
        self.stack.addWidget(widget)

    def switch_page(self, name):
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])
            # ✅ Update active state
            for page, action in self.page_actions.items():
                action.setChecked(page == name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet("""
        QMainWindow {
            background-color: #293E6b;
        }

        QToolBar {
            background-color: rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 0;
            padding: 5px;
            spacing: 10px;
            border-bottom: 1px solid white;
        }

        QToolBar QToolButton {
            color: white;
            background: transparent;
            padding: 6px 12px;
            border-radius: 2px;
        }
                      
        QToolBar QToolButton:hover {
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
        }

        QToolBar QToolButton:checked {
            background-color: white;
            color: #293E6b;
        }

        QStatusBar {
            background-color: #293E6b;
            color: white;
        }

        QLabel {
            color: white;
        }
                      
        QTableWidget {
            background-color: white;
            border-radius: 4px;
            border: 1px solid white;
            color: #293E6b;
            gridline-color: white;
        }
                      
        QPushButton {
            padding: 8px 16px;
            background-color: white;
            font-weight: bold;
            color: #293E6b;
        }
                      
        QPushButton:hover {
            background-color: #f0f0f0;
        }
                      
        QCheckBox {
            spacing: 8px;
            color: white;
            font-size: 14px;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }

        QCheckBox::indicator:unchecked {
            border: 1px solid #293E6b;
            background-color: transparent;
        }

        QCheckBox::indicator:checked {
            background-color: #293E6b;
            border: 1px solid #293E6b;
            image: url(assets/icons/IconoirCheck.svg);  /* prevent default check image */
        }  

        QMessageBox {
            background-color: #293E6b;
            color: white;
        }                    
    """)
    window.show()
    sys.exit(app.exec())