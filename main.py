import sys
import shutil
from pathlib import Path
from packaging.version import Version
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QPalette, QColor, QIcon, QDesktopServices
from PyQt6.QtCore import Qt, QUrl, QTimer

from get_version import UpdateChecker
import app.utils as app_utils
from app.windows.window_main import MainWindow
from app.workers.worker_croc import CrocWorker, CrocAction

_APP_NAME = "Swamp Swap"
_APP_VERSION = "1.1.2"



# Dark mode detector
def _is_dark(app: QApplication) -> bool:
    """Detect whether the user is using a dark theme."""

    # Determine the window's color via the app's palette
    palette = app.palette()
    window_color = palette.color(QPalette.ColorRole.Window)

    # If the window background is darker than mid-grey, assume dark mode
    return window_color.lightness() < 128

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

    worker = CrocWorker(_APP_NAME, _APP_VERSION)

    window = MainWindow(worker)
    window.show()

    if shutil.which("croc") is None:
        QTimer.singleShot(0,
            lambda: _croc_not_installed(window, worker)
        )

    if worker.settings.startup_croc_updates_check:
        croc_checker = UpdateChecker("1", "schollz", "croc")
        croc_checker.update_available.connect(
            lambda v: _new_croc_version_available(window, worker, v)
        )
        croc_checker.start()

    if worker.settings.startup_swampswap_updates_check:
        swampswap_checker = UpdateChecker("1", "Ferase", "SwampSwap")
        swampswap_checker.update_available.connect(
            lambda v: _new_swampswap_version_available(window, worker, v)
        )
        swampswap_checker.start()

    sys.exit(app.exec())



def _croc_not_installed(window: MainWindow, worker: CrocWorker) -> None:
    worker.change_action(CrocAction.ERROR)
    window._croc_not_installed_alert()

def _new_croc_version_available(parent, worker: CrocWorker, new_version: str) -> None:
    result = QMessageBox.information(
        parent,
        worker.settings.tr("dialog:croc_update_available:title"),
        worker.settings.tr("dialog:croc_update_available:body1").format(v=f"<b>{new_version}</b>") + "\n" + worker.settings.tr("dialog:croc_update_available:body2") + "\n" + f"<b>{worker.settings.tr('dialog:croc_update_available:body3')}</b>",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )

    if result == QMessageBox.StandardButton.Yes:
        QDesktopServices.openUrl(
            QUrl("https://github.com/Ferase/SwampSwap/releases/latest")
        )

def _new_swampswap_version_available(parent, worker: CrocWorker, new_version: str) -> None:
    result = QMessageBox.information(
        parent,
        worker.settings.tr("dialog:swampswap_update_available:title"),
        worker.settings.tr("dialog:swampswap_update_available:body1").format(v=f"<b>{new_version}</b>") + "\n" + worker.settings.tr("dialog:swampswap_update_available:body2"),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )

    if result == QMessageBox.StandardButton.Yes:
        QDesktopServices.openUrl(
            QUrl("https://github.com/Ferase/SwampSwap/releases/latest")
        )



if __name__ == "__main__":
    main()
