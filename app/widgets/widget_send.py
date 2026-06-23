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

    file_selected = pyqtSignal(Path)

    output_line = pyqtSignal(str)
    operation_running = pyqtSignal(bool)
    send_complete = pyqtSignal(str)

    # Init
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.selected_file_folder: Path | None = None

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
        group = QGroupBox()
        layout = QGridLayout(group)

        bold_font = QFont()
        bold_font.setBold(True)

        self.btn_browse_file = QPushButton(self.worker.settings.tr("send:btn:select_file"))
        self.btn_browse_file.setMinimumHeight(48)

        self.btn_browse_folder = QPushButton(self.worker.settings.tr("send:btn:select_folder"))
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
        self.btn_send.setStyleSheet("font-size: 24pt;")

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
        self.btn_browse_file.setText(self.worker.settings.tr("send:btn:select_file"))
        self.btn_browse_folder.setText(self.worker.settings.tr("send:btn:select_folder"))
        self.btn_clear_selected_file_folder.setText(self.worker.settings.tr("send:btn:clear_selection"))

        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("send:lineedit:placeholder_code"))
        self.btn_copy_code.setText(self.worker.settings.tr("send:btn:copy_code"))

        self._set_button_text_by_operation()
        self._update_selected_file_ui(self.selected_file_folder)
    


    def _connect_signals(self) -> None:
        self.worker.state_changed.connect(self._state_responses)
        self.worker.line_received.connect(self._read_command_line)
        self.worker.finished.connect(self._on_finish)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.file_selected.connect(self._update_selected_file_ui)

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
        if self.worker.state.operation == CrocOperation.RECEIVING or self.selected_file_folder is None:
            self.btn_send.setEnabled(False)
            return
        elif self.selected_file_folder is not None:
            self.btn_send.setEnabled(True)

        is_sending: bool = self.worker.state.action not in [CrocAction.NONE, CrocAction.COMPLETED, CrocAction.CANCELLED, CrocAction.ERROR]
        self._set_button_text_by_operation()
        self.lineedit_code.setEnabled(is_sending)

    def _determine_selected_files(self, path: Path) -> str:
        if not path.is_dir():
            return "1 file"

        file_count = sum(1 for item in path.iterdir() if item.is_file())
        folder_count = sum(1 for item in path.iterdir() if item.is_dir())

        folder_text: str = self.worker.settings.tr("generic:folder_single") if folder_count == 1 else self.worker.settings.tr("generic:folder_plural")
        file_text: str = self.worker.settings.tr("generic:file_single") if folder_count == 1 else self.worker.settings.tr("generic:file_plural")

        return f"{folder_count} {folder_text}, {file_count} {file_text}"
    
    def _read_command_line(self, line: str) -> None:
        self._test_for_code(line)

    def _test_for_code(self, line: str) -> None:
        match = re.search(r"Code is:\s*(.+)", line, re.IGNORECASE)
        if match:
            self.lineedit_code.setText(match.group(1).strip())

    def is_file_selected(self) -> bool:
        return bool(self.selected_file_folder)

    def _state_responses(self) -> None:
        self._determine_main_button_behavior()

    def _on_finish(self, code: int) -> None:
        if self.is_file_selected():
            self.btn_send.setEnabled(True)
    


    def _update_selected_file_ui(self, path: Path | None = None) -> None:
        if path is None:
            self.label_selected_file_folder.setText(self.worker.settings.tr("send:label:no_selection"))
            self.label_selected_file_folder_desc.setText(self.worker.settings.tr("send:label:please_select"))
            self.label_selected_file_folder.setToolTip(None)
            self.btn_clear_selected_file_folder.setEnabled(False)
            self._determine_main_button_behavior()
            return

        file_name: str = path.name + ("/*" if path.is_dir() else "")
        self.label_selected_file_folder.setText(file_name)
        self.label_selected_file_folder.setToolTip(str(path))
        found_files_text: str = self._determine_selected_files(path)

        self.label_selected_file_folder_desc.setText(found_files_text)
        self.btn_clear_selected_file_folder.setEnabled(True)
        self._determine_main_button_behavior()

    def _enable_copy_code_button(self, text: str) -> None:
        self.btn_copy_code.setEnabled(bool(text))

    def _copy_code(self) -> None:
        QApplication.clipboard().setText(self.lineedit_code.text())



    def _click_browse_file_button(self) -> None:
        dialog = QFileDialog()

        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if dialog.exec():
            self.selected_file_folder = Path(dialog.selectedFiles()[0])
            self.file_selected.emit(self.selected_file_folder)
        else:
            self.selected_file_folder = None
            self._update_selected_file_ui()

    def _click_browse_folder_button(self) -> None:
        dialog = QFileDialog()

        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec():
            self.selected_file_folder = Path(dialog.selectedFiles()[0])
            self.file_selected.emit(self.selected_file_folder)

    def _click_clear_button(self) -> None:
        self.selected_file_folder = None
        self._update_selected_file_ui()

    def _click_send_button(self) -> None:
        if self.selected_file_folder is None:
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

        self.worker.start_send(self.selected_file_folder)