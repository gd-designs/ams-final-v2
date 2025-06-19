from PySide6.QtCore import QThread, Signal
from functions.translation_pipeline import process_file
from pathlib import Path


class TranslationWorker(QThread):
    # --------------------------------------------------------------
    # Signals
    # --------------------------------------------------------------
    log_signal = Signal(str)          # → live log lines
    finished   = Signal(str)          # → final translated path
    failed     = Signal(str, str)     # → (input path, error msg)

    # --------------------------------------------------------------
    # Init
    # --------------------------------------------------------------
    def __init__(self, file_path, source_lang, target_lang,
                 glossary_map, output_folder):
        super().__init__()
        self.input_path   = Path(file_path).resolve()   # original file
        self.source_lang  = source_lang
        self.target_lang  = target_lang
        self.glossary_map = glossary_map
        self.output_folder = output_folder             # may be None / ""
                                                     
    # --------------------------------------------------------------
    # Worker entry-point
    # --------------------------------------------------------------
    def run(self) -> None:
        try:
            # pass log lines to GUI
            def logger(msg: str) -> None:
                self.log_signal.emit(msg)

            # heavy lifting – must **return** output path
            translated_path = process_file(
                dwg_path      = self.input_path,
                source_lang   = self.source_lang,
                target_lang   = self.target_lang,
                glossary_map  = self.glossary_map,
                output_folder = self.output_folder,
                log           = logger
            )

            # success → emit final path for on_translation_finished()
            self.finished.emit(str(translated_path))

        except Exception as err:
            # failure → emit original file & error
            self.failed.emit(str(self.input_path), str(err))


