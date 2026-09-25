import os
import sys
import certifi
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtCore import QUrl

import app.utils as app_utils
from app.windows.window_main import MainWindow
from app.workers.worker_croc import CrocWorker

# Name and version variables
_APP_NAME = "Swamp Swap"
_APP_VERSION = "1.4.8"
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
    worker = CrocWorker(_APP_NAME, _APP_VERSION, _MINIMUM_CROC_VERSION)

    # Create and show main window
    window = MainWindow(worker)
    window.show()

    # General exit logic
    sys.exit(app.exec())



# Start everything
if __name__ == "__main__":
    main()
