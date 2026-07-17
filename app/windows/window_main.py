from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMessageBox,
    QMenuBar, QMenu, QLabel, QInputDialog,
    QToolButton, QStyle, QProgressBar, QWidget,
    QVBoxLayout, QGroupBox
)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer

from app.enums import CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.widgets.widget_send import SendWidget
from app.widgets.widget_receive import ReceiveWidget
from app.widgets.widget_settings import SettingsWidget
from app.windows.window_console import ConsoleWindow
from app.windows.window_about import AboutWindow



# Main window
class MainWindow(QMainWindow):
    """The main window for the application which persists through the app's life. If the main window is killed, the program and all other child windows terminate."""

    # Init
    def __init__(self, worker: CrocWorker) -> None:
        # Run base init
        super().__init__()

        self.worker = worker

        # Instantiate other windows
        self._window_console = ConsoleWindow(self.worker)
        self._window_about = AboutWindow(self.worker, self)

        self._current_selected_tab_index: int = 0

        # Define window title and size
        self.setWindowTitle(self.worker.settings.app_name)
        self.setFixedSize(375, 620)

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
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(container)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setUsesScrollButtons(False)

        self.widget_send = SendWidget(self.worker)
        self.tabs.addTab(self.widget_send, self.worker.settings.tr("generic:send"))

        self.widget_receive = ReceiveWidget(self.worker)
        self.tabs.addTab(self.widget_receive, self.worker.settings.tr("generic:receive"))

        self.widget_settings = SettingsWidget(self.worker)
        self.tabs.addTab(self.widget_settings, self.worker.settings.tr("generic:settings"))

        animation_group = self._build_animation_group()

        layout.addWidget(self.tabs)
        layout.addWidget(animation_group)

    # Build animation group
    def _build_animation_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        group.setContentsMargins(5, 0, 5, 5)

        self.label_animation = QLabel()
        self.label_animation.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addWidget(self.label_animation)
        layout.addSpacing(8)
        layout.addWidget(self.progress_bar)

        return group
        


    # Construct status bar UI
    def _build_statusbar(self) -> None:
        # Set status bar and text
        self.setStatusBar(QStatusBar())
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().setContentsMargins(7, 0, 7, 0)

        self.label_status = QLabel()

        console_fallback_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink)
        console_icon = QIcon.fromTheme("utilities-terminal", console_fallback_icon)

        about_fallback_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        about_icon = QIcon.fromTheme("help-browser", about_fallback_icon)

        self.btn_console = QToolButton()
        self.btn_console.setIcon(console_icon)

        self.btn_about = QToolButton()
        self.btn_about.setIcon(about_icon)

        self.statusBar().addWidget(self.label_status)
        self.statusBar().addPermanentWidget(self.btn_console)
        self.statusBar().addPermanentWidget(self.btn_about)



    def _open_console_window(self) -> None:
        """Shows the console window"""

        self._window_console.show()

    def _open_about_window(self) -> None:
        """Shows the about window. It is raised as a modal and will block actions on the main window until closed."""

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
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.finished.connect(self._reset_progress_bar)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)
        self.widget_settings.settings_changed.connect(self._apply_asterisk_to_unsaved_settings)

        self.tabs.currentChanged.connect(self._check_settings_have_changed_on_tab_switch)

        self.btn_console.clicked.connect(self._open_console_window)
        self.btn_about.clicked.connect(self._open_about_window)

        self.worker.settings.theme_manager.animation_manager.frame_ready.connect(self._on_animation_frame)

    def _set_status(self):
        """Set the status bar text on the bottom left of the window."""

        # A label is used instead of self.statusBar().showMessage() because of a Windows bug
        self.label_status.setText(self.worker.get_action_text())
        self.label_status.setToolTip(self.worker.get_action_text_only())

        self.worker.settings.theme_manager.animation_manager.status_changed.emit(self.worker.get_operation(), self.worker.get_action())

    def _append_error_to_status(self, error: str) -> None:
        """Will append an error to the status tootlip if there's an error to report."""

        # We msut be in an error state to do this
        if not self.worker.state.action == CrocAction.ERROR:
            return
        
        # Do nothing if the error text is empty
        if not error:
            return
        
        # Combine text adn output
        text: str = f"{self.worker.state.action.text}: {error}"
        self.label_status.setToolTip(text[1:].strip())

    def _check_settings_have_changed_on_tab_switch(self, index: int) -> None:
        """Blocks the user from switching off of the settings tab unless they save their changes."""

        # Monitor the current tab index
        if not self._current_selected_tab_index == 2:
            self._current_selected_tab_index = index
            return

        # If settings aren't dirty, do nothing
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

        # Click the save button for the user
        if box == QMessageBox.StandardButton.Save:
            self.widget_settings.btn_save.click()

        self._current_selected_tab_index = index

    def _apply_asterisk_to_unsaved_settings(self, dirty: bool) -> None:
        """Adds an asterisk to the settings tab name when settings ahve been modified."""

        text: str = self.worker.settings.tr("generic:settings")
        if dirty:
            text += "*"

        self.tabs.setTabText(2, text)
    
    def _is_operation_running(self) -> bool:
        if self.worker.state.operation == CrocOperation.IDLE:
            return False
        
        return True


    def _send_file(self) -> None:
        """Qucik send files function used for the top menu bar."""

        self.tabs.tabBar().setCurrentIndex(0)

        # Warn the user that they will lose the list of files they've queued to send
        if self.widget_send.are_files_selected():
            box = QMessageBox.information(
                self,
                self.worker.settings.tr("dialog:quick_send_warning:title"),
                self.worker.settings.tr("dialog:quick_send_warning:body"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if box == QMessageBox.StandardButton.No:
                return

        self.widget_send._reset_selected_fies_folders()
        self.widget_send.btn_add_files.click()

        if not self.widget_send.are_files_selected():
            return
        
        self.widget_send.btn_send.click()

        # Wait a moment before copying the code
        QTimer.singleShot(20, self.widget_send.btn_copy_code.click)

    def _send_folder(self) -> None:
        """Qucik send folders function used for the top menu bar."""

        self.tabs.tabBar().setCurrentIndex(0)

        # Warn the user that they will lose the list of files they've queued to send
        if self.widget_send.are_files_selected():
            box = QMessageBox.information(
                self,
                self.worker.settings.tr("dialog:quick_send_warning:title"),
                self.worker.settings.tr("dialog:quick_send_warning:body"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if box == QMessageBox.StandardButton.No:
                return

        self.widget_send._reset_selected_fies_folders()
        self.widget_send.btn_add_folders.click()

        if not self.widget_send.are_files_selected():
            return
        
        self.widget_send.btn_send.click()

        # Wait a moment before copying the code
        QTimer.singleShot(20, self.widget_send.btn_copy_code.click)

    def _receive(self) -> None:
        """Qucik receive files/folders function used for the top menu bar."""

        self.tabs.tabBar().setCurrentIndex(1)

        # Entery textbox for the code
        text, ok_pressed = QInputDialog.getText(
            self,
            self.worker.settings.tr("menubar:window_receive_code:title"),
            self.worker.settings.tr("menubar:window_receive_code:body")
        )

        # Do nothing if the user cancelled
        if not ok_pressed:
            return

        # If the user entered no text, warn them and then cancel
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
        """Stops/cancels any currently active operations and kills the worker."""

        # Check if an operation is running and, if so, stop it gracefully
        match self.worker.state.operation:
            case CrocOperation.SENDING:
                self.widget_send.btn_send.click()
            case CrocOperation.RECEIVING:
                self.widget_receive.btn_receive.click()
            case _:
                pass

        self.worker.stop()



    def _run_startup_functions(self) -> None:
        """Executes a collection of functions at startup."""

        self._set_status()
        self._show_console()

    def _show_console(self) -> None:
        """If the user has enabled the setting to start the console on startup, this function will open the console window."""

        if self.worker.settings.startup_console:
            self._window_console.show()



    def closeEvent(self, event):
        """Kills all child windows, stops the worker, and terminates the program. Will prompt the user first if an operation is running."""

        if self._is_operation_running():
            box = QMessageBox.warning(
                self,
                self.worker.settings.tr("dialog:close_warning:title"),
                self.worker.settings.tr("dialog:close_warning:body"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if box == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            event.accept()

        self._window_console.close()
        self._window_about.close()
        self.widget_send.window_filelist.close()
        self.worker.stop()
        super().closeEvent(event)

    def _on_progress_update(self, percent: int, filename: str, is_hashing: bool) -> None:
        """Handle progress bar updating."""

        is_sending: bool = self.worker.state.operation == CrocOperation.SENDING

        # Create prefix; if we're hashing, just say hashing, otherwise display sending or receiving text
        if is_hashing:
            prefix = self.worker.settings.tr("state:hashing")
        else:
            prefix = self.worker.settings.tr("state:sending") if is_sending else self.worker.settings.tr("state:receiving")

        # Fixes the issue of hashing (which is generally a fast process) stopping at 99 percent even when it's actually done
        if prefix:
            percent = 100 if percent == 99 else percent

        self.progress_bar.setValue(percent)
        self.progress_bar.setFormat(f"{prefix} {filename}  {percent}%")

    def _reset_progress_bar(self) -> None:
        """Handle progress bar display when an operation ends."""

        # Reset the format to remove the other text
        self.progress_bar.resetFormat()

        # 100% if completed, 0% otherwise (starting, cancelling, error, etc.)
        value: int = 100 if self.worker.state.action == CrocAction.COMPLETED else 0
        self.progress_bar.setValue(value)

    def _change_animation(self) -> None:
        """Change the animation on the lower part of the window"""

        self.label_animation.setMovie(self.worker.settings.theme_manager.animation_manager.current_anim)
        self.worker.settings.theme_manager.animation_manager.current_anim.start()

    def _on_animation_frame(self, pixmap: QPixmap) -> None:
        """Display the latest recolored animation frame."""

        self.label_animation.setPixmap(pixmap)