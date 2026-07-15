import os
import sys
import re
import subprocess
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from app.enums import CrocState, CrocOperation, CrocAction
from app.managers.manager_settings import SettingsManager

_PROGRESS_RE = re.compile(
    r"^(Hashing\s+)?(.+?)\s+(\d+)%\s+\|",
    re.IGNORECASE
)



class CrocWorker(QThread):
    """Worker object responsible for running croc and taking commands from the GUI."""

    # Signals
    started_croc = pyqtSignal(CrocOperation)
    ended_croc = pyqtSignal(CrocOperation)

    line_received = pyqtSignal(str)
    state_changed = pyqtSignal(CrocState)
    error_state = pyqtSignal(str)
    finished = pyqtSignal(int, CrocOperation)
    error = pyqtSignal(str)

    # Percentage transferred, filename (truncated), and whetehr it's being hashed
    progress_update = pyqtSignal(int, str, bool)

    # Initialize
    def __init__(self, app_name: str, app_version: str):
        super().__init__()
        self._proc: subprocess.Popen | None = None
        self._args: list[str] = []
        self._env: dict | None = None

        # Get croc version
        self.croc_version: str | None = None
        try:
            self.croc_version = self.get_croc_version()
        except Exception:
            self.croc_version = "Couldn't get croc version!"
        
        self.state: CrocState = CrocState()

        self.settings = SettingsManager(app_name, app_version)

    # Create and return croc process
    def _create_croc_process(self, operation: CrocOperation, args: list[str]) -> subprocess.Popen:
        """Spawns the croc process with the provided arguments."""

        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE if operation == CrocOperation.RECEIVING else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=self._env,
            **kwargs
        )

        return process
    
    def _process_line(self, line: str) -> None:
        """Process the current line output from croc."""

        # Check for progress to pass
        self._check_for_progress(line)

        # Emit the line, then update status
        self.line_received.emit(line)
        self._update_state_from_line(line)
        # print(line, end="", flush=True)

    def _update_state_from_line(self, line: str) -> None:
        """Update the current CrocAction based on the output of croc."""

        # Lookup table for croc behavior and CrocAction correlation
        rules: list[dict[str, CrocAction]] = [
            (r"Code is:", CrocAction.WAIT_FOR_PEER),
            (r"Sending \(->", CrocAction.SEND_IN_PROGRESS),
            (r"Receiving \(<-", CrocAction.RECEIVE_IN_PROGRESS),

            (r"Accept", CrocAction.WAIT_FOR_APPROVAL),
            (r"connecting...", CrocAction.CONNECTING_TO_PEER)
        ]

        # Search and see if the line matches. If so, change the action
        for pattern, action in rules:
            if re.search(pattern, line, re.IGNORECASE):
                self.change_action(action)
                return
            
    def _check_for_progress(self, line: str) -> bool:
        """Parse a progress line and emit progress. Returns True if it there's a match."""

        # Test for a match, and return False if not
        match = _PROGRESS_RE.match(line.strip())
        if not match:
            return False
        
        # Get the values from the message
        is_hashing = bool(match.group(1))
        filename = match.group(2).strip()
        percent = int(match.group(3))

        # Return True
        self.progress_update.emit(percent, filename, is_hashing)
        return True
    
    def run(self) -> None:
        """Run croc and pipe outputs to be processed"""

        current_operation: CrocOperation = self.state.operation

        try:
            # Alert other scripts that corc is starting, then actually start it
            self.started_croc.emit(self.state.operation)
            self._proc = self._create_croc_process(self.state.operation, self._args)

            # Buffer for line processing
            buffer = ""

            while True:
                # Read one character of the output at a time
                ch = self._proc.stdout.read(1)

                # If we read no character but the buffer hs data, we are at the end. Process the line and end the loop
                if not ch:
                    if buffer:
                        self._process_line(buffer)
                    break

                # Add the character to the buffer
                buffer += ch

                # Update CrocState
                self._update_state_from_line(buffer)

                # Process the line if we hit a newline or carriage return
                if ch in ("\n", "\r"):
                    self._process_line(buffer.strip())
                    buffer = ""
                    continue

                # Process yes-no prompts
                if re.search(r"\(Y/n\)", buffer):
                    self.line_received.emit(buffer)
                    buffer = ""

            # Halt further action until the process ends
            self._proc.wait()

            # If we didn't cancel the operation, change the current CrocAction
            if self.state.action != CrocAction.CANCELLED:
                # If exit code is 0, it completed successfully
                if self._proc.returncode == 0:
                    self.change_action(CrocAction.COMPLETED)
                
                # If the exit code is anything else, it's an error
                else:
                    self.change_action(CrocAction.ERROR)
                    self.error_state.emit(buffer.strip())

            # Alert all scripts that croc is finishing, then return to idle
            self.finished.emit(self._proc.returncode, current_operation)
            self.change_operation(CrocOperation.IDLE)

        # Guard except for if the user somehow starts a transfer without croc installed
        except FileNotFoundError:
            self.error.emit("croc not found on PATH")

        # Generic catch all
        except Exception as e:
            self.error.emit(str(e))

        # After everything, nullify the process and alert all scripts that the croc process is physically ended
        finally:
            self._proc = None
            self.ended_croc.emit(self.state.operation)

    def start_send(self, paths: set[Path], code: str = None) -> None:
        """Construct the command to send files and then pass it to CrocWorker.run() automatically."""

        # croc, then settings, and then send
        args = ["croc"]
        args.extend(self.settings.build_flags())
        args.append("send")
        
        # If the user has a custom code, add it with the --code flag/CROC_SECRET envrionment variable
        if code:
            # Windows: Pass it as a flag
            if sys.platform == "win32":
                args.extend(["--code", code])

            # All other systems: Pass it as an environment variable
            else:
                env = os.environ.copy()
                env["CROC_SECRET"] = code

        # Remove the auto-generated secret if it was passed to avoid it sticking around
        else:
            if self._env is not None and "CROC_SECRET" in self._env:
                self._env.pop("CROC_SECRET")

        args.extend(paths)

        # print(args)

        # Change CrocState to sending while waiting for peer
        self.change_operation(CrocOperation.SENDING)
        self.change_action(CrocAction.WAIT_FOR_PEER)

        self._args = args

        # Pass the code to the env if the code is custom
        if code and sys.platform != "win32":
            self._env = env

        self.start()

    def start_receive(self, code: str, out_path: str, env: dict | None = None) -> None:
        """Construct the command to receive files and then pass it to CrocWorker.run() automatically."""

        # croc, then build flags
        args = ["croc"]
        args.extend(self.settings.build_flags())
        
        # Pass the output path
        if out_path:
            args.extend(["--out", out_path])

        # Windows: Add code as a flag
        if sys.platform == "win32":
            args.append(code)

        # All other platforms: Add code as environment variable
        else:
            env = os.environ.copy()
            env["CROC_SECRET"] = code

        self.change_operation(CrocOperation.RECEIVING)
        self.change_action(CrocAction.CONNECTING_TO_PEER)

        self._args = args

        # Only pass the environment variable if not on WIndows
        if sys.platform != "win32":
            self._env = env

        self.start()

    def send_input(self, text: str) -> None:
        """Send input to croc for yes-no prompts."""

        if self._proc and self._proc.stdin:
            self._proc.stdin.write(text + "\n")
            self._proc.stdin.flush()

    def stop(self):
        """Stop the croc process manually."""

        # If the process exists, declare the operation as cancelled and kill the process
        if self._proc and self._proc.poll() is None:
            self.change_action(CrocAction.CANCELLED)

            self._proc.terminate()

            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()



    def change_state(self, state: CrocState) -> None:
        """Change the current CrocState."""

        self.state = state
        self.state_changed.emit(self.state)

    def change_operation(self, operation: CrocOperation) -> None:
        """Change the current CrocOperation."""

        self.state.operation = operation
        self.state_changed.emit(self.state)

    def change_action(self, action: CrocAction) -> None:
        """Change the current CrocAction."""

        self.state.action = action
        self.state_changed.emit(self.state)



    def get_state(self) -> CrocState:
        """Get the current CrocState."""

        return self.state
    
    def get_operation(self) -> CrocOperation:
        """Get the current CrocOperation."""

        return self.state.operation
    
    def get_action(self) -> CrocAction:
        """Get the current CrocAction."""

        return self.state.action
    

    
    def get_action_text(self) -> tuple[str, str]:
        """Get the text and icon of the current CrocAction for display."""

        icon: str = self.get_action_icon_only()
        text: str = self.get_action_text_only()
        return f"{icon} {text}"
    
    def get_action_icon_only(self) -> str:
        """Get the icon emoji of the current CrocAction."""

        icon: str = self.state.action.text[0]
        return icon
    
    def get_action_text_only(self) -> str:
        """Get the text of the current CrocAction and then pass it to the locale manager for translation."""

        key: str = self.state.action.text[2:].strip()
        return self.settings.tr(key)
    

    
    def get_croc_version(self) -> str:
        """Get the output from croc --version as a string."""

        if self.croc_version is None:
            return subprocess.run(["croc", "--version"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        
        return self.croc_version
    
    def get_croc_version_number_only(self) -> str:
        """Get just the version number from croc --version for comparison purposes."""

        return self.get_croc_version().split("croc version ")[1]