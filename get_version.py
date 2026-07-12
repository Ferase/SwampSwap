# app/update_checker.py
import urllib.request
import json
from PyQt6.QtCore import QThread, pyqtSignal


class UpdateChecker(QThread):
    update_available = pyqtSignal(str)

    def __init__(self, current_version: str, user: str, repo: str):
        super().__init__()
        self._current = current_version
        self._url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"

    def run(self):
        try:
            req = urllib.request.Request(
                self._url,
                headers={"Accept": "application/vnd.github+json"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            tag = data.get("tag_name", "")
            if tag and _is_new_version_available(tag, self._current):
                self.update_available.emit(tag)
        except Exception:
            pass



def _is_new_version_available(remote: str, local: str) -> bool:
    def parse(v: str) -> tuple[int, ...]:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    try:
        return parse(remote) > parse(local)
    except Exception:
        return False