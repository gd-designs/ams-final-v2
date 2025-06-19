# functions/paths.py
from __future__ import annotations

import sys, os
from pathlib import Path

# ──────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────
def app_root() -> Path:
    """
    Root of the *project*, not the functions package.
    If bundled with PyInstaller we still respect _MEIPASS.
    """
    if getattr(sys, "frozen", False):          # PyInstaller
        return Path(sys._MEIPASS)

    # ⬇️  two levels up:  .../functions/paths.py  ->  .../<project_root>
    return Path(__file__).resolve().parents[2]  # <--- changed line


def _local_glossary_dir() -> Path:
    return app_root() / "glossaries"


def _network_glossary_dir() -> Path:
    # 👉 adjust if the shared-folder structure ever changes
    return Path(r"\\srv012\dati\Risorse condivise\AMS Translator Tool\glossaries")


def _safe_mkdir(p: Path) -> bool:
    """
    Try to create *p* (and parents).  
    Return True on success, False if the dir is not writable / reachable.
    """
    try:
        p.mkdir(parents=True, exist_ok=True)
        testfile = p / ".write_test"
        testfile.touch(exist_ok=True)
        testfile.unlink(missing_ok=True)
        return True
    except OSError:
        return False


# ──────────────────────────────────────────────────────────────
# public helpers
# ──────────────────────────────────────────────────────────────
def glossary_paths() -> tuple[Path, Path]:
    """
    Return (primary, fallback) directories – they are NOT guaranteed
    to be writable, that check is left to the caller.
    """
    return _local_glossary_dir(), _network_glossary_dir()


def get_glossary_dir() -> Path:
    """
    Return the first directory (local → network) that exists **and** is writable.
    Falls back to the local folder if the share is offline / read-only.
    """
    primary, fallback = glossary_paths()

    if _safe_mkdir(primary):
        return primary      # ✅ local path is fine

    if _safe_mkdir(fallback):
        return fallback     # ✅ remote share is alive / writable

    # Last-ditch effort – use a sub-folder in the user’s HOME to avoid crashing
    home_fallback = Path.home() / "AMS-Translator-Glossaries"
    _safe_mkdir(home_fallback)
    return home_fallback

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource inside PyInstaller bundle or locally."""
    if getattr(sys, 'frozen', False):
        # PyInstaller runtime folder (_MEIPASS)
        base_path = Path(sys._MEIPASS)
    else:
        # In dev mode, resolve from project root
        base_path = Path(__file__).resolve().parents[1]  # points to project root

    return str(base_path / relative_path)

def _desktop_folder() -> Path:
    """Return the user’s Desktop (cross-locale, cross-Windows-version)."""
    # Works on Windows 7-11; falls back to HOME if Desktop cannot be resolved
    desktop = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
    return desktop if desktop.exists() else Path.home()

def queue_dir() -> Path:
    """
    A per-user, writable folder that survives updates:
    • <Desktop>\AMS-Applicazione-Coda
    """
    qdir = _desktop_folder() / "AMS-Applicazione-Coda"
    qdir.mkdir(parents=True, exist_ok=True)
    return qdir

def translated_dir() -> Path:
    """
    Returns a user-local path to store translated files, e.g. on Desktop.
    Creates it if missing.
    """
    desktop = Path.home() / "Desktop"
    path = desktop / "AMS-Applicazione-Tradotto"
    path.mkdir(parents=True, exist_ok=True)
    return path
