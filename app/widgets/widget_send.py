import os
import sys
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog,
    QPushButton, QLineEdit, QLabel, QMessageBox,
    QGroupBox, QFileDialog, QApplication, QFrame,
    QStyle, QTabWidget, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont

import app.utils as app_utils
from app.enums import CrocOperation, CrocAction, SendType
from app.workers.worker_croc import CrocWorker
from app.windows.window_filelist import FileListWindow
from app.managers.manager_sendfiles import SendFilesManager, SendableFileFolder
from app.windows.window_filterfiles import FilterFilesDialog



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
        if sys.platform == "win32":
            pixmap = icon.pixmap(QSize(40, 40))
        else:
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



class SendFilesWidget(QWidget):
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.worker = worker

        # Build UI
        self._build_central()
        self._connect_signals()

    def _build_central(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

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

        root.addWidget(self.drop_zone)

        root.addLayout(btn_row)
        btn_row.addWidget(self.btn_add_files)
        btn_row.addWidget(self.btn_add_folders)

        root.addWidget(self.btn_view_file_list)
        root.addWidget(self.btn_clear_list)

        self.btn_view_file_list.setEnabled(False)
        self.btn_clear_list.setEnabled(False)

    def _retranslate(self) -> None:
        self.drop_zone.label_browse_drop.setText(self.worker.settings.tr("send:label:drop_zone"))
        self.drop_zone.label_file_count.setText(self.worker.settings.tr("send:label:no_files_selected"))
        self.btn_add_files.setText(self.worker.settings.tr("generic:add_files"))
        self.btn_add_folders.setText(self.worker.settings.tr("generic:add_folders"))
        self.btn_view_file_list.setText(self.worker.settings.tr("send:btn:view_file_list"))
        self.btn_clear_list.setText(self.worker.settings.tr("generic:clear_list"))

    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)



class SendTextWidget(QWidget):
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.worker = worker

        # Build UI
        self._build_central()
        self._connect_signals()

    def _build_central(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        self.label_text = QLabel(self.worker.settings.tr("send:label:send_text"))

        self.textedit_text = QTextEdit()
        self.textedit_text.setPlaceholderText(self.worker.settings.tr("send:textedit:send_text"))

        root.addWidget(self.label_text)
        root.addWidget(self.textedit_text)

    def _retranslate(self) -> None:
        self.textedit_text.setPlaceholderText(self.worker.settings.tr("send:textedit:send_text"))

    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)



class SendWidget(QWidget):

    files_added = pyqtSignal(list)
    folders_added = pyqtSignal(list)

    output_line = pyqtSignal(str)
    operation_running = pyqtSignal(bool)
    send_complete = pyqtSignal(str)

    # Init
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self._send_type: SendType = SendType.FILES
        
        self.worker: CrocWorker = worker

        self.sendfiles_manager = SendFilesManager(self.worker)

        self.window_filelist = FileListWindow(self.worker, self.sendfiles_manager, self)

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
        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.tabBar().setUsesScrollButtons(False)

        self.widget_files = SendFilesWidget(self.worker)
        self.tabs.addTab(self.widget_files, self.worker.settings.tr("send:tab:files"))

        self.widget_text = SendTextWidget(self.worker)
        self.tabs.addTab(self.widget_text, self.worker.settings.tr("send:tab:text"))

        return self.tabs
    
    # Send controls
    def _build_controls_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.btn_send = QPushButton(self.worker.settings.tr("generic:send"))
        self.btn_send.setMinimumHeight(60)
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

        self.lineedit_code.setPlaceholderText(self.worker.settings.tr("send:lineedit:placeholder_code"))
        self.btn_copy_code.setText(self.worker.settings.tr("send:btn:copy_code"))

        self._set_button_text_by_operation()
        self.widget_files.drop_zone.label_file_count.setText(self._create_file_folder_count_text())
        


    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.state_changed.connect(self._state_responses)
        self.worker.line_received.connect(self._read_command_line)
        self.worker.finished.connect(self._on_finish)

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.tabs.currentChanged.connect(
            lambda i: self._mark_send_type(SendType(i))
        )
        self.tabs.currentChanged.connect(self._determine_main_button_behavior)

        self.widget_text.textedit_text.textChanged.connect(self._determine_main_button_behavior)

        self.sendfiles_manager.selected_files_changed.connect(self._update_selected_file_ui)
        self.sendfiles_manager.file_count_updated.connect(self._on_file_count_updated)

        self.files_added.connect(self._add_selected_files)
        self.folders_added.connect(self._add_selected_files)

        self.lineedit_code.textChanged.connect(self._enable_copy_code_button)
        self.lineedit_code.textChanged.connect(self._determine_main_button_behavior)

        self.widget_files.btn_add_files.clicked.connect(self._click_browse_file_button)
        self.widget_files.btn_add_folders.clicked.connect(self._click_browse_folder_button)
        self.widget_files.btn_view_file_list.clicked.connect(self._click_view_filelist_button)
        self.widget_files.btn_clear_list.clicked.connect(self._click_clear_button)
        
        self.widget_files.drop_zone.files_dropped.connect(self._add_selected_files)

        self.btn_copy_code.clicked.connect(self._copy_code)
        self.btn_send.clicked.connect(self._click_send_button)

        self.window_filelist.files_changed.connect(self._set_selected_files)
        self.window_filelist.files_cleared.connect(self._reset_selected_fies_folders)



    def _set_button_text_by_operation(self) -> None:
        match self.worker.state.operation:
            case CrocOperation.SENDING:
                self.btn_send.setText(self.worker.settings.tr("generic:cancel"))
            case _:
                self.btn_send.setText(self.worker.settings.tr("generic:send"))

    def _main_button_toggle_send_files(self) -> None:
        files_selected: bool = self.are_files_selected()

        if self.worker.state.operation == CrocOperation.RECEIVING or not files_selected or (self.lineedit_code.text() and len(self.lineedit_code.text()) < 6):
            self.btn_send.setEnabled(False)
            return
        
        elif files_selected:
            self.btn_send.setEnabled(True)

        is_sending: bool = self.worker.state.action not in [CrocAction.NONE, CrocAction.COMPLETED, CrocAction.CANCELLED, CrocAction.ERROR]
        self._set_button_text_by_operation()
        self.lineedit_code.setDisabled(is_sending)

    def _main_button_toggle_send_text(self) -> None:
        text_to_send: str = self._get_text_to_send()

        if self.worker.state.operation == CrocOperation.RECEIVING or not text_to_send or (self.lineedit_code.text() and len(self.lineedit_code.text()) < 6):
            self.btn_send.setEnabled(False)
            return

        elif text_to_send:
            self.btn_send.setEnabled(True)

        is_sending: bool = self.worker.state.action not in [CrocAction.NONE, CrocAction.COMPLETED, CrocAction.CANCELLED, CrocAction.ERROR]
        self._set_button_text_by_operation()
        self.lineedit_code.setDisabled(is_sending)

    def _determine_main_button_behavior(self) -> None:
        if self._send_type == SendType.FILES:
            self._main_button_toggle_send_files()
            return

        self._main_button_toggle_send_text()

    def _on_file_count_updated(self, count: dict) -> None:
        count_text = self._create_file_folder_count_text()
        self.widget_files.drop_zone.label_file_count.setText(count_text)

    def _create_file_folder_count_text(self) -> str:
        if all(count <= 0 for count in self.sendfiles_manager.selected_paths_count.values()):
            return self.worker.settings.tr("send:label:no_files_selected")

        file_text: str = ""
        folder_text: str = ""

        files_count: int = self.sendfiles_manager.selected_paths_count["files"]
        folders_count: int = self.sendfiles_manager.selected_paths_count["folders"]

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
        return bool(self.sendfiles_manager.selected_paths)

    def _state_responses(self) -> None:
        self._enable_controls()
        self._determine_main_button_behavior()

    def _on_finish(self, code: int, operation: CrocOperation) -> None:
        if operation != CrocOperation.SENDING:
            return

        self._clear_code()
        self._enable_controls()
        if self.are_files_selected():
            self.btn_send.setEnabled(True)

    def _paths_set_to_string(self, paths: set[Path]) -> str:
        return "\n".join([str(path) + os.sep + "*" if path.is_dir() else str(path) for path in paths])
    
    def _reset_selected_fies_folders(self) -> None:
        self.sendfiles_manager.clear_selected_file_set()
        self._update_selected_file_ui()

    def _flatten_paths_dict(self, paths_dict: dict[str, Path]) -> set[Path]:
        final_list: set[Path] = paths_dict.copy()
        final_list.update(paths_dict["folders"])
        return final_list

    def _unflatten_paths_set(self, paths: set[Path]) -> dict[str, Path]:
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

    def _flatten_selected_files(self) -> set[Path]:
        return set([sendable.root_path for sendable in self.sendfiles_manager.selected_paths])

    def _flatten_excluded_files(self) -> set[Path]:
        excluded_files_by_path: set[Path] = set()
        excluded_files_by_type: set[Path] = set()

        for sendable in self.sendfiles_manager.selected_paths:
            excluded_files_by_path.update(sendable.excluded_files)

            for filetype_path in sendable.excluded_filetypes.values():
                excluded_files_by_type.update(filetype_path)
            
        return excluded_files_by_path | excluded_files_by_type



    def _list_str_to_sendable_set(self, paths: list[str]) -> set[SendableFileFolder]:
        return set([SendableFileFolder(path) for path in paths])

    def _check_if_selected_is_dir_and_is_empty(self, path: SendableFileFolder) -> bool:
        if not path.is_folder:
            return False
        
        if any(path.root_path.iterdir()):
            return False
        
        return True

    def _filter_paths(self, sendables: set[SendableFileFolder]) -> set[SendableFileFolder]:
        final_paths: set[SendableFileFolder] = set()

        for sendable in sendables:
            if self._check_if_selected_is_dir_and_is_empty(sendable):
                continue

            final_paths.add(sendable)

        return final_paths
    
    def _set_selected_files(self, sendables: set[SendableFileFolder]) -> None:
        final_paths: set[SendableFileFolder] = self._filter_paths(sendables)
        self.sendfiles_manager.set_paths(final_paths)
    
    def _add_selected_files(self, paths: list[str]) -> None:
        final_paths: set[SendableFileFolder] = self._filter_paths(self._list_str_to_sendable_set(paths))

        if self.worker.settings.raise_filter_window:
            for path in final_paths:
                if path.is_folder:
                    path = self._open_filter_dialog(path)

        self.sendfiles_manager.add_paths(final_paths)



    def _update_selected_file_ui(self) -> None:
        self._enable_list_buttons(bool(self.sendfiles_manager.selected_paths))

        self._determine_main_button_behavior()
        self._enable_controls()

    def _enable_copy_code_button(self, text: str) -> None:
        self.btn_copy_code.setEnabled(bool(text))

    def _copy_code(self) -> None:
        QApplication.clipboard().setText(self.lineedit_code.text())

    def _enable_list_buttons(self, enabled: bool) -> None:
        self.widget_files.btn_view_file_list.setEnabled(enabled)
        self.widget_files.btn_clear_list.setEnabled(enabled)

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
        result = self.window_filelist.raise_modal(self.sendfiles_manager.selected_paths)

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
        match self._send_type:
            case SendType.FILES:
                if not self.sendfiles_manager.selected_paths:
                    return

            case _:
                if not self.widget_text.textedit_text.toPlainText():
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

        items_for_croc: set[Path] | str = None
        exclusions_for_croc: set[Path] | None = None
        if self._send_type == SendType.FILES:
            items_for_croc = self._flatten_selected_files()
            exclusions_for_croc = self._flatten_excluded_files()
        else:
            items_for_croc = self._get_text_to_send()

        self.worker.start_send(items_for_croc, exclusions_for_croc, self.lineedit_code.text())
        self._enable_controls()

    def _enable_controls(self) -> None:
        can_send_no_files: bool = False
        block_all: bool = False

        if not self.are_files_selected():
            can_send_no_files = True
            
        if self.worker.state.operation == CrocOperation.SENDING:
            block_all = True
        
        self.widget_files.drop_zone.setDisabled(block_all)
        self.widget_files.btn_add_files.setDisabled(block_all)
        self.widget_files.btn_add_folders.setDisabled(block_all)
        self.widget_files.btn_view_file_list.setDisabled(block_all or can_send_no_files)
        self.widget_files.btn_clear_list.setDisabled(block_all or can_send_no_files)

    def _mark_send_type(self, send_type: SendType) -> None:
        self._send_type = send_type

    def _get_text_to_send(self) -> str:
        return self.widget_text.textedit_text.toPlainText()



    def _open_filter_dialog(self, folder: SendableFileFolder) -> SendableFileFolder:
        dialog = FilterFilesDialog(folder, self.worker, self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.sendfiles_manager.calculate_file_folder_count()
            return dialog.sendable

        return folder