import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QMessageBox,
    QMenuBar, QMenu, QLabel, QInputDialog,
    QToolButton, QStyle, QProgressBar, QWidget,
    QVBoxLayout, QGroupBox, QDialog, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog, QCheckBox,
    QGridLayout
)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import Qt, QTimer

import app.utils as app_utils
from app.enums import CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.widgets.tabs.widget_send import SendWidget
from app.widgets.tabs.widget_receive import ReceiveWidget
from app.widgets.tabs.widget_settings import SettingsWidget
from app.windows.window_console import ConsoleWindow
from app.windows.window_about import AboutWindow



class FirstRunReceivePathDialog(QDialog):
    def __init__(self, worker: CrocWorker, parent=None):
        super().__init__(parent)

        self.worker = worker

        self.setWindowTitle(self.worker.settings.tr("firstrun:window:title"))
        self.setFixedSize(500, 300)

        self._build_central()
        self._connect_signals()

    def _build_central(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        main_group = self._build_main()
        buttons_group = self._build_buttons()

        root.addWidget(main_group)
        root.addWidget(buttons_group)

    def _build_main(self) -> QGroupBox:
        self.main_group = QGroupBox(self.worker.settings.tr("firstrun:group:set_settings"))
        layout = QVBoxLayout(self.main_group)

        self.label_path = QLabel(self.worker.settings.tr("options:default_receive_path:label"))
        self.label_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))

        path_row = QHBoxLayout()
        self.lineedit_path = QLineEdit()
        self.lineedit_path.setText(self.worker.settings.default_receive_path)
        self.lineedit_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))

        self.btn_browse = QPushButton(self.worker.settings.tr("generic:browse"))

        ui_grid = QGridLayout()

        self.label_lang = QLabel(self.worker.settings.tr("options:language:label"))
        self.label_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))

        self.combo_lang = app_utils.BoundedComboBox()
        self.combo_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))
        self.combo_lang.addItems(self.worker.settings.locale_manager.get_lang_list())
        self.combo_lang.setCurrentText(self.worker.settings.lang)

        # Language will remain disabled until another language is added
        self.combo_lang.setEnabled(False)

        self.label_theme = QLabel(self.worker.settings.tr("options:theme:label"))
        self.label_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))

        self.combo_theme = app_utils.BoundedComboBox()
        self.combo_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))
        self.combo_theme.addItems(self.worker.settings.theme_manager.get_theme_list() + ["Random"])
        self.combo_theme.setCurrentText(self.worker.settings.theme)

        self.checkbox_enable_sound = QCheckBox(self.worker.settings.tr("options:enable_sound:label"))
        self.checkbox_enable_sound.setToolTip(self.worker.settings.tr("options:enable_sound:tooltip"))
        self.checkbox_enable_sound.setChecked(self.worker.settings.enable_sound)

        layout.addLayout(ui_grid)
        ui_grid.addWidget(self.label_lang, 0, 0)
        ui_grid.addWidget(self.combo_lang, 1, 0)
        ui_grid.addWidget(self.label_theme, 0, 1)
        ui_grid.addWidget(self.combo_theme, 1, 1)

        layout.addStretch()

        layout.addWidget(self.label_path)

        layout.addLayout(path_row)
        path_row.addWidget(self.lineedit_path)
        path_row.addWidget(self.btn_browse)

        layout.addStretch()

        layout.addWidget(self.checkbox_enable_sound)

        layout.addStretch()

        return self.main_group

    def _build_buttons(self) -> None:
        group = QGroupBox()
        layout = QHBoxLayout(group)

        self.btn_ok = QPushButton(self.worker.settings.tr("generic:ok"))

        layout.addStretch()
        layout.addWidget(self.btn_ok)

        return group

    def _retranslate(self) -> None:
        self.setWindowTitle(self.worker.settings.tr("firstrun:window:title"))
        self.main_group.setTitle(self.worker.settings.tr("firstrun:group:set_settings"))
        
        self.label_path.setText(self.worker.settings.tr("options:default_receive_path:label"))
        self.label_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))
        self.lineedit_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))
        self.btn_browse.setText(self.worker.settings.tr("generic:browse"))

        self.label_lang.setText(self.worker.settings.tr("options:language:label"))
        self.label_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))
        self.label_theme.setText(self.worker.settings.tr("options:theme:label"))
        self.label_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))

        self.checkbox_enable_sound.setText(self.worker.settings.tr("options:enable_sound:label"))
        self.checkbox_enable_sound.setToolTip(self.worker.settings.tr("options:enable_sound:tooltip"))

        self.btn_ok.setText(self.worker.settings.tr("generic:ok"))

    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.btn_browse.clicked.connect(self._browse)
        self.lineedit_path.textChanged.connect(self._enable_disable_button)

        self.combo_lang.currentTextChanged.connect(self._change_lang)
        self.combo_theme.currentTextChanged.connect(self._change_theme)
        self.checkbox_enable_sound.toggled.connect(self._enable_disable_sound)

        self.btn_ok.clicked.connect(self._accept)

    def _browse(self) -> None:
        dialog = QFileDialog(directory=self.lineedit_path.text())
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec():
            self.lineedit_path.setText(dialog.selectedFiles()[0])

    def _enable_disable_button(self, text: str) -> None:
        self.btn_ok.setEnabled(bool(text))

    def _change_lang(self, lang: str) -> None:
        self.worker.settings.lang = lang
        self.worker.settings.change_language()

    def _change_theme(self, theme: str) -> None:
        self.worker.settings.theme = theme
        self.worker.settings.change_theme()

    def _enable_disable_sound(self, enabled: bool) -> None:
        if enabled:
            self.worker.sound_manager.play_enable_sound()

        self.worker.settings.enable_sound = enabled

    def _accept(self) -> None:
        if Path(self.get_path()).exists():
            self.accept()
            return

        box = QMessageBox.information(
            self,
            self.worker.settings.tr("dialog:first_run_path_create:title"),
            self.worker.settings.tr("dialog:first_run_path_create:body1") + "<br><br>" + self.worker.settings.tr("dialog:first_run_path_create:body2"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if box == QMessageBox.StandardButton.No:
            return
        
        self.accept()

    def get_path(self) -> str:
        return self.lineedit_path.text()



    def reject(self):
        sys.exit()
        super().reject()




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
        self.setFixedSize(375, 665)

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
        self.btn_console.setToolTip(self.worker.settings.tr("statusbar:console:tooltip"))

        self.btn_about = QToolButton()
        self.btn_about.setIcon(about_icon)
        self.btn_about.setToolTip(self.worker.settings.tr("statusbar:about:tooltip"))

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
        self.btn_console.setToolTip(self.worker.settings.tr("statusbar:console:tooltip"))
        self.btn_about.setToolTip(self.worker.settings.tr("statusbar:about:tooltip"))



    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.state_changed.connect(self._set_status)
        self.worker.error_state.connect(self._append_error_to_status)
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.finished.connect(self._reset_progress_bar)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)
        self.widget_settings.settings_changed.connect(self._apply_asterisk_to_unsaved_settings)

        self.tabs.currentChanged.connect(self._check_settings_have_changed_on_tab_switch)

        self.widget_settings.btn_defualt_receive_path.clicked.connect(self._pass_path_from_settings_to_received)

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
            self.worker.settings.tr("dialog:unsaved_settings:body1") + "<br><br>" + self.worker.settings.tr("dialog:unsaved_settings:body2"),
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Abort | QMessageBox.StandardButton.Ignore,
            QMessageBox.StandardButton.Abort
        )

        # Click the save button for the user
        match box:
            case QMessageBox.StandardButton.Save:
                self.widget_settings.btn_save.click()
            case QMessageBox.StandardButton.Discard:
                self.widget_settings.restore_previous_settings()
            case QMessageBox.StandardButton.Abort:
                self.tabs.blockSignals(True)
                self.tabs.tabBar().setCurrentIndex(2)
                self.tabs.blockSignals(False)
                return
            case _:
                pass

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
        self.widget_send.widget_files.btn_add_files.click()

        if not self.widget_send.are_files_selected():
            return
        
        self.widget_send.widget_files.btn_send.click()

        # Wait a moment before copying the code
        QTimer.singleShot(20, self.widget_send.widget_files.btn_copy_code.click)

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
        self.widget_send.widget_files.btn_add_folders.click()

        if not self.widget_send.are_files_selected():
            return
        
        self.widget_send.widget_files.btn_send.click()

        # Wait a moment before copying the code
        QTimer.singleShot(20, self.widget_send.widget_files.btn_copy_code.click)

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
                self.widget_send.widget_files.btn_send.click()
            case CrocOperation.RECEIVING:
                self.widget_receive.btn_receive.click()
            case _:
                pass

        self.worker.stop()



    def _run_startup_functions(self) -> None:
        """Executes a collection of functions at startup."""

        self._set_status()
        self._show_console()
        self._check_settings_version()
        self._first_run()

    def _show_console(self) -> None:
        """If the user has enabled the setting to start the console on startup, this function will open the console window."""

        if self.worker.settings.startup_console:
            self._window_console.show()



    def _on_progress_update(self, percent: int, filename: str, prefix_word: str) -> None:
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(percent)

        if prefix_word:
            key = f"state:{prefix_word.lower()}"
            prefix = self.worker.settings.tr(key) + " "
        else:
            prefix = ""

        self.progress_bar.setFormat(f"{prefix}{filename}  {percent}%")

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

    def _pass_path_from_settings_to_received(self) -> None:
        text: str = self.widget_settings.lineedit_defualt_receive_path.text()
        if not text:
            QMessageBox.warning(
                self,
                self.worker.settings.tr("dialog:cant_pass_empty_path:title"),
                self.worker.settings.tr("dialog:cant_pass_empty_path:body"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return

        self.tabs.tabBar().setCurrentIndex(1)
        self.widget_receive.lineedit_path.setText(text)



    def closeEvent(self, event):
        """Kills all child windows, stops the worker, and terminates the program. Will prompt the user first if an operation is running."""

        if self.widget_settings.dirty:
            box = QMessageBox.warning(
                self,
                self.worker.settings.tr("dialog:close_warning_settings:title"),
                self.worker.settings.tr("dialog:close_warning_settings:body"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )

            if box == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            
            elif box == QMessageBox.StandardButton.Yes:
                self.worker.settings.save_settings()

        if self._is_operation_running():
            box2 = QMessageBox.warning(
                self,
                self.worker.settings.tr("dialog:close_warning_operation:title"),
                self.worker.settings.tr("dialog:close_warning_operation:body"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if box2 == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
        event.accept()

        self.worker.sound_manager.silence_all()

        self._window_console.close()
        self._window_about.close()
        self.widget_send.window_filelist.close()
        self.worker.stop()
        super().closeEvent(event)

    def _check_settings_version(self) -> None:
        if self.worker.settings.settings_version is None:
            return

        if self.worker.settings.settings_version_baseline <= self.worker.settings.settings_version:
            return

        box = QMessageBox.warning(
            self,
            self.worker.settings.tr("dialog:outdated_settings:title"),
            self.worker.settings.tr("dialog:outdated_settings:body1") + "<br><br>" + self.worker.settings.tr("dialog:outdated_settings:body2"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if box == QMessageBox.StandardButton.No:
            return

        self.worker.settings.set_defaults()

    def _first_run(self) -> None:
        if self.worker.settings.settings_file_path.exists():
            return

        dialog = FirstRunReceivePathDialog(self.worker, self)

        if dialog.exec():
            self.worker.settings.default_receive_path = dialog.get_path()
            self.widget_receive.lineedit_path.setText(dialog.get_path())
            self.widget_settings.lineedit_defualt_receive_path.setText(dialog.get_path())

            self.widget_settings.combo_lang.setCurrentText(dialog.combo_lang.currentText())

            # Block signals so themes like Random don't leapfrog
            self.widget_settings.combo_theme.blockSignals(True)
            self.widget_settings.combo_theme.setCurrentText(dialog.combo_theme.currentText())
            self.widget_settings.combo_theme.blockSignals(False)

            self.widget_settings.checkbox_enable_sound.setChecked(dialog.checkbox_enable_sound.isChecked())

            self.worker.settings.save_settings()
            self.widget_settings.clear_dirty()