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
from PyQt6.QtCore import Qt, pyqtSignal

import app.utils as app_utils
from app.enums import CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.widgets.tabs.widget_send import SendWidget
from app.widgets.tabs.widget_receive import ReceiveWidget
from app.widgets.tabs.widget_settings import SettingsWidget
from app.windows.window_console import ConsoleWindow
from app.windows.window_about import AboutWindow



class FirstRunReceivePathDialog(QDialog):

    verified_changed = pyqtSignal(bool)

    def __init__(self, worker: CrocWorker, parent=None):
        super().__init__(parent)

        self.worker = worker

        self.setWindowTitle(self.worker.settings.tr("firstrun:window:title"))
        self.setFixedSize(500, 375)

        self._build_central()
        self._connect_signals()

    def _build_central(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        croc_group = self._build_croc()
        main_group = self._build_main()
        buttons_group = self._build_buttons()

        root.addWidget(croc_group)
        root.addWidget(main_group)
        root.addWidget(buttons_group)

    def _build_croc(self) -> QGroupBox:
        self.croc_group = QGroupBox(self.worker.settings.tr("firstrun:group:find_croc"))
        layout = QVBoxLayout(self.croc_group)

        self.checkbox_use_system_croc = QCheckBox(self.worker.settings.tr("options:use_system_croc:label"))
        self._set_use_system_croc_enabled()

        layout.addWidget(self.checkbox_use_system_croc)

        return self.croc_group

    def _build_main(self) -> QGroupBox:
        self.main_group = QGroupBox(self.worker.settings.tr("firstrun:group:set_settings"))
        layout = QVBoxLayout(self.main_group)

        self.label_receive_path = QLabel(self.worker.settings.tr("options:default_receive_path:label"))
        self.label_receive_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))

        path_row = QHBoxLayout()
        self.lineedit_receive_path = QLineEdit()
        self.lineedit_receive_path.setText(self.worker.settings.default_receive_path)
        self.lineedit_receive_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))

        self.btn_receive_path_browse = QPushButton(self.worker.settings.tr("generic:browse"))

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

        layout.addWidget(self.label_receive_path)

        layout.addLayout(path_row)
        path_row.addWidget(self.lineedit_receive_path)
        path_row.addWidget(self.btn_receive_path_browse)

        layout.addStretch()

        layout.addWidget(self.checkbox_enable_sound)

        layout.addStretch()

        return self.main_group

    def _build_buttons(self) -> None:
        self.buttons_group = QGroupBox()
        layout = QHBoxLayout(self.buttons_group)

        self.btn_ok = QPushButton(self.worker.settings.tr("generic:ok"))

        layout.addStretch()
        layout.addWidget(self.btn_ok)

        return self.buttons_group

    def _retranslate(self) -> None:
        self.setWindowTitle(self.worker.settings.tr("firstrun:window:title"))
        self.croc_group.setTitle(self.worker.settings.tr("firstrun:group:find_croc"))
        self.main_group.setTitle(self.worker.settings.tr("firstrun:group:set_settings"))

        self.checkbox_use_system_croc.setText(self.worker.settings.tr("options:use_system_croc:label"))
        self._set_use_system_croc_enabled()
        
        self.lineedit_croc_path.setToolTip(self.worker.settings.tr("options:croc_path:tooltip"))
        self.btn_croc_path_browse.setText(self.worker.settings.tr("generic:browse"))
        self.btn_verify_croc.setText(self.worker.settings.tr("detect_croc:btn:verify"))
        self._draw_croc_status()
        self._populate_croc_detection_methods()
        
        self.label_receive_path.setText(self.worker.settings.tr("options:default_receive_path:label"))
        self.label_receive_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))
        self.lineedit_receive_path.setToolTip(self.worker.settings.tr("options:default_receive_path:tooltip"))
        self.btn_receive_path_browse.setText(self.worker.settings.tr("generic:browse"))

        self.label_lang.setText(self.worker.settings.tr("options:language:label"))
        self.label_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))
        self.label_theme.setText(self.worker.settings.tr("options:theme:label"))
        self.label_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))

        self.checkbox_enable_sound.setText(self.worker.settings.tr("options:enable_sound:label"))
        self.checkbox_enable_sound.setToolTip(self.worker.settings.tr("options:enable_sound:tooltip"))

        self.btn_ok.setText(self.worker.settings.tr("generic:ok"))

    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.checkbox_use_system_croc.toggled.connect(self._handle_switch_croc_version)

        self.btn_receive_path_browse.clicked.connect(self._browse_for_receive)
        self.lineedit_receive_path.textChanged.connect(self._enable_disable_button)

        self.combo_lang.currentTextChanged.connect(self._change_lang)
        self.combo_theme.currentTextChanged.connect(self._change_theme)
        self.checkbox_enable_sound.toggled.connect(self._enable_disable_sound)

        self.btn_ok.clicked.connect(self._accept)

    def _browse_for_receive(self) -> None:
        dialog = QFileDialog(directory=self.lineedit_receive_path.text())
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec():
            self.lineedit_receive_path.setText(dialog.selectedFiles()[0])

    def _enable_disable_button(self) -> None:
        self.btn_ok.setEnabled(bool(self.lineedit_receive_path.text()))

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



    def _set_use_system_croc_enabled(self) -> None:
        system_croc_available: bool = self.worker.is_system_croc_installed()

        self.checkbox_use_system_croc.setEnabled(system_croc_available)

        text_key: str = "options:use_system_croc:tooltip"
        if not system_croc_available:
            text_key += ":disabled"

        self.checkbox_use_system_croc.setToolTip(self.worker.settings.tr(text_key))

        if system_croc_available:
            self.checkbox_use_system_croc.setChecked(self.worker.settings.use_system_croc)

    def _handle_switch_croc_version(self, checked: bool) -> None:
        self.worker.settings.use_system_croc = checked

        if checked:
            version_test: str | None = self.worker.get_croc_version_number_only()
            if version_test is None:
                QMessageBox.critical(
                    self,
                    self.worker.settings.tr("dialog:croc_not_on_system:title"),
                    self.worker.settings.tr("dialog:croc_not_on_system:body"),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok
                )
                self.checkbox_use_system_croc.setChecked(False)
                self.worker.settings.use_system_croc = False

            if not self.worker.is_croc_version_greater_than_minimum():
                QMessageBox.critical(
                    self,
                    self.worker.settings.tr("dialog:system_croc_too_old:title"),
                    "<br><br>".join([
                        self.worker.settings.tr("dialog:system_croc_too_old:body1").format(
                            v1=f"<b>{version_test}</b>",
                            v2=f"<b>{self.worker.minimum_croc_version}</b>"
                        ),
                        self.worker.settings.tr("dialog:system_croc_too_old:body2")
                    ]),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok
                )
                self.checkbox_use_system_croc.setChecked(False)
                self.worker.settings.use_system_croc = False

            QMessageBox.information(
                self,
                self.worker.settings.tr("dialog:switched_to_system_croc:title"),
                self.worker.settings.tr("dialog:switched_to_system_croc:body"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )

            self.worker.settings.save_single_setting("use_system_croc", self.worker.settings.use_system_croc)
            return

        QMessageBox.information(
            self,
            self.worker.settings.tr("dialog:switched_to_bundled_croc:title"),
            self.worker.settings.tr("dialog:switched_to_bundled_croc:body"),
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )

        self.worker.settings.save_single_setting("use_system_croc", self.worker.settings.use_system_croc)



    def _accept(self) -> None:
        if Path(self.get_path()).exists():
            self.accept()
            return

        try:
            Path(self.get_path()).mkdir(exist_ok=True)
        except (OSError, FileNotFoundError):
            QMessageBox.critical(
                self,
                self.worker.settings.tr("dialog:first_run_path_not_valid:title"),
                "<br><br>".join([
                    self.worker.settings.tr("dialog:first_run_path_not_valid:body1"),format(p=f"<b>{self.lineedit_receive_path.text()}</b>"),
                    self.worker.settings.tr("dialog:first_run_path_not_valid:body2")
                ]),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return

        box = QMessageBox.information(
            self,
            self.worker.settings.tr("dialog:first_run_path_create:title"),
            "<br><br>".join([
                self.worker.settings.tr("dialog:first_run_path_create:body1").format(p=f"<b>{self.get_path()}</b>"),
                self.worker.settings.tr("dialog:first_run_path_create:body2")
            ]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if box == QMessageBox.StandardButton.No:
            return
        
        self.accept()

    def get_path(self) -> str:
        return self.lineedit_receive_path.text()



    def reject(self):
        sys.exit()
        super().reject()