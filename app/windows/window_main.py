import subprocess
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMessageBox,
    QMenuBar, QMenu, QApplication, QPushButton,
    QGroupBox, QVBoxLayout, QToolButton, QStyle,
    QInputDialog
)
from PyQt6.QtGui import QAction, QDesktopServices, QIcon
from PyQt6.QtCore import QUrl, pyqtSignal, QTimer

import app.utils as app_utils
from app.enums import CrocState, CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.widgets.widget_send import SendWidget
from app.widgets.widget_receive import ReceiveWidget
from app.widgets.widget_settings import SettingsWidget
from app.windows.window_console import ConsoleWindow
from app.windows.window_about import AboutWindow



# Main window
class MainWindow(QMainWindow):
    # Init
    def __init__(self, worker: CrocWorker) -> None:
        # Run base init
        super().__init__()

        self.worker = worker

        self._window_console = ConsoleWindow(self.worker)
        self._window_about = AboutWindow(self.worker, self)

        self._current_selected_tab_index: int = 0

        # Define window title and size
        self.setWindowTitle(self.worker.settings.app_name)
        self.setFixedSize(360, 475)

        # Build UI
        self._build_central()
        self._build_menu()
        self._build_statusbar()

        self._connect_signals()
        self._run_startup_functions()

    def _build_menu(self):
        menubar: QMenuBar = self.menuBar()

        # File menu
        self.file_menu: QMenu = menubar.addMenu(self.worker.settings.tr("menubar:file"))
        self.actions_menu: QMenu = menubar.addMenu(self.worker.settings.tr("menubar:actions"))

        self.console_action = QAction(self.worker.settings.tr("menubar:file:console"), self)
        self.console_action.setShortcut("Shift+C")
        self.console_action.triggered.connect(self._open_console_window)
        self.file_menu.addAction(self.console_action)

        self.about_action = QAction(self.worker.settings.tr("menubar:file:about"), self)
        self.about_action.setShortcut("Shift+A")
        self.about_action.triggered.connect(self._open_about_window)
        self.file_menu.addAction(self.about_action)

        self.send_file_action = QAction(self.worker.settings.tr("menubar:actions:send_file"), self)
        self.send_file_action.setShortcut("Ctrl+S")
        self.send_file_action.triggered.connect(self._send_file)
        self.actions_menu.addAction(self.send_file_action)

        self.send_folder_action = QAction(self.worker.settings.tr("menubar:actions:send_folder"), self)
        self.send_folder_action.setShortcut("Ctrl+Shift+S")
        self.send_folder_action.triggered.connect(self._send_folder)
        self.actions_menu.addAction(self.send_folder_action)

        self.receive_action = QAction(self.worker.settings.tr("menubar:actions:receive"), self)
        self.receive_action.setShortcut("Ctrl+R")
        self.receive_action.triggered.connect(self._receive)
        self.actions_menu.addAction(self.receive_action)

        self.stop_actopm = QAction(self.worker.settings.tr("menubar:actions:stop_all"), self)
        self.stop_actopm.setShortcut("Ctrl+Shift+D")
        self.stop_actopm.triggered.connect(self._stop_all)
        self.actions_menu.addAction(self.stop_actopm)

    # Construct main UI
    def _build_central(self) -> None:
        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setUsesScrollButtons(False)
        self.setCentralWidget(self.tabs)

        self.widget_send = SendWidget(self.worker)
        self.tabs.addTab(self.widget_send, self.worker.settings.tr("generic:send"))

        self.widget_receive = ReceiveWidget(self.worker)
        self.tabs.addTab(self.widget_receive, self.worker.settings.tr("generic:receive"))

        self.widget_settings = SettingsWidget(self.worker)
        self.tabs.addTab(self.widget_settings, self.worker.settings.tr("generic:settings"))

    # Construct status bar UI
    def _build_statusbar(self) -> None:
        # Set status bar and text
        self.setStatusBar(QStatusBar())
        self.statusBar().setSizeGripEnabled(False)

        console_fallback_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink)
        console_icon = QIcon.fromTheme("utilities-terminal", console_fallback_icon)

        about_fallback_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        about_icon = QIcon.fromTheme("help-browser", about_fallback_icon)

        self.btn_console = QToolButton()
        self.btn_console.setIcon(console_icon)

        self.btn_about = QToolButton()
        self.btn_about.setIcon(about_icon)

        self.statusBar().addPermanentWidget(self.btn_console)
        self.statusBar().addPermanentWidget(self.btn_about)



    def _open_console_window(self) -> None:
        self._window_console.show()

    def _open_about_window(self) -> None:
        self._window_about.exec()

    

    def _retranslate(self) -> None:
        """Retranslate everything on language change."""

        self.tabs.setTabText(0, self.worker.settings.tr("generic:send"))
        self.tabs.setTabText(1, self.worker.settings.tr("generic:receive"))
        self._apply_asterisk_to_unsaved_settings(self.widget_settings.dirty)
        self.statusBar().showMessage(self.worker.get_action_text())
        self.statusBar().setToolTip(self.worker.get_action_text_only())
        
        self.file_menu.menuAction().setText(self.worker.settings.tr("menubar:file"))
        self.actions_menu.menuAction().setText(self.worker.settings.tr("menubar:actions"))
        self.console_action.setText(self.worker.settings.tr("menubar:file:console"))
        self.about_action.setText(self.worker.settings.tr("menubar:file:about"))
        self.send_file_action.setText(self.worker.settings.tr("menubar:actions:send_file"))
        self.send_folder_action.setText(self.worker.settings.tr("menubar:actions:send_folder"))
        self.receive_action.setText(self.worker.settings.tr("menubar:actions:receive"))
        self.stop_actopm.setText(self.worker.settings.tr("menubar:actions:stop_all"))



    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.state_changed.connect(self._set_status)
        self.worker.error_state.connect(self._append_error_to_status)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)
        self.widget_settings.settings_changed.connect(self._apply_asterisk_to_unsaved_settings)

        self.tabs.currentChanged.connect(self._check_settings)

        self.btn_console.clicked.connect(self._open_console_window)
        self.btn_about.clicked.connect(self._open_about_window)

    def _set_status(self):
        self.statusBar().showMessage(self.worker.get_action_text())
        self.statusBar().setToolTip(self.worker.get_action_text_only())

    def _append_error_to_status(self, error: str) -> None:
        if not self.worker.state.action == CrocAction.ERROR:
            return
        
        if not error:
            return
        
        text: str = f"{self.worker.state.action.text}: {error}"
        
        self.statusBar().showMessage(text)
        self.statusBar().setToolTip(text[1:].strip())

    def _check_settings(self, index: int) -> None:
        if not self._current_selected_tab_index == 2:
            self._current_selected_tab_index = index
            return

        if not self.widget_settings.dirty:
            self._current_selected_tab_index = index
            return
        
        box = QMessageBox.information(
            self,
            self.worker.settings.tr("dialog:unsaved_settings:title"),
            self.worker.settings.tr("dialog:unsaved_settings:body"),
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Ignore,
            QMessageBox.StandardButton.Save
        )

        if box == QMessageBox.StandardButton.Save:
            self.widget_settings.btn_save.click()

        self._current_selected_tab_index = index

    def _apply_asterisk_to_unsaved_settings(self, dirty: bool) -> None:
        text: str = self.worker.settings.tr("generic:settings")
        if dirty:
            text += "*"

        self.tabs.setTabText(2, text)



    def _send_file(self) -> None:
        self.tabs.tabBar().setCurrentIndex(0)
        self.widget_send._reset_selected_fies_folders()
        self.widget_send.btn_add_files.click()

        if not self.widget_send.are_files_selected():
            return
        
        self.widget_send.btn_send.click()
        QTimer.singleShot(20, self.widget_send.btn_copy_code.click)

    def _send_folder(self) -> None:
        self.tabs.tabBar().setCurrentIndex(0)
        self.widget_send._reset_selected_fies_folders()
        self.widget_send.btn_add_folders.click()

        if not self.widget_send.are_files_selected():
            return
        
        self.widget_send.btn_send.click()
        QTimer.singleShot(20, self.widget_send.btn_copy_code.click)

    def _receive(self) -> None:
        self.tabs.tabBar().setCurrentIndex(1)

        text, ok_pressed = QInputDialog.getText(
            self,
            self.worker.settings.tr("menubar:window_receive_code:title"),
            self.worker.settings.tr("menubar:window_receive_code:body")
        )

        if not ok_pressed:
            return

        if not text:
            QMessageBox.warning(
                self,
                self.worker.settings.tr("menubar:window_bad_code:title"),
                self.worker.settings.tr("menubar:window_bad_code:body"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return
        
        self.widget_receive.btn_browse_output_folder.click()
        self.widget_receive.lineedit_code.setText(text)
        self.widget_receive.btn_receive.click()

    def _stop_all(self) -> None:
        match self.worker.state.operation:
            case CrocOperation.SENDING:
                self.widget_send.btn_send.click()
            case CrocOperation.RECEIVING:
                self.widget_receive.btn_receive.click()
            case _:
                pass

        self.worker.stop()



    def _run_startup_functions(self) -> None:
        self._set_status()
        self._show_console()

    def _show_console(self) -> None:
        if self.worker.settings.startup_console:
            self._window_console.show()



    def closeEvent(self, event):
        self._window_console.close()
        self._window_about.close()
        super().closeEvent(event)