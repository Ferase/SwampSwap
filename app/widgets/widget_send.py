import os
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QCheckBox,
    QGroupBox, QFileDialog, QTextEdit, QAbstractItemView,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir
from PyQt6.QtGui import QFont

import app.utils as app_utils
from app.enums import CrocState, CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker



class SendWidget(QWidget):

    file_selected = pyqtSignal(list)
    dropped_files = pyqtSignal(list)

    output_line = pyqtSignal(str)
    operation_running = pyqtSignal(bool)
    send_complete = pyqtSignal(str)

    # Init
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.selected_file_folders: list[Path] | None = None

        self.worker: CrocWorker = worker

        # Build UI
        self._build_central()

        self._connect_signals()

    # Construct the UI
    def _build_central(self) -> None:
        # Create box layout container
        root = QVBoxLayout(self)
        root.setSpacing(8)

        file_group = self._build_file_group()
        controls_group = self._build_controls_group()

        # Add widgets to box layout
        root.addWidget(file_group)
        root.addWidget(controls_group)

    # Construct file group
    def _build_file_group(self) -> QGroupBox:
        group = app_utils.QGroupBoxFileDrop()
        group.files_dropped.connect(self.dropped_files.emit)
        layout = QGridLayout(group)

        bold_font = QFont()
        bold_font.setBold(True)

        self.btn_browse_file = QPushButton(self.worker.settings.tr("send:btn:select_files"))
        self.btn_browse_file.setMinimumHeight(48)

        self.btn_browse_folder = QPushButton(self.worker.settings.tr("send:btn:select_folders"))
        self.btn_browse_folder.setMinimumHeight(48)

        self.btn_clear_selected_file_folder = QPushButton(self.worker.settings.tr("send:btn:clear_selection"))
        self.btn_clear_selected_file_folder.setEnabled(False)

        self.label_selected_file_folder = QLabel(self.worker.settings.tr("send:label:no_selection"))
        self.label_selected_file_folder.setFont(bold_font)
        self.label_selected_file_folder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_selected_file_folder.setStyleSheet("padding-top: 5px;")

        self.label_selected_file_folder_desc = QLabel(self.worker.settings.tr("send:label:please_select"))
        self.label_selected_file_folder_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.btn_browse_file, 0, 0)
        layout.addWidget(self.btn_browse_folder, 0, 1)
        layout.addWidget(self.btn_clear_selected_file_folder, 1, 0, 1, -1)
        layout.addWidget(self.label_selected_file_folder, 2, 0, 1, -1)
        layout.addWidget(self.label_selected_file_folder_desc, 3, 0, 1, -1)

        return group
    
    # Send controls
    def _build_controls_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.btn_send = QPushButton(self.worker.settings.tr("generic:send"))
        self.btn_send.setMinimumHeight(80)
        self.btn_send.setEnabled(False)
        font = self.btn_send.font()
        font.setPointSize(24)
        self.btn_send.setFont(font)

        self.lineedit_code = QLineEdit()
        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("send:lineedit:placeholder_code"))
        self.lineedit_code.setReadOnly(True)
        self.lineedit_code.setEnabled(False)

        self.btn_copy_code = QPushButton(self.worker.settings.tr("send:btn:copy_code"))
        self.btn_copy_code.setEnabled(False)

        layout.addWidget(self.btn_send)
        layout.addWidget(self.lineedit_code)
        layout.addWidget(self.btn_copy_code)

        return group
    


    def _retranslate(self) -> None:
        self.btn_browse_file.setText(self.worker.settings.tr("send:btn:select_files"))
        self.btn_browse_folder.setText(self.worker.settings.tr("send:btn:select_folders"))
        self.btn_clear_selected_file_folder.setText(self.worker.settings.tr("send:btn:clear_selection"))

        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("send:lineedit:placeholder_code"))
        self.btn_copy_code.setText(self.worker.settings.tr("send:btn:copy_code"))

        self._set_button_text_by_operation()
        self._update_selected_file_ui(self.selected_file_folders)
    


    def _connect_signals(self) -> None:
        self.worker.state_changed.connect(self._state_responses)
        self.worker.line_received.connect(self._read_command_line)
        self.worker.finished.connect(self._on_finish)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.file_selected.connect(self._update_selected_file_ui)
        self.dropped_files.connect(self._set_selected_files)

        self.lineedit_code.textChanged.connect(self._enable_copy_code_button)

        self.btn_browse_file.clicked.connect(self._click_browse_file_button)
        self.btn_browse_folder.clicked.connect(self._click_browse_folder_button)
        self.btn_clear_selected_file_folder.clicked.connect(self._click_clear_button)
        self.btn_copy_code.clicked.connect(self._copy_code)
        self.btn_send.clicked.connect(self._click_send_button)

    def _set_button_text_by_operation(self) -> None:
        match self.worker.state.operation:
            case CrocOperation.SENDING:
                self.btn_send.setText(self.worker.settings.tr("generic:cancel"))
            case _:
                self.btn_send.setText(self.worker.settings.tr("generic:send"))

    def _determine_main_button_behavior(self) -> None:
        if self.worker.state.operation == CrocOperation.RECEIVING or self.selected_file_folders is None:
            self.btn_send.setEnabled(False)
            return
        elif self.selected_file_folders is not None:
            self.btn_send.setEnabled(True)

        is_sending: bool = self.worker.state.action not in [CrocAction.NONE, CrocAction.COMPLETED, CrocAction.CANCELLED, CrocAction.ERROR]
        self._set_button_text_by_operation()
        self.lineedit_code.setEnabled(is_sending)

    def _determine_selected_files(self, paths: list[Path]) -> str:
        # Init file/folder count
        file_count: int = 0
        folder_count: int = 0

        for path in paths:
            # Add sums to total
            if path.is_dir():
                file_count += sum(1 for item in path.rglob("*") if item.is_file())
                folder_count += sum(1 for item in path.rglob("*") if item.is_dir()) + 1
            else:
                file_count += 1

        file_text: str = self._determine_selected_files_text("file", file_count)
        folder_text: str = self._determine_selected_files_text("folder", folder_count)

        if file_text and folder_text:
            return f"{file_text}, {folder_text}"
        
        return folder_text if folder_text else file_text

    def _determine_selected_files_text(self, target: str, count: int) -> str:
        if count <= 0:
            return ""
        
        count_text: str = format(count, ",")
        
        if count == 1:
            return self.worker.settings.tr(f"template:num_{target}_single").format(n=count_text)
        else:
            return self.worker.settings.tr(f"template:num_{target}s_multiple").format(n=count_text)
    
    def _read_command_line(self, line: str) -> None:
        self._test_for_code(line)

    def _test_for_code(self, line: str) -> None:
        match = re.search(r"Code is:\s*(.+)", line, re.IGNORECASE)
        if match:
            self.lineedit_code.setText(match.group(1).strip())

    def are_files_selected(self) -> bool:
        return bool(self.selected_file_folders)

    def _state_responses(self) -> None:
        self._determine_main_button_behavior()

    def _on_finish(self, code: int) -> None:
        if self.are_files_selected():
            self.btn_send.setEnabled(True)

    def _paths_list_to_string(self, paths: list[Path]) -> str:
        return "\n".join([str(path) + os.sep + "*" if path.is_dir() else str(path) for path in paths])
    
    def _reset_selected_fies_folders(self) -> None:
        self.selected_file_folders = None
        self._update_selected_file_ui()

    def _set_selected_files(self, selected: list[str]):
        self.selected_file_folders = [Path(path) for path in selected]
        self.file_selected.emit(self.selected_file_folders)



    def _update_selected_file_ui(self, paths: list[Path] | None = None) -> None:
        if paths is None:
            self.label_selected_file_folder.setText(self.worker.settings.tr("send:label:no_selection"))
            self.label_selected_file_folder_desc.setText(self.worker.settings.tr("send:label:please_select"))
            self.label_selected_file_folder.setToolTip(None)
            self.label_selected_file_folder_desc.setToolTip(None)
            self.btn_clear_selected_file_folder.setEnabled(False)
            self._determine_main_button_behavior()
            return
        
        file_name: str = ""
        if len(paths) == 1:
            file_name = paths[0].name + ("/*" if paths[0].is_dir() else "")
        else:
            file_name = self.worker.settings.tr("send:label:multiple_files")

        self.label_selected_file_folder.setText(file_name)

        paths_string: str = self._paths_list_to_string(paths)
        self.label_selected_file_folder.setToolTip(paths_string)
        self.label_selected_file_folder_desc.setToolTip(paths_string)

        found_files_text: str = self._determine_selected_files(paths)
        self.label_selected_file_folder_desc.setText(found_files_text)

        self.btn_clear_selected_file_folder.setEnabled(True)
        self._determine_main_button_behavior()

    def _enable_copy_code_button(self, text: str) -> None:
        self.btn_copy_code.setEnabled(bool(text))

    def _copy_code(self) -> None:
        QApplication.clipboard().setText(self.lineedit_code.text())



    def _click_browse_file_button(self) -> None:
        dialog = app_utils.QFileDialog(
            self,
            self.worker.settings.tr("file_dialog:choose_files")
        )

        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if not dialog.exec():
            return
        
        selected_files: list[str] = dialog.selectedFiles()
        self.dropped_files.emit(selected_files)

    def _click_browse_folder_button(self) -> None:
        dialog = app_utils.MultiFolderDialog(
            self,
            self.worker.settings.tr("file_dialog:choose_folders")
        )

        if not dialog.exec():
            return
        
        selected_folders: list[str] = dialog.selectedFiles()
        self.dropped_files.emit(selected_folders)

    def _click_clear_button(self) -> None:
        self._reset_selected_fies_folders()

    def _click_send_button(self) -> None:
        if self.selected_file_folders is None:
            return
        
        is_active = self.worker.state.action not in (
            CrocAction.NONE,
            CrocAction.COMPLETED,
            CrocAction.CANCELLED,
            CrocAction.ERROR,
        )

        # Button is in cancel mode
        if is_active:
            self.worker.stop()
            return

        self.worker.start_send(self.selected_file_folders)