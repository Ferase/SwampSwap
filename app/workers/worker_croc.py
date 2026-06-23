import os
import sys
import re
import subprocess
from collections import deque
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from app.enums import CrocState, CrocOperation, CrocAction
from app.managers.manager_settings import SettingsManager
from app.managers.manager_locale import LocaleManager



class CrocWorker(QThread):

    # Signals
    started_croc = pyqtSignal(CrocOperation)
    ended_croc = pyqtSignal(CrocOperation)

    line_received = pyqtSignal(str)
    state_changed = pyqtSignal(CrocState)
    error_state = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    # Initialize
    def __init__(self, app_name: str, app_version: str):
        super().__init__()
        self._proc: subprocess.Popen | None = None
        self._args: list[str] = []
        self._env: dict | None = None

        self.croc_version = "croc version NULL"
        try:
            self.croc_version = subprocess.run(["croc", "--version"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        except Exception:
            pass
        
        self.state: CrocState = CrocState()

        self.settings = SettingsManager(app_name, app_version)

    # Create and return croc process
    def _create_croc_process(self, operation: CrocOperation, args: list[str]) -> subprocess.Popen:
        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE if operation == CrocOperation.RECEIVING else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=self._env,
        )

        return process
    
    # Process the current line output by the process
    def _process_line(self, line: str) -> None:
        self.line_received.emit(line)

        self._update_state_from_line(line)

        # print(line, end="", flush=True)

    def _update_state_from_line(self, line: str) -> None:
        rules: list[dict[str, CrocAction]] = [
            (r"Code is:", CrocAction.WAIT_FOR_PEER),
            (r"Sending \(->", CrocAction.SEND_IN_PROGRESS),
            (r"Receiving \(<-", CrocAction.RECEIVE_IN_PROGRESS),

            (r"Accept", CrocAction.WAIT_FOR_APPROVAL),
            (r"connecting...", CrocAction.CONNECTING_TO_PEER)
        ]

        for pattern, action in rules:
            if re.search(pattern, line, re.IGNORECASE):
                self.change_action(action)
                return
    
    # Run croc and pipe outputs to be processed
    def run(self) -> None:
        try:
            self.started_croc.emit(self.state.operation)
            self._proc = self._create_croc_process(self.state.operation, self._args)

            buffer = ""

            while True:
                ch = self._proc.stdout.read(1)

                if not ch:
                    if buffer:
                        self._process_line(buffer)
                    break

                buffer += ch

                self._update_state_from_line(buffer)

                if ch in ("\n", "\r"):
                    self._process_line(buffer.strip())
                    buffer = ""
                    continue

                if re.search(r"\(Y/n\)", buffer):
                    self.line_received.emit(buffer)
                    buffer = ""

            self._proc.wait()

            if self.state.action != CrocAction.CANCELLED:
                if self._proc.returncode == 0:
                    self.change_action(CrocAction.COMPLETED)
                else:
                    self.change_action(CrocAction.ERROR)
                    self.error_state.emit(buffer.strip())

            self.finished.emit(self._proc.returncode)
            self.change_operation(CrocOperation.IDLE)

        except FileNotFoundError:
            self.error.emit("croc not found on PATH")
        except Exception as e:
            self.error.emit(str(e))

        finally:
            self._proc = None
            self.ended_croc.emit(self.state.operation)

    def start_send(self, path: Path) -> None:
        args = ["croc"]
        args.extend(self.settings.build_flags())
        args.append("send")
        args.append(str(path))

        self.change_operation(CrocOperation.SENDING)
        self.change_action(CrocAction.WAIT_FOR_PEER)

        self._args = args
        self.start()

    def start_receive(self, code: str, out_path: str, env: dict | None = None) -> None:
        args = ["croc"]
        
        args.extend(self.settings.build_flags())
        
        if out_path:
            args.extend(["--out", out_path])

        if sys.platform == "win32":
            args.append(code)
        else:
            env = os.environ.copy()
            env["CROC_SECRET"] = code

        self.change_operation(CrocOperation.RECEIVING)
        self.change_action(CrocAction.CONNECTING_TO_PEER)

        self._args = args
        self._env = env
        self.start()

    def send_input(self, text: str) -> None:
        if self._proc and self._proc.stdin:
            self._proc.stdin.write(text + "\n")
            self._proc.stdin.flush()

    def stop(self):
        if self._proc and self._proc.poll() is None:
            self.change_action(CrocAction.CANCELLED)

            self._proc.terminate()

            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()

    # Chagne state
    def change_state(self, state: CrocState) -> None:
        self.state = state
        self.state_changed.emit(self.state)
    def change_operation(self, operation: CrocOperation) -> None:
        self.state.operation = operation
        self.state_changed.emit(self.state)
    def change_action(self, action: CrocAction) -> None:
        self.state.action = action
        self.state_changed.emit(self.state)

    # Get statu
    def get_state(self) -> CrocState:
        return self.state
    def get_operation(self) -> CrocOperation:
        return self.state.operation
    def get_action(self) -> CrocAction:
        return self.state.action
    
    def get_action_text(self) -> tuple[str, str]:
        icon: str = self.get_action_icon_only()
        text: str = self.get_action_text_only()
        return f"{icon} {text}"
    def get_action_icon_only(self) -> str:
        icon: str = self.state.action.text[0]
        return icon
    def get_action_text_only(self) -> str:
        key: str = self.state.action.text[2:].strip()
        return self.settings.tr(key)