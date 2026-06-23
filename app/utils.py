# app/utils.py
import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import QGroupBox, QComboBox
from PyQt6.QtGui import QWheelEvent





def reveal_in_file_manager(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return

    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(p)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(p)])
        else:
            target = str(p) if p.is_file() else str(p)
            parent = str(p.parent) if p.is_file() else str(p)
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



class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()