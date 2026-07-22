from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QGroupBox, QFileDialog, QApplication, QMessageBox,
    QDialog, QTextEdit, QHBoxLayout, QLabel
)
from PyQt6.QtCore import pyqtSignal, QRegularExpression

import app.utils as app_utils
from app.enums import CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker

_ACCEPT_RE = QRegularExpression(r"Accept\s+(?:'(?P<filename>[^']+)'|(?P<count>\d+\s+files?(?:\s+and\s+\d+\s+folders?)?))\s*\((?P<size>[^)]+)\)\?")
_DISPLAY_TEXT_RE = QRegularExpression(r"Display text message\s+\((?P<size>[^)]+)\)\?")
_RECEIVING_RE = QRegularExpression(r"Receiving \(<-")



class ReceiveTextDialog(QDialog):
    def __init__(self, text: str, worker: CrocWorker, parent=None):
        super().__init__(parent)

        self.worker = worker

        self.setWindowTitle(self.worker.settings.tr("dialog:displaying_sent_text:title"))
        self.setFixedSize(600, 300)

        self._text: str = text

        self._build_central()
        self._connect_signals()

    def _build_central(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        self.label_display_text = QLabel(self.worker.settings.tr("dialog:displaying_sent_text:body1") + "<br>" + self.worker.settings.tr("dialog:displaying_sent_text:body2"))

        self.textedit_display_text = QTextEdit()
        self.textedit_display_text.setText(self._text)
        self.textedit_display_text.setReadOnly(True)

        self.btn_copy_text = QPushButton(self.worker.settings.tr("dialog:displaying_sent_text:copy_text"))

        btn_row = QHBoxLayout()

        self.btn_close = QPushButton(self.worker.settings.tr("generic:close"))

        root.addWidget(self.label_display_text)
        root.addWidget(self.textedit_display_text)
        root.addWidget(self.btn_copy_text)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_close)

        root.addLayout(btn_row)

    def _connect_signals(self) -> None:
        self.btn_close.clicked.connect(self.accept)
        self.btn_copy_text.clicked.connect(self._copy_text)

    def _copy_text(self) -> None:
        QApplication.clipboard().setText(self._text)



class ReceiveWidget(QWidget):

    output_line = pyqtSignal(str)
    operation_running = pyqtSignal(bool)
    send_complete = pyqtSignal(str)

    # Init
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self._is_text_transfer: bool = False
        self._text_content_lines: list[str] = []

        self._output_path: str | None = None
        self._code: str | None = None

        self.worker: CrocWorker = worker

        # Build UI
        self._build_central()

        self._connect_signals()

    # Construct the UI
    def _build_central(self) -> None:
        # Create box layout container
        root = QVBoxLayout(self)
        root.setSpacing(8)

        output_group = self._build_output_group()
        controls_group = self._build_controls_group()

        # Add widgets to box layout
        root.addWidget(output_group)
        root.addWidget(controls_group)

    # Construct file group
    def _build_output_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.lineedit_path = QLineEdit()
        self.lineedit_path.setPlaceholderText(self.worker.settings.tr("receive:lineedit:placeholder_path"))
        self.lineedit_path.setText(self._get_default_path())
        self._update_path_tooltip()

        self.btn_open_output_path = QPushButton(self.worker.settings.tr("receive:btn:open_output_folder"))

        self.btn_browse_output_folder = QPushButton(self.worker.settings.tr("receive:btn:select_folder"))
        self.btn_browse_output_folder.setMinimumHeight(50)

        self.btn_default_path = QPushButton(self.worker.settings.tr("receive:btn:default_folder"))
        self.btn_default_path.setMinimumHeight(50)

        layout.addWidget(self.lineedit_path)
        layout.addWidget(self.btn_open_output_path)
        layout.addStretch()
        layout.addWidget(self.btn_browse_output_folder, stretch=1)
        layout.addWidget(self.btn_default_path, stretch=1)

        return group
    
    # Send controls
    def _build_controls_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.lineedit_code = QLineEdit()
        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("receive:lineedit:placeholder_code"))

        self.btn_paste_code = QPushButton(self.worker.settings.tr("receive:btn:paste_code"))

        self.btn_receive = QPushButton(self.worker.settings.tr("generic:receive"))
        self.btn_receive.setMinimumHeight(60)
        self.btn_receive.setEnabled(False)
        font = self.btn_receive.font()
        font.setPointSize(24)
        self.btn_receive.setFont(font)

        layout.addWidget(self.lineedit_code)
        layout.addWidget(self.btn_paste_code)

        layout.addWidget(self.btn_receive)


        return group
    


    def _raise_accept_messagebox(self, name: str, size: str) -> None:
        QApplication.alert(self)

        box = QMessageBox.question(
            self,
            self.worker.settings.tr("dialog:accept:title"),
            self.worker.settings.tr("dialog:accept:body1") + "<br><br>" + self.worker.settings.tr("dialog:accept:body2").format(f=f"<b>{name}</b>", s=size),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if box == QMessageBox.StandardButton.No:
            self.worker.send_input("n")
            self.worker.change_action(CrocAction.CANCELLED)
            return
        
        self.worker.send_input("y")

    def _raise_display_messagebox(self, size: str) -> None:
        QApplication.alert(self)

        box = QMessageBox.question(
            self,
            self.worker.settings.tr("dialog:ask_display_text:title"),
            self.worker.settings.tr("dialog:ask_display_text:body1") + "<br><br>" + self.worker.settings.tr("dialog:ask_display_text:body2").format(s=size),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if box == QMessageBox.StandardButton.No:
            self.worker.send_input("n")
            self.worker.change_action(CrocAction.CANCELLED)
            return
        
        self.worker.send_input("y")



    def _retranslate(self) -> None:
        """Retranslate everything on language change."""

        self.lineedit_path.setPlaceholderText(self.worker.settings.tr("receive:lineedit:placeholder_path"))
        self.btn_open_output_path.setText(self.worker.settings.tr("receive:btn:open_output_folder"))
        self.btn_browse_output_folder.setText(self.worker.settings.tr("receive:btn:select_folder"))
        self.btn_default_path.setText(self.worker.settings.tr("receive:btn:default_folder"))
        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("receive:lineedit:placeholder_code"))
        self.btn_paste_code.setText(self.worker.settings.tr("receive:btn:paste_code"))

        self._set_button_text_by_operation()
        self._update_path_tooltip()



    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.state_changed.connect(self._state_responses)
        self.worker.line_received.connect(self._read_command_line)
        self.worker.finished.connect(self._on_finish)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.lineedit_path.textChanged.connect(self._entered_output_path)
        self.lineedit_code.textChanged.connect(self._typed_in_code)

        self.btn_open_output_path.clicked.connect(self._click_open_output_folder_button)
        self.btn_browse_output_folder.clicked.connect(self._click_browse_button)
        self.btn_default_path.clicked.connect(self._click_default_path_button)
        self.btn_paste_code.clicked.connect(self._paste_code)
        self.btn_receive.clicked.connect(self._click_receive_button)

    def _set_button_text_by_operation(self) -> None:
        match self.worker.state.operation:
            case CrocOperation.RECEIVING:
                self.btn_receive.setText(self.worker.settings.tr("generic:cancel"))
            case _:
                self.btn_receive.setText(self.worker.settings.tr("generic:receive"))

    def _determine_main_button_behavior(self) -> None:
        if self.worker.state.operation == CrocOperation.SENDING or len(self.lineedit_code.text()) < 6:
            self.btn_receive.setEnabled(False)
            return
        else:
            self.btn_receive.setEnabled(True)

        self._set_button_text_by_operation()

    def _get_default_path(self) -> str:
        defualt_path: str = str(app_utils.determine_received_path("received"))
        self._output_path = defualt_path
        return defualt_path

    def _paste_code(self) -> None:
        clipboard_text: str = QApplication.clipboard().text().strip()
        self.lineedit_code.setText(clipboard_text)
    
    def _read_command_line(self, line: str) -> None:
        if self._is_text_transfer and self._text_content_lines is not None:
            self._text_content_lines.append(line)
            return

        self._test_for_accept(line)
        self._test_for_display(line)

        if _RECEIVING_RE.match(line, 0).hasMatch() and self._is_text_transfer:
            self._text_content_lines = []

    def _test_for_accept(self, line: str) -> None:
        matched_accept_prompt = _ACCEPT_RE.match(line, 0)

        if not matched_accept_prompt.hasMatch():
            return
        
        name = matched_accept_prompt.captured("filename") or matched_accept_prompt.captured("count") 
        size = matched_accept_prompt.captured("size")

        self._raise_accept_messagebox(name, size)

    def _test_for_display(self, line: str) -> None:
        matched_display_prompt = _DISPLAY_TEXT_RE.match(line, 0)
        if not matched_display_prompt.hasMatch():
            return
        
        size = matched_display_prompt.captured("size")

        self._is_text_transfer = True
        self._raise_display_messagebox(size)

    def _state_responses(self) -> None:
        self._determine_main_button_behavior()

    def _create_output_directory(self) -> None:
        Path(self._output_path).mkdir(exist_ok=True)

    def _on_finish(self, code: int, operation: CrocOperation) -> None:
        if operation != CrocOperation.RECEIVING:
            return

        if self._is_text_transfer and self._text_content_lines is not None:
            text = "\n".join(self._text_content_lines[2:]).strip()
            if text:
                self._show_received_text(text)

        self._text_content_lines = []
        self._is_text_transfer = False
        
        self.btn_receive.setEnabled(True)
    


    def _typed_in_code(self, code: str) -> None:
        self._code = code
        self._determine_main_button_behavior()

    def _entered_output_path(self, output_path: str) -> None:
        self._output_path = output_path
        self._update_path_tooltip()

    def _update_path_tooltip(self) -> None:
        if self._output_path:
            self.lineedit_path.setToolTip(self._output_path)
            return

        self.lineedit_path.setToolTip(self.worker.settings.tr("receive:lineedit:placeholder_path"))
    


    def _click_browse_button(self) -> None:
        dialog = QFileDialog(directory=self.lineedit_path.text())
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if dialog.exec():
            self.lineedit_path.setText(dialog.selectedFiles()[0])
    
    def _click_default_path_button(self) -> None:
        self.lineedit_path.setText(self._get_default_path())

    def _click_receive_button(self) -> None:
        is_active = self.worker.state.action not in (
            CrocAction.NONE,
            CrocAction.COMPLETED,
            CrocAction.CANCELLED,
            CrocAction.ERROR,
        )

        # Button is in cancel mode
        if is_active:
            self.worker.stop()
            self.worker.change_action(CrocAction.CANCELLED)
            return

        self._create_output_directory()
        self.worker.start_receive(self._code, self._output_path)

    def _click_open_output_folder_button(self) -> None:
        if not self._output_path:
            QMessageBox.warning(
                self,
                self.worker.settings.tr("dialog:no_receive_path:title"),
                self.worker.settings.tr("dialog:no_receive_path:body"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return

        path: Path = app_utils.backpedal_paths_to_existing_path(Path(self._output_path))

        if not path.exists():
            QMessageBox.warning(
                self,
                self.worker.settings.tr("dialog:invalid_receive_path:title"),
                self.worker.settings.tr("dialog:invalid_receive_path:body1") + "<br><br>" + self.worker.settings.tr("dialog:invalid_receive_path:body2"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return

        app_utils.reveal_in_file_manager(path)

    def _show_received_text(self, text: str) -> None:
        dialog = ReceiveTextDialog(text, self.worker, self)
        dialog.exec()