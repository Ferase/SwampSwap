import os
import sys
import shutil
import certifi
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtCore import QUrl

import app.utils as app_utils
from app.windows.window_main import MainWindow
from app.workers.worker_croc import CrocWorker, CrocAction

# Name and version variables
_APP_NAME = "Swamp Swap"
_APP_VERSION = "1.4.13"
_MINIMUM_CROC_VERSION = "11.2.4"



def _configure_ssl() -> None:
    """Point Python's SSL to bundled certificates when running as an executable."""

    try:
        os.environ["SSL_CERT_FILE"] = certifi.where()
        os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
    except ImportError:
        pass

# Main runner
def main() -> None:
    """Main function that creates the persistent worker and the main window. Also handles critical warnings and updater calling"""

    _configure_ssl()

    # Create and setup application
    app = QApplication(sys.argv)
    app.setApplicationName(_APP_NAME)
    app.setOrganizationName(_APP_NAME)
    app.setObjectName(_APP_NAME)
    app.setQuitOnLastWindowClosed(True)
    app.setWindowIcon(QIcon(str(app_utils.determine_filepath("icon.ico", 2))))

    # Windows: Set the app's style to Qt Fusion
    if sys.platform == "win32":
        app.setStyle("Fusion")

    # Create worker
    worker = CrocWorker(_APP_NAME, _APP_VERSION)

    # Create and show main window
    window = MainWindow(worker)
    window.show()

    # Test if croc is installed. If not, raise an error
    if shutil.which(worker.settings.croc_path) is None:
        _croc_not_installed(window, worker)

    # Test if croc is below minimum version
    elif _is_croc_too_old(worker):
        _croc_too_old(window, worker)

    # General exit logic
    sys.exit(app.exec())



def _croc_not_installed(window: MainWindow, worker: CrocWorker) -> None:
    """If croc is not installed, raise an error and either open the install instructions or close the program."""

    # Set status to error (why the hell not)
    worker.change_action(CrocAction.ERROR)

    # Raise a message box and tell the user croc isn't installed
    box = QMessageBox.warning(
        window,
        worker.settings.tr("dialog:croc_not_found:title"),
        "<br><br>".join([
            worker.settings.tr("dialog:croc_not_found:body1"),
            worker.settings.tr("dialog:croc_not_found:body2"),
            worker.settings.tr("dialog:croc_not_found:body3")
        ]),
        QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Close,
        QMessageBox.StandardButton.Open
    )

    # If the user chooses open, open the install instructions on croc's GitHub page
    if box == QMessageBox.StandardButton.Open:
        QDesktopServices.openUrl(QUrl("https://github.com/schollz/croc#install"))
    elif box == QMessageBox.StandardButton.Ignore:
        return

    sys.exit()

def _croc_too_old(window: MainWindow, worker: CrocWorker) -> None:
    """Raises an error if croc is found to be too old."""

    # Set status to error (why the hell not)
    worker.change_action(CrocAction.ERROR)

    # Raise a message box and tell the user croc isn't installed
    box = QMessageBox.warning(
        window,
        worker.settings.tr("dialog:croc_too_old:title"),
        "<br><br>".join([
            worker.settings.tr("dialog:croc_too_old:body1"),
            worker.settings.tr("dialog:croc_too_old:body2").format(v1=worker.get_croc_version_number_only(), v2=f"v{_MINIMUM_CROC_VERSION}"),
            worker.settings.tr("dialog:croc_too_old:body3"),
            worker.settings.tr("dialog:croc_too_old:body4")
        ]),
        QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Close,
        QMessageBox.StandardButton.Open
    )

    # If the user chooses open, open the install instructions on croc's GitHub page
    if box == QMessageBox.StandardButton.Open:
        QDesktopServices.openUrl(QUrl("https://github.com/schollz/croc#install"))
    elif box == QMessageBox.StandardButton.Ignore:
        return

    sys.exit()

def _is_croc_too_old(worker: CrocWorker) -> bool:
    croc_version: str = worker.get_croc_version_number_only()
    
    def _parse(v: str) -> tuple[int]:
        return tuple(int(x) for x in v.lstrip("v").split("."))

    return bool(_parse(croc_version) < _parse(_MINIMUM_CROC_VERSION))



# Start everything
if __name__ == "__main__":
    main()
