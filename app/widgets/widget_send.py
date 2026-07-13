import os
import re
from pathlib import Path
from typing import Iterator

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QCheckBox,
    QGroupBox, QFileDialog, QTextEdit, QAbstractItemView,
    QSizePolicy, QApplication, QStackedWidget, QFrame,
    QStyle, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir, QSize
from PyQt6.QtGui import QFont

import app.utils as app_utils
from app.enums import CrocState, CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.windows.window_filelist import FileListWindow



class DropZone(QFrame):
    clicked = pyqtSignal()
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Sunken)

        font = QFont()
        font.setBold(True)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Get style to set folder icon
        style = QApplication.style()

        pixmap_enum = QStyle.StandardPixmap.SP_DirIcon
        icon = style.standardIcon(pixmap_enum)
        pixmap = icon.pixmap(QSize(48, 48))
        
        self.label_icon = QLabel()
        self.label_icon.setPixmap(pixmap)

        label_column = QVBoxLayout()
        label_column.setSpacing(3)
        label_column.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_browse_drop = QLabel("PLACEHOLDER")
        self.label_browse_drop.setFont(font)

        self.label_file_count = QLabel("0 files, 0 folders selected")

        layout.addWidget(self.label_icon)
        layout.addLayout(label_column)
        label_column.addWidget(self.label_browse_drop)
        label_column.addWidget(self.label_file_count)
        layout.addStretch()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            paths = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.isLocalFile()
            ]
            if paths:
                self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()



