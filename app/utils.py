import re
import sys
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QGroupBox, QComboBox, QFileDialog,
    QListView, QTreeView, QAbstractItemView, QFrame,
    QVBoxLayout, QLabel, QStyle, QPushButton,
    QListWidget
)
from PyQt6.QtGui import QWheelEvent, QFileSystemModel, QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QSize

CODE_RE = re.compile(r"^([0-9]){4}(-[a-z]+){3}$")



def reveal_in_file_manager(path: str | Path) -> None:
    path = Path(path)
    if not path.exists():
        return

    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(path)])
        else:
            target = str(path) if path.is_file() else str(path)
            parent = str(path.parent) if path.is_file() else str(path)
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



def determine_filepath(filename: str, parent_levels: int = 0) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve()

        for _ in range(parent_levels):
            base_path = base_path.parent

    return base_path / filename

def determine_icon_filepath(file_name: str, levels_up: int) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base: Path = Path(__file__)
        for _ in range(levels_up):
            base = base.parent
    return str(base / file_name)

def determine_received_path(folder_name: str) -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent.parent

    return base_dir / folder_name

def hide_group_box_border(group_box: QGroupBox) -> None:
    group_box.setStyleSheet("QGroupBox { border: 0px solid transparent; }")

def regex_match(pattern: str, text: str) -> bool:
    return not bool(re.match(pattern, text))



class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

class MultiFolderDialog(QFileDialog):
    def __init__(self, parent=None, caption="Select Folders", directory=""):
        super().__init__(parent, caption, directory)
        
        # 1. Enforce non-native dialog (Required to modify child widgets)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        
        # 2. Tell the dialog it should look for Directories
        self.setFileMode(QFileDialog.FileMode.Directory)
        
        # 3. Target internal list views and tree views to allow multi-selection
        for view in self.findChildren((QListView, QTreeView)):
            if isinstance(view.model(), QFileSystemModel):
                view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)