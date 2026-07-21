import re
import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QDoubleSpinBox, QComboBox, QFileDialog, QListView,
    QTreeView, QAbstractItemView, QStyleOptionSlider, QStyle,
    QSlider
)
from PyQt6.QtGui import QWheelEvent, QFileSystemModel
from PyQt6.QtCore import Qt, QEvent, QObject

# Regex used to see if a string matches the formatting of croc's auto-generated codes
CODE_RE = re.compile(r"^([0-9]){4}(-[a-z]+){3}$")



def reveal_in_file_manager(path: str | Path) -> None:
    """Opens the user's file manager to the specified path."""

    path = Path(path)

    # Do nothing if the path is invalid
    if not path.exists():
        return

    try:
        match sys.platform:
            # Windows: Use explorer directly
            case "win32":
                subprocess.Popen(["explorer", "/select,", str(path)])

            # macOS: Open via native commands
            case "darwin":
                subprocess.Popen(["open", "-R", str(path)])

            # Linux/Other:  Try various options for different distros
            case _:
                # Get the target file/fodler and its parent
                target = str(path)
                parent = str(path.parent) if path.is_file() else str(path)

                # Run through different options until one works
                for cmd in (
                    # GNOME
                    ["nautilus", "--select", target],

                    # KDE
                    ["dolphin", "--select", target],

                    # Cinnamon
                    ["nemo", target],

                    # XFCE
                    ["thunar", parent],

                    # Fallback
                    ["xdg-open", parent]
                ):
                    try:
                        subprocess.Popen(cmd)
                        return
                    except FileNotFoundError:
                        continue

    except Exception:
        pass


def is_executable() -> bool:
    """Returns true if Swamp Swap is being run as an executable."""

    return bool(getattr(sys, "frozen", False))

def get_running_path() -> Path:
    """Get the path in which the script/executable is being run from"""

    # If the application is a frozen executable, get the sys._MEIPASS folder
    if is_executable():
        base_path = Path(sys._MEIPASS)

    # If the application is a script, calcualte the path differently
    else:
        # Get the base path
        base_path = Path(__file__).resolve()

    return base_path

def get_true_path() -> Path:
    """Determine the true base path regardless of if Swamp Swap is a script or executable."""

    base_path: Path = get_running_path()

    if not is_executable():
        base_path = base_path.parent.parent

    return base_path

def determine_filepath(filename: str | Path, parent_levels: int = 2) -> Path:
    """Determines the path of a file relative to Swamp Swap. Will function accurately regardless of if the program is run in script form or as a frozen executable."""

    return get_true_path() / filename

def get_assets_path() -> Path:

    return get_true_path() / "assets"

def determine_received_path(folder_name: str) -> Path:
    """Determines the path of the default receive folder. Will function accurately regardless of if the program is run in script form or as a frozen executable."""

    # If the application is a frozen executable, mark it relative to the executable
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent

    # If the application is a script, mark it relative to the script
    else:
        base_dir = Path(__file__).resolve().parent.parent

    return base_dir / folder_name

def regex_match(pattern: str, text: str) -> bool:
    """Basic regex match"""

    return not bool(re.match(pattern, text))

def backpedal_paths_to_existing_path(path: Path) -> Path:
    """Backpedals a path if the specified path doesn't exist."""

    final_path: Path = path if path.exists() else backpedal_paths_to_existing_path(path.parent)

    return final_path
    




class NoScrollComboBox(QComboBox):
    """A variant of QComboBox that does not allow using scroll wheel to change the selected item."""

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

class MultiFolderDialog(QFileDialog):
    """Custom QFileDialog that allows selecting multiple folders"""

    def __init__(self, parent=None, caption="Select Folders", directory=""):
        super().__init__(parent, caption, directory)
        
        # Make the dialog non-native
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        
        # Filter valid selection to only directories
        self.setFileMode(QFileDialog.FileMode.Directory)
        
        # Allow multi-folder selection
        for view in self.findChildren((QListView, QTreeView)):
            if isinstance(view.model(), QFileSystemModel):
                view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)



class ClickableSlider(QSlider):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            sr = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider, 
                opt, 
                QStyle.SubControl.SC_SliderGroove, 
                self
            )

            if self.orientation() == Qt.Orientation.Horizontal:
                slider_length = sr.width()
                slider_pos = event.position().x() - sr.x()
            else:
                slider_length = sr.height()
                slider_pos = sr.bottom() - event.position().y()

            if slider_length > 0:
                percentage = max(0.0, min(1.0, slider_pos / slider_length))
                new_value = self.minimum() + int(percentage * (self.maximum() - self.minimum()))
                self.setValue(new_value)
                
            event.accept()
            return
        
        super().mousePressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

class NoScrollDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()