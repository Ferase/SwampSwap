import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QCheckBox,
    QGroupBox, QFileDialog, QTextEdit, QAbstractItemView,
    QSizePolicy, QApplication, QScrollArea, QFrame,
    QDialog, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir, QUrl
from PyQt6.QtGui import QFont, QPixmap, QFont, QPalette, QColor, QDesktopServices

import app.utils as app_utils
from app.enums import CrocState, CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.managers.manager_locale import SwampSwapLang, SwampSwapLanguageList



class FileDropList(QListWidget):

    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setDragEnabled(False)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)

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
        valid_paths: list[Path] = []
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    valid_paths.append(Path(url.toLocalFile()))
            
            self.files_dropped.emit(valid_paths)
            event.acceptProposedAction()
        else:
            event.ignore()



class FileListWindow(QDialog):

    files_changed = pyqtSignal(list)
    files_cleared = pyqtSignal()

    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.worker = worker

        self._paths: list[Path] = []

        # Define window title and size
        self.setWindowTitle(self.worker.settings.tr("manage_send_list:window:title"))
        self.setFixedSize(560, 350)

        # Build UI
        self._build_central()

        self._connect_signals()

    # Construct the UI
    def _build_central(self) -> None:
        # Create box layout container
        root = QVBoxLayout(self)
        root.setSpacing(8)

        files_group = self._build_files_group()
        buttons_group = self._build_buttons()

        # Add widgets to box layout
        root.addWidget(files_group)
        root.addWidget(buttons_group)
    
    def _build_files_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        self.list_widget = FileDropList()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        btn_row = QHBoxLayout()

        self.btn_add_files = QPushButton(self.worker.settings.tr("generic:add_files"))
        self.btn_add_folder = QPushButton(self.worker.settings.tr("generic:add_folders"))
        self.btn_remove = QPushButton(self.worker.settings.tr("manage_send_list:btn:remove_selected"))
        self.btn_clear = QPushButton(self.worker.settings.tr("generic:clear_list"))

        layout.addWidget(self.list_widget)
        btn_row.addWidget(self.btn_add_files)
        btn_row.addWidget(self.btn_add_folder)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_remove)
        btn_row.addWidget(self.btn_clear)
        layout.addLayout(btn_row)

        return group
    
    def _build_buttons(self) -> QGroupBox:
        group = QGroupBox()
        layout = QHBoxLayout(group)

        self.btn_ok = QPushButton(self.worker.settings.tr("generic:ok"))
        self.btn_cancel = QPushButton(self.worker.settings.tr("generic:cancel"))

        layout.addStretch()
        layout.addWidget(self.btn_ok)
        layout.addWidget(self.btn_cancel)

        return group
    


    def _retranslate(self) -> None:
        self.setWindowTitle(self.worker.settings.tr("manage_send_list:window:title"))

        self.btn_add_files.setText(self.worker.settings.tr("generic:add_files"))
        self.btn_add_folder.setText(self.worker.settings.tr("generic:add_folders"))
        self.btn_remove.setText(self.worker.settings.tr("manage_send_list:btn:remove_selected"))
        self.btn_clear.setText(self.worker.settings.tr("generic:clear_list"))

        self.btn_ok.setText(self.worker.settings.tr("generic:ok"))
        self.btn_cancel.setText(self.worker.settings.tr("generic:cancel"))



    def _connect_signals(self) -> None:
        self.list_widget.files_dropped.connect(self._add_files)

        self.btn_add_files.clicked.connect(self._click_add_files_button)
        self.btn_add_folder.clicked.connect(self._click_add_folder_button)
        self.btn_remove.clicked.connect(self._click_remove_selected_button)
        self.btn_clear.clicked.connect(self._click_clear_all_button)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def _populate(self):
        self._clear_list()
        self.list_widget.addItems([str(path) for path in self._paths])

    def _clear_list(self) -> None:
        self.list_widget.clear()



    def raise_modal(self, paths: list[Path]) -> int:
        self._paths = paths
        self._populate()

        result = self.exec()

        if not result:
            return
        
        return result
    

    def _add_files(self, paths: list[Path]):
        final_paths: list[Path] = self._filter_paths(paths)

        self._paths.extend(final_paths)

        self._populate()

    def _remove_selected(self):
        selected_texts = {item.text() for item in self.list_widget.selectedItems()}

        self._paths = [path for path in self._paths if str(path) not in selected_texts]
        self._populate()

        if not self._paths:
            self._clear_all()
            return

    def _clear_all(self):
        self._paths.clear()
        self.files_cleared.emit()
        self.accept()

    def _check_if_selected_is_dir_and_is_empty(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        
        if any(path.iterdir()):
            return False
        
        return True

    def _filter_paths(self, paths: list[Path]) -> list[Path]:
        final_paths: list[Path] = []

        for path in paths:
            if self._paths is not None and path in self._paths:
                continue

            if self._check_if_selected_is_dir_and_is_empty(path):
                continue

            final_paths.append(path)

        return final_paths



    def _click_add_files_button(self) -> None:
        dialog = QFileDialog(self, self.worker.settings.tr("file_dialog:choose_files"))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if not dialog.exec():
            return
        
        paths: list[Path] = []
        for path in dialog.selectedFiles():
            path = Path(path)
            if not self._check_if_selected_is_dir_and_is_empty(path):
                paths.append(path)

        self._add_files(paths)

    def _click_add_folder_button(self) -> None:
        dialog = QFileDialog(self, self.worker.settings.tr("file_dialog:choose_folders"))
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        if not dialog.exec():
            return
        
        paths: list[Path] = []
        for path in dialog.selectedFiles():
            path = Path(path)
            if not self._check_if_selected_is_dir_and_is_empty(path):
                paths.append(path)

        self._add_files(paths)

    def _click_remove_selected_button(self) -> None:
        self._remove_selected()

    def _click_clear_all_button(self) -> None:
        result = QMessageBox.question(
            self,
            self.worker.settings.tr("dialog:clear_list_confirm:title"),
            self.worker.settings.tr("dialog:clear_list_confirm:body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self._clear_all()



    def accept(self):
        self.files_changed.emit(list(self._paths))
        super().accept()