class SendWidget(QWidget):

    selected_files_changed = pyqtSignal()
    files_added = pyqtSignal(list)
    folders_added = pyqtSignal(list)

    output_line = pyqtSignal(str)
    operation_running = pyqtSignal(bool)
    send_complete = pyqtSignal(str)

    # Init
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)
        
        self.worker: CrocWorker = worker

        self.selected_files_folders: dict[str, set[Path]] = {
            "files": set(),
            "folders": set()
        }
        self.selected_files_folders_count: dict[str, int] = {
            "files": 0,
            "folders": 0
        }

        self._window_filelist = FileListWindow(self.worker, self)

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
        layout = QVBoxLayout(group)

        self.drop_zone = DropZone()
        self.drop_zone.label_browse_drop.setText(self.worker.settings.tr("send:label:drop_zone"))
        self.drop_zone.label_file_count.setText(self.worker.settings.tr("send:label:no_files_selected"))

        btn_row = QHBoxLayout()

        self.btn_add_files = QPushButton(self.worker.settings.tr("generic:add_files"))
        self.btn_add_files.setMinimumHeight(35)

        self.btn_add_folders = QPushButton(self.worker.settings.tr("generic:add_folders"))
        self.btn_add_folders.setMinimumHeight(35)

        self.btn_view_file_list = QPushButton(self.worker.settings.tr("send:btn:view_file_list"))
        self.btn_view_file_list.setMinimumHeight(35)

        self.btn_clear_list = QPushButton(self.worker.settings.tr("generic:clear_list"))

        layout.addWidget(self.drop_zone)

        layout.addLayout(btn_row)
        btn_row.addWidget(self.btn_add_files)
        btn_row.addWidget(self.btn_add_folders)

        layout.addWidget(self.btn_view_file_list)
        layout.addWidget(self.btn_clear_list)

        self.btn_view_file_list.setEnabled(False)
        self.btn_clear_list.setEnabled(False)

        return group
    
    # Send controls
    def _build_controls_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.btn_send = QPushButton(self.worker.settings.tr("generic:send"))
        self.btn_send.setMinimumHeight(80)
        self.btn_send.setEnabled(False)
        font = self.btn_send.font()
        font.setPointSize(24)
        self.btn_send.setFont(font)

        self.lineedit_code = QLineEdit()
        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("send:lineedit:placeholder_code"))

        self.btn_copy_code = QPushButton(self.worker.settings.tr("send:btn:copy_code"))
        self.btn_copy_code.setEnabled(False)

        layout.addWidget(self.btn_send)
        layout.addWidget(self.lineedit_code)
        layout.addWidget(self.btn_copy_code)

        return group
    


    def _retranslate(self) -> None:
        """Retranslate everything on language change."""

        self.drop_zone.label_browse_drop.setText(self.worker.settings.tr("send:label:drop_zone"))
        self.btn_add_files.setText(self.worker.settings.tr("generic:add_files"))
        self.btn_add_folders.setText(self.worker.settings.tr("generic:add_folders"))
        self.btn_view_file_list.setText(self.worker.settings.tr("send:btn:view_file_list"))
        self.btn_clear_list.setText(self.worker.settings.tr("generic:clear_list"))

        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("send:lineedit:placeholder_code"))
        self.btn_copy_code.setText(self.worker.settings.tr("send:btn:copy_code"))

        self._set_button_text_by_operation()
        self.drop_zone.label_file_count.setText(self._create_file_folder_count_text())
        


    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.state_changed.connect(self._state_responses)
        self.worker.line_received.connect(self._read_command_line)
        self.worker.finished.connect(self._on_finish)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.selected_files_changed.connect(self._update_selected_file_ui)

        self.files_added.connect(self._add_selected_files)
        self.folders_added.connect(self._add_selected_files)

        self.lineedit_code.textChanged.connect(self._enable_copy_code_button)
        self.lineedit_code.textChanged.connect(self._determine_main_button_behavior)

        self.btn_add_files.clicked.connect(self._click_browse_file_button)
        self.btn_add_folders.clicked.connect(self._click_browse_folder_button)
        self.btn_view_file_list.clicked.connect(self._click_view_filelist_button)
        self.btn_clear_list.clicked.connect(self._click_clear_button)
        
        self.drop_zone.files_dropped.connect(self._add_selected_files)

        self.btn_copy_code.clicked.connect(self._copy_code)
        self.btn_send.clicked.connect(self._click_send_button)

        self._window_filelist.files_changed.connect(self._set_selected_files)
        self._window_filelist.files_cleared.connect(self._reset_selected_fies_folders)

    def _set_button_text_by_operation(self) -> None:
        match self.worker.state.operation:
            case CrocOperation.SENDING:
                self.btn_send.setText(self.worker.settings.tr("generic:cancel"))
            case _:
                self.btn_send.setText(self.worker.settings.tr("generic:send"))

    def _determine_main_button_behavior(self) -> None:
        files_selected: bool = self.are_files_selected()

        if self.worker.state.operation == CrocOperation.RECEIVING or not files_selected or (self.lineedit_code.text() and len(self.lineedit_code.text()) < 6):
            self.btn_send.setEnabled(False)
            return
        
        elif files_selected:
            self.btn_send.setEnabled(True)

        is_sending: bool = self.worker.state.action not in [CrocAction.NONE, CrocAction.COMPLETED, CrocAction.CANCELLED, CrocAction.ERROR]
        self._set_button_text_by_operation()
        self.lineedit_code.setDisabled(is_sending)

    def _reset_file_folder_count(self) -> None:
        self.selected_files_folders_count["files"] = 0
        self.selected_files_folders_count["folders"] = 0

        self.drop_zone.label_file_count.setText(self._create_file_folder_count_text())

    def _calculate_file_folder_count(self) -> None:
        # Init file/folder count
        file_count: int = 0
        folder_count: int = 0

        for folder in self.selected_files_folders["folders"]:
            file_count += sum(1 for item in folder.rglob("*") if item.is_file())
            folder_count += sum(1 for item in folder.rglob("*") if item.is_dir())

        for file in self.selected_files_folders["files"]:
            file_count += 1

        self.selected_files_folders_count["files"] = file_count
        self.selected_files_folders_count["folders"] = folder_count

    def _create_file_folder_count_text(self) -> str:
        if all(count == 0 for count in self.selected_files_folders_count.values()):
            return self.worker.settings.tr("send:label:no_files_selected")

        file_text: str = ""
        folder_text: str = ""

        files_count: int = self.selected_files_folders_count["files"]
        folders_count: int = self.selected_files_folders_count["folders"]

        if files_count:
            file_text: str = self._determine_selected_files_text("file", files_count)
        
        if folders_count:
            folder_text: str = self._determine_selected_files_text("folder", folders_count)

        if file_text and folder_text:
            return f"{file_text}, {folder_text}"
        
        return folder_text if folder_text else file_text

    def _determine_selected_files_text(self, target: str, count: int) -> str:
        if count <= 0:
            return ""
        
        count_text: str = format(count, ",")
        
        if count == 1:
            return self.worker.settings.tr(f"template:num_{target}_single").format(n=count_text)
        else:
            return self.worker.settings.tr(f"template:num_{target}s_multiple").format(n=count_text)
    
    def _read_command_line(self, line: str) -> None:
        self._test_for_code(line)

    def _test_for_code(self, line: str) -> None:
        if self.lineedit_code.text():
            return

        match = re.search(r"Code is:\s*(.+)", line, re.IGNORECASE)
        if match:
            self.lineedit_code.setText(match.group(1).strip())

    def are_files_selected(self) -> bool:
        return any([value for value in self.selected_files_folders.values()])

    def _state_responses(self) -> None:
        self._determine_main_button_behavior()

    def _on_finish(self, code: int) -> None:
        self._clear_code()
        if self.are_files_selected():
            self.btn_send.setEnabled(True)

    def _paths_set_to_string(self, paths: set[Path]) -> str:
        return "\n".join([str(path) + os.sep + "*" if path.is_dir() else str(path) for path in paths])
    
    def _reset_selected_fies_folders(self) -> None:
        self.selected_files_folders["files"].clear()
        self.selected_files_folders["folders"].clear()
        self._update_selected_file_ui()

    def _flatten_selected_files(self) -> set[Path]:
        final_list: list[Path] = self.selected_files_folders["files"].copy()
        final_list.update(self.selected_files_folders["folders"])
        return final_list
    
    def _unflatten_seleced_files(self, paths: set[Path]) -> dict[str, set[Path]]:
        final_dict: dict[str, set[Path]] = {
            "files": set(),
            "folders": set()
        }

        for path in paths:
            if path.is_dir():
                final_dict["folders"].add(path)
                continue
            
            final_dict["files"].add(path)

        return final_dict



    def _list_str_to_set_path(self, paths: list[str]) -> set[Path]:
        return set([Path(path) for path in paths])

    def _check_if_selected_is_dir_and_is_empty(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        
        if any(path.iterdir()):
            return False
        
        return True

    def _filter_paths(self, paths: set[Path]) -> set[Path]:
        final_paths: set[Path] = set()

        flattened_paths: set[Path] = self._flatten_selected_files()

        for path in paths:
            if self._check_if_selected_is_dir_and_is_empty(path):
                continue

            final_paths.add(path)

        return final_paths
    
    def _set_selected_files(self, paths: set[Path]) -> None:
        final_paths: set[Path] = set()
        for path in paths:
            if not self._check_if_selected_is_dir_and_is_empty(path):
                final_paths.add(path)

        self.selected_files_folders = self._unflatten_seleced_files(final_paths)
        self.selected_files_changed.emit()
    
    def _add_selected_files(self, paths: list[str]) -> None:
        final_paths: set[Path] = self._filter_paths(self._list_str_to_set_path(paths))

        organized_paths: dict[str, set[Path]] = self._unflatten_seleced_files(final_paths)

        self.selected_files_folders["files"].update(organized_paths["files"])
        self.selected_files_folders["folders"].update(organized_paths["folders"])
        self.selected_files_changed.emit()



    def _update_selected_file_ui(self) -> None:
        self._enable_list_buttons(bool(self.selected_files_folders))

        if not self.selected_files_folders or self.selected_files_folders is None:
            self.selected_files_folders = None
            self._reset_file_folder_count()
            self._determine_main_button_behavior()
            return

        self._calculate_file_folder_count()
        count_text: str = self._create_file_folder_count_text()
        self.drop_zone.label_file_count.setText(count_text)
        self._determine_main_button_behavior()

    def _enable_copy_code_button(self, text: str) -> None:
        self.btn_copy_code.setEnabled(bool(text))

    def _copy_code(self) -> None:
        QApplication.clipboard().setText(self.lineedit_code.text())

    def _enable_list_buttons(self, enabled: bool) -> None:
        self.btn_view_file_list.setEnabled(enabled)
        self.btn_clear_list.setEnabled(enabled)

    def _clear_code(self) -> None:
        is_generated_code: bool = app_utils.regex_match(app_utils.CODE_RE, self.lineedit_code.text())
        if not is_generated_code:
            self.lineedit_code.clear()



    def _click_browse_file_button(self) -> None:
        dialog = app_utils.QFileDialog(
            self,
            self.worker.settings.tr("file_dialog:choose_files")
        )

        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if not dialog.exec():
            return
        
        selected_files: list[str] = dialog.selectedFiles()
        self.files_added.emit(selected_files)

    def _click_browse_folder_button(self) -> None:
        dialog = app_utils.MultiFolderDialog(
            self,
            self.worker.settings.tr("file_dialog:choose_folders")
        )

        if not dialog.exec():
            return
        
        selected_folders: list[str] = dialog.selectedFiles()
        self.folders_added.emit(selected_folders)

    def _click_view_filelist_button(self) -> None:
        result = self._window_filelist.raise_modal(self.selected_files_folders)

        if result == QDialog.DialogCode.Rejected:
            return

        self._update_selected_file_ui()

    def _click_clear_button(self) -> None:
        result = QMessageBox.question(
            self,
            self.worker.settings.tr("dialog:clear_list_confirm:title"),
            self.worker.settings.tr("dialog:clear_list_confirm:body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self._reset_selected_fies_folders()

    def _click_send_button(self) -> None:
        if self.selected_files_folders is None:
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
            self.worker.change_action(CrocAction.CANCELLED)
            return

        self.worker.start_send(self._flatten_selected_files(), self.lineedit_code.text())