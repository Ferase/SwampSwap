# app/update_checker.py
import urllib.request
import json
from PyQt6.QtCore import QThread, pyqtSignal


class UpdateChecker(QThread):
    """Basic update checker that uses GitHub's REST API to check for updates to a specific repo by their release tag."""

    update_available = pyqtSignal(str)

    def __init__(self, current_version: str, user: str, repo: str):
        """Construct URL and get current version."""

        super().__init__()
        self._current = current_version
        self._url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"

    def run(self):
        # Try to reach out to GitHub and get the tag name for version comparison
        try:
            # Reach out to GitHub's API
            result = urllib.request.Request(
                self._url,
                headers={"Accept": "application/vnd.github+json"}
            )

            # Get the resulting data as JSON
            with urllib.request.urlopen(result, timeout=5) as resp:
                data = json.loads(resp.read())

            # Get the tag name
            tag = data.get("tag_name", "")

            # Emit the update_available signal if the remote version tests newer
            if tag and _is_new_version_available(tag, self._current):
                self.update_available.emit(tag)

        except Exception:
            pass



def _is_new_version_available(remote: str, local: str) -> bool:
    """Check if a new version is available by comparing the rgiven emote and local version numbers."""

    # Child function that parses a version string into a tuple
    def _parse(v: str) -> tuple[int]:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    
    # Try comparing versions, and if remote is newer, return True. Return false if anything goes wrong or if the user is up to date.
    try:
        return _parse(remote) > _parse(local)
    except Exception:
        return False