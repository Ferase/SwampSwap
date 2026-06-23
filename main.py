import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QIcon
from PyQt6.QtCore import Qt, QTimer

import app.utils as app_utils
from app.windows.window_main import MainWindow
from app.workers.worker_croc import CrocWorker, CrocAction

_APP_NAME = "Swamp Swap"
_APP_VERSION = "1.0.0"



# Dark mode detector
def _is_dark(app: QApplication) -> bool:
    """Detect whether the user is using a dark theme."""

    # Determine the window's color via the app's palette
    palette = app.palette()
    window_color = palette.color(QPalette.ColorRole.Window)

    # If the window background is darker than mid-grey, assume dark mode
    return window_color.lightness() < 128

def _set_palette_windows(app: QApplication) -> None:
    dark_palette = QPalette()
    dark = QColor(45, 45, 45)
    darker = QColor(30, 30, 30)
    text = QColor(220, 220, 220)
    highlight = QColor(42, 130, 218)

    dark_palette.setColor(QPalette.ColorRole.Window, dark)
    dark_palette.setColor(QPalette.ColorRole.WindowText, text)
    dark_palette.setColor(QPalette.ColorRole.Base, darker)
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, dark)
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, dark)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, text)
    dark_palette.setColor(QPalette.ColorRole.Text, text)
    dark_palette.setColor(QPalette.ColorRole.Button, dark)
    dark_palette.setColor(QPalette.ColorRole.ButtonText, text)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Highlight, highlight)
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    dark_palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.Text,
        QColor(120, 120, 120),
    )
    dark_palette.setColor(
        QPalette.ColorGroup.Disabled,
        QPalette.ColorRole.ButtonText,
        QColor(120, 120, 120),
    )
    app.setPalette(dark_palette)
    return

# Main runner
def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(_APP_NAME)
    app.setOrganizationName(_APP_NAME)
    app.setObjectName(_APP_NAME)
    app.setQuitOnLastWindowClosed(True)
    app.setWindowIcon(QIcon(str(app_utils.determine_icon_filepath("icon.ico", 2))))

    if sys.platform == "win32":
        app.setStyle("Fusion")
        if _is_dark(app):
            _set_palette_windows(app)

    worker = CrocWorker(_APP_NAME, _APP_VERSION)

    window = MainWindow(worker)
    window.show()

    if shutil.which("croc") is None:
        QTimer.singleShot(0,
            lambda: _croc_not_installed(window, worker)
        )

    sys.exit(app.exec())



def _croc_not_installed(window: MainWindow, worker: CrocWorker) -> None:
    worker.change_action(CrocAction.ERROR)
    window._croc_not_installed_alert()



if __name__ == "__main__":
    main()
