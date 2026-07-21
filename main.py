import sys
import shutil
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtCore import QUrl

from get_version import UpdateChecker
import app.utils as app_utils
from app.windows.window_main import MainWindow
from app.workers.worker_croc import CrocWorker, CrocAction

# Name and version variables
_APP_NAME = "Swamp Swap"
_APP_VERSION = "1.2.6"



# Main runner
def main() -> None:
    """Main function that creates the persistent worker and the main window. Also handles critical warnings and updater calling"""

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
    if shutil.which("croc") is None:
        _croc_not_installed(window, worker)

    # Check for various updates
    else:
        # If the user hasn't disabled checking for croc updates, check schollz/croc for a new release
        if worker.settings.startup_croc_updates_check:
            croc_checker = UpdateChecker(worker.get_croc_version_number_only(), "schollz", "croc")
            croc_checker.update_available.connect(
                lambda v: _new_croc_version_available(window, worker, v)
            )
            croc_checker.start()

        # If the user hasn't disabled checking for Swamp Swamp GUI updates, check Ferase/SwampSwap for a new release
        if worker.settings.startup_swampswap_updates_check:
            swampswap_checker = UpdateChecker(_APP_VERSION, "Ferase", "SwampSwap")
            swampswap_checker.update_available.connect(
                lambda v: _new_swampswap_version_available(window, worker, v)
            )
            swampswap_checker.start()

    # General exit logic
    sys.exit(app.exec())



def _croc_not_installed(window: MainWindow, worker: CrocWorker) -> None:
    """If croc is not installed, raise an error and either open the install instructions or close the program."""

    # Set status to error (why the hell not)
    worker.change_action(CrocAction.ERROR)

    # Raise a message box and tell the user croc isn't installed
    box = QMessageBox.warning(
        window,
        worker.settings.tr("dialog:croc_not_installed:title"),
        worker.settings.tr("dialog:croc_not_installed:body1") + "<br><br>" + worker.settings.tr("dialog:croc_not_installed:body2"),
        QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Close,
        QMessageBox.StandardButton.Open
    )

    # If the user chooses open, open the install instructions on croc's GitHub page
    if box == QMessageBox.StandardButton.Open:
        QDesktopServices.openUrl(QUrl("https://github.com/schollz/croc#install"))

    # Kill the application
    window.close()

def _new_croc_version_available(parent, worker: CrocWorker, new_version: str) -> None:
    """Raise an alert if a new croc version is detected on the schollz/croc repo on GitHub"""

    # Ask the user if they want to update
    result = QMessageBox.information(
        parent,
        worker.settings.tr("dialog:croc_update_available:title"),
        worker.settings.tr("dialog:croc_update_available:body1").format(v=f"<b>{new_version}</b>") + "<br><br>" + worker.settings.tr("dialog:croc_update_available:body2") + "<br><br>" + f"<b>{worker.settings.tr('dialog:croc_update_available:body3')}</b>",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )

    # If they do, open the GitHub
    if result == QMessageBox.StandardButton.Yes:
        QDesktopServices.openUrl(
            QUrl("https://github.com/schollz/croc/releases/latest")
        )

def _new_swampswap_version_available(parent, worker: CrocWorker, new_version: str) -> None:
    """Raise an alert if a new Swamp Swap version is detected on the Ferase/SwampSwap repo on GitHub"""

    # Ask the user if they want to update
    result = QMessageBox.information(
        parent,
        worker.settings.tr("dialog:swampswap_update_available:title"),
        worker.settings.tr("dialog:swampswap_update_available:body1").format(v=f"<b>{new_version}</b>") + "<br><br>" + worker.settings.tr("dialog:swampswap_update_available:body2"),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes
    )

    # If they do, open the GitHub
    if result == QMessageBox.StandardButton.Yes:
        QDesktopServices.openUrl(
            QUrl("https://github.com/Ferase/SwampSwap/releases/latest")
        )



# Start everything
if __name__ == "__main__":
    main()
