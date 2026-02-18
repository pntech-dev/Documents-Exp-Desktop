import sys
from pathlib import Path

APP_NAME = "Documents Exp"

def get_app_root() -> Path:
    """Returns the root directory of the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    else:
        # Running from source: utils/.. -> root
        return Path(__file__).resolve().parent.parent

def get_app_data_dir() -> Path:
    """
    Returns the path to the roaming application data directory (Profiles, etc).

    Returns:
        Path: The path to the app data directory.
    """
    home = Path.home()
    if sys.platform == "win32":
        return home / "AppData" / "Roaming" / APP_NAME
    elif sys.platform == "darwin":
        return home / "Library" / "Application Support" / APP_NAME
    else:
        # Linux / Unix (XDG standard)
        return home / ".local" / "share" / APP_NAME

def get_local_data_dir() -> Path:
    """
    Returns the path to the local application data directory (Logs, Caches).

    Returns:
        Path: The path to the local data directory.
    """
    home = Path.home()
    if sys.platform == "win32":
        return home / "AppData" / "Local" / APP_NAME
    elif sys.platform == "darwin":
        return home / "Library" / "Caches" / APP_NAME
    else:
        # Linux / Unix (XDG standard)
        return home / ".cache" / APP_NAME