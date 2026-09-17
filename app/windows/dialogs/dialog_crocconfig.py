import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QMessageBox, QLabel, QVBoxLayout, QGroupBox,
    QDialog, QHBoxLayout, QLineEdit, QPushButton,
    QFileDialog
)
from PyQt6.QtCore import pyqtSignal

import app.utils as app_utils
from app.workers.worker_croc import CrocWorker



class ConfigureCrocDialog(QDialog):

    verified_changed = pyqtSignal(bool)

    def __init__(self, worker: CrocWorker, parent=None):
        super().__init__(parent)

        self.worker = worker

        self.verified: bool = False

        self.setWindowTitle(self.worker.settings.tr("detect_croc:window:title"))
        self.setFixedSize(500, 250)

        self._build_central()
        self._get_current_status()
        self._connect_signals()

    def _build_central(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        croc_group = self._build_croc()
        buttons_group = self._build_buttons()

        root.addWidget(croc_group)
        root.addWidget(buttons_group)

    def _build_croc(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.label_croc_exists = QLabel()
        self._draw_croc_status()

        self.combo_croc_method = app_utils.BoundedComboBox()
        self.combo_croc_method.setToolTip(self.worker.settings.tr("detect_croc:combo:tooltip"))
        self._populate_croc_detection_methods()

        path_row = QHBoxLayout()
        self.lineedit_croc_path = QLineEdit()
        self.lineedit_croc_path.setToolTip(self.worker.settings.tr("detect_croc:lineedit:tooltip"))
        self.lineedit_croc_path.setDisabled(True)

        self.btn_croc_path_browse = QPushButton(self.worker.settings.tr("generic:browse"))
        self.btn_croc_path_browse.setDisabled(True)

        self.btn_verify_croc = QPushButton(self.worker.settings.tr("detect_croc:btn:verify"))

        layout.addWidget(self.label_croc_exists)
        layout.addWidget(self.combo_croc_method)

        layout.addLayout(path_row)
        path_row.addWidget(self.lineedit_croc_path)
        path_row.addWidget(self.btn_croc_path_browse)

        layout.addWidget(self.btn_verify_croc)

        return group

    def _build_buttons(self) -> None:
        self.buttons_group = QGroupBox()
        layout = QHBoxLayout(self.buttons_group)

        self.btn_ok = QPushButton(self.worker.settings.tr("generic:ok"))
        self.btn_ok.setDisabled(True)

        self.btn_cancel = QPushButton(self.worker.settings.tr("generic:cancel"))

        layout.addStretch()
        layout.addWidget(self.btn_ok)
        layout.addWidget(self.btn_cancel)

        return self.buttons_group

    def _draw_croc_status(self) -> None:
        self.label_croc_exists.setToolTip(None)

        status: str = self.worker.settings.tr("detect_croc:label:croc_exists_no")
        if self.verified:
            suffix: str = "PATH"
            if self._user_wants_standalone_croc():
                suffix = self.get_croc_path()
                self.label_croc_exists.setToolTip(suffix)

            status = self.worker.settings.tr("detect_croc:label:croc_exists_yes").format(p=f"<b>{suffix}</b>")

        self.label_croc_exists.setText(" ".join([
            self.worker.settings.tr("detect_croc:label:croc_exists"),
            status
        ]))

    def _retranslate(self) -> None:
        self.setWindowTitle(self.worker.settings.tr("detect_croc:window:title"))
        
        self.lineedit_croc_path.setToolTip(self.worker.settings.tr("options:croc_path:tooltip"))
        self.btn_croc_path_browse.setText(self.worker.settings.tr("generic:browse"))
        self.btn_verify_croc.setText(self.worker.settings.tr("detect_croc:btn:verify"))
        self._draw_croc_status()
        self._populate_croc_detection_methods()

        self.btn_ok.setText(self.worker.settings.tr("generic:ok"))

    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.combo_croc_method.currentIndexChanged.connect(self._change_croc_detect_method)
        self.btn_croc_path_browse.clicked.connect(self._browse_for_croc)
        self.verified_changed.connect(self._verified_status_changed)
        self.btn_verify_croc.clicked.connect(self._verify)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def _browse_for_receive(self) -> None:
        dialog = QFileDialog(directory=self.lineedit_receive_path.text())
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec():
            self.lineedit_receive_path.setText(dialog.selectedFiles()[0])

    def _enable_disable_button(self) -> None:
        croc_path_bool: bool = self.checkbox_use_evar.isChecked()
        croc_path_xor: bool = croc_path_bool or bool(self.get_croc_path())

        all_text: bool = all([
            croc_path_xor,
            self.lineedit_receive_path.text()
        ])

        print(all_text)

        self.btn_ok.setEnabled(all_text)

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



    def _user_wants_standalone_croc(self):
        return self.combo_croc_method.currentIndex() == 1

    def _does_croc_exist(self) -> bool:
        """Checks whether croc exists on the system PATH/at the specicified file, depending on the user's choice."""

        # If the user wants to use a standalone croc EXXE
        if self._user_wants_standalone_croc():
            path = Path(self.get_croc_path())

            # If the croc EXE doesn't exist
            if not path.exists():
                QMessageBox.critical(
                    self,
                    self.worker.settings.tr("dialog:detect_croc_path_not_exist:title"),
                    self.worker.settings.tr("dialog:detect_croc_path_not_exist:body"),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok
                )
                return False

            # Attempt to get the version from the specified croc EXE
            version_poke: str | None = self.worker.get_croc_version_from_path(path)

            # The EXE did not return a croc version
            if version_poke is None:
                QMessageBox.critical(
                    self,
                    self.worker.settings.tr("dialog:detect_croc_path_is_not_croc:title"),
                    self.worker.settings.tr("dialog:detect_croc_path_is_not_croc:body"),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok
                )
                return False

            # The EXE is a valid croc EXE
            return True

        # Poke croc on the system PATH
        is_croc_on_path: bool = self.worker.get_croc_version_from_path_number_only("croc")

        # croc doesn't exist on the system PATH or somehow the croc on the PATH isn't croc
        if not is_croc_on_path:
            QMessageBox.critical(
                self,
                self.worker.settings.tr("dialog:detect_croc_path_not_on_path:title"),
                self.worker.settings.tr("dialog:detect_croc_path_not_on_path:body"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return False

        # croc was found on the system PATH
        return True

    def _verify(self) -> None:
        """Using the selected detection method and the user's system PATH/specified croc EXE path, the croc application will be checekd to be sure it exists and up to date."""

        # Check that croc exists on the system PATH/at the location specified by the user
        croc_found: bool = self._does_croc_exist()
        if not croc_found:
            return

        # If the user wants to use a standalone croc EXE
        if self._user_wants_standalone_croc():
            # If the standalone croc EXE is an odler version than Swamp Swap's minimum
            if not self.worker.is_croc_version_at_path_greater_than_minimum(self.get_croc_path()):
                QMessageBox.critical(
                    self,
                    self.worker.settings.tr("dialog:detect_croc_path_found_too_old:title"),
                    "<br><br>".join([
                        self.worker.settings.tr("dialog:detect_croc_path_found_too_old_standalone:body1").format(p=self.get_croc_path(), v1=f"<b>v{self.worker.get_croc_version_from_path_number_only(self.get_croc_path())}</b>", v2=f"<b>v{self.worker.minimum_croc_version}</b>"),
                        self.worker.settings.tr("dialog:detect_croc_path_found_too_old_standalone:body2")
                    ]),
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok
                )
                return

            # A valid croc EXE was found at the specified path
            QMessageBox.information(
                self,
                self.worker.settings.tr("dialog:detect_croc_path_found_standalone:title"),
                self.worker.settings.tr("dialog:detect_croc_path_found_standalone:body").format(p=f"<b>{self.get_croc_path()}</b>"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )

            # croc has been verified
            self.verified_changed.emit(True)
            return

        # croc on the system PATH has a version older than the minimum
        if not self.worker.is_croc_version_at_path_greater_than_minimum("croc"):
            QMessageBox.critical(
                self,
                self.worker.settings.tr("dialog:detect_croc_path_found_too_old:title"),
                "<br><br>".join([
                    self.worker.settings.tr("dialog:detect_croc_path_found_too_old_path:body1").format(v1=f"<b>v{self.worker.get_croc_version_from_path_number_only("croc")}</b>", v2=f"<b>v{self.worker.minimum_croc_version}</b>"),
                    self.worker.settings.tr("dialog:detect_croc_path_found_too_old_path:body2")
                ]),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return

        # croc was found on the system PATH
        QMessageBox.information(
            self,
            self.worker.settings.tr("dialog:detect_croc_path_found_on_path:title"),
            self.worker.settings.tr("dialog:detect_croc_path_found_on_path:body"),
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )

        # croc has been verified
        self.verified_changed.emit(True)
        return

    def _change_croc_detect_method(self, index: int) -> None:
        self.lineedit_croc_path.setEnabled(bool(max(index, 0)))
        self.btn_croc_path_browse.setEnabled(bool(max(index, 0)))
        self.verified_changed.emit(False)

    def _verified_status_changed(self, status: bool) -> None:
        self.verified = status
        self.btn_ok.setEnabled(status)
        self._draw_croc_status()

        if status:
            if self._user_wants_standalone_croc():
                self.worker.settings.croc_path = self.get_croc_path()
            else:
                self.worker.settings.croc_path = "croc"

    def _browse_for_croc(self) -> None:
        dialog = QFileDialog(self)
        dialog.setWindowTitle(self.worker.settings.tr(""))
        
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        
        if sys.platform == "win32":
            dialog.setNameFilter("Executables (*.exe)")
        else:
            dialog.setNameFilter("All Files (*)")
            
        if dialog.exec():
            files = dialog.selectedFiles()

            if not files:
                return

            self.lineedit_croc_path.setText(files[0])

    def _populate_croc_detection_methods(self) -> None:
        selected_index: int = self.combo_croc_method.currentIndex()

        try:
            self.verified_changed.disconnect(self._verified_status_changed)
        except TypeError:
            pass

        self.combo_croc_method.clear()
        self.combo_croc_method.addItems([
            self.worker.settings.tr("detect_croc:combo:system"),
            self.worker.settings.tr("detect_croc:combo:standalone")
        ])

        self.combo_croc_method.setCurrentIndex(max(selected_index, 0))
        
        self.verified_changed.connect(self._verified_status_changed)

    def get_path(self) -> str:
        return self.lineedit_receive_path.text()

    def get_croc_path(self) -> str:
        return self.lineedit_croc_path.text()

    def get_final_croc_path(self) -> str:
        if self._user_wants_standalone_croc():
            return self.get_croc_path()

        return "croc"

    def _get_current_status(self) -> None:
        is_standalone: bool = self.worker.settings.croc_path != "croc"

        if is_standalone:
            self.combo_croc_method.setCurrentIndex(1)
            self.lineedit_croc_path.setText(self.worker.settings.croc_path)

        self.lineedit_croc_path.setEnabled(is_standalone)
        self.btn_croc_path_browse.setEnabled(is_standalone)

        version: str | None = self.worker.get_croc_version_from_path(self.worker.settings.croc_path)

        if version is None:
            return

        self.verified_changed.emit(True)