from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QSizePolicy, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.enums import CrocOperation
from app.workers.worker_croc import CrocWorker



class ConsoleWindow(QMainWindow):
    """Simple console window that shows output from croc that would normally appear in a terminal."""

    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window)

        self.worker = worker

        # Define window title and size
        self.setWindowTitle(self.worker.settings.tr("console:window:title"))
        self.setFixedSize(500, 500)

        # Build UI
        self._build_central()

        self._connect_signals()
        self._toggle_input()

    # Construct the UI
    def _build_central(self) -> None:
        root = QGroupBox(self)
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setSpacing(8)

        console_group = self._build_console_group()
        input_group = self._build_input_group()

        # Add widgets to box layout
        layout.addWidget(console_group)
        layout.addWidget(input_group)

    def _build_console_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        font.setPointSize(10)

        self.textedit_console = QTextEdit()
        self.textedit_console.setReadOnly(True)
        self.textedit_console.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.textedit_console.setFont(font)
        self.textedit_console.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.btn_clear = QPushButton(self.worker.settings.tr("generic:clear"))

        layout.addWidget(self.textedit_console)
        layout.addWidget(self.btn_clear)

        return group

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QHBoxLayout(group)

        self.lineedit_input = QLineEdit()
        self.lineedit_input.setPlaceholderText(self.worker.settings.tr("console:input_placeholder"))

        self.btn_submit = QPushButton(self.worker.settings.tr("generic:submit"))

        layout.addWidget(self.lineedit_input)
        layout.addWidget(self.btn_submit)

        return group



    def _retranslate(self) -> None:
        """Retranslate everything on language change."""

        self.setWindowTitle(self.worker.settings.tr("console:window:title"))
        self.btn_clear.setText(self.worker.settings.tr("generic:clear"))
        self.btn_submit.setText(self.worker.settings.tr("generic:submit"))
        self.lineedit_input.setPlaceholderText(self.worker.settings.tr("console:input_placeholder"))



    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.worker.line_received.connect(self._output_line)
        self.worker.started_croc.connect(self._toggle_input)
        self.worker.ended_croc.connect(self._toggle_input)

        self.btn_clear.clicked.connect(self._clicked_clear_button)
        self.btn_submit.clicked.connect(self._clicked_submit_button)

        self.lineedit_input.returnPressed.connect(self._clicked_submit_button)

    def _output_line(self, line: str) -> None:
        """Output a line to the console window text area."""

        self.textedit_console.append(line)

    def _toggle_input(self, operation: CrocOperation = None) -> None:
        """Enables the input box only when croc is running."""

        if operation is not None:
            not_idle: bool = operation != CrocOperation.IDLE
        else:
            not_idle: bool = False

        self.btn_submit.setEnabled(not_idle)
        self.lineedit_input.setEnabled(not_idle)



    def _clicked_clear_button(self) -> None:
        """Clears the console."""

        self.textedit_console.clear()

    def _clicked_submit_button(self) -> None:
        """Submits the typed text to the current running croc instance."""

        text: str = self.lineedit_input.text()

        if text:
            self.textedit_console.append(text)
            self.worker.send_input(text)
            self.lineedit_input.clear()