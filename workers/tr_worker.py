from PySide6.QtCore import QThread, Signal
from functions.translation_pipeline import process_file

class TranslationWorker(QThread):
    log_signal = Signal(str)  # ✅ Emit log lines to the UI
    finished = Signal(str)
    failed = Signal(str, str)

    def __init__(self, file_path, source_lang, target_lang, glossary_map, output_folder):
        super().__init__()
        self.file_path = file_path
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.glossary_map = glossary_map
        self.output_folder = output_folder

    def run(self):
        try:
            def logger(msg):
                self.log_signal.emit(msg)  # ✅ Emit each log line

            process_file(
                dwg_path=self.file_path,
                source_lang=self.source_lang,
                target_lang=self.target_lang,
                glossary_map=self.glossary_map,
                output_folder=self.output_folder,
                log=logger  # ✅ Pass logger function
            )
            self.finished.emit(self.file_path)
        except Exception as e:
            self.failed.emit(self.file_path, str(e))