from pathlib import Path

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFileDialog, QAbstractItemView,
    QApplication, QDialog, QListWidget, QMessageBox,
    QListWidgetItem, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

import app.utils as app_utils
from app.workers.worker_croc import CrocWorker



class FileDropList(QListWidget):
    """A subclass of QListWidget that accepts dropped files and pipes them out with a signal."""

    files_dropped = pyqtSignal(set)

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
        valid_paths: set[Path] = {}
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    valid_paths.add(Path(url.toLocalFile()))
            
            self.files_dropped.emit(valid_paths)
            event.acceptProposedAction()
        else:
            event.ignore()



class FileListWindow(QDialog):
    """An extended window for managing the files you wish to send."""

    files_changed = pyqtSignal(dict)
    files_cleared = pyqtSignal()

    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.worker = worker

        self._dirty: bool = False
        self._paths: dict[str, set[Path]] = {
            "files": set(),
            "folders": set(),
        }

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
        """Retranslate everything on language change."""

        self.setWindowTitle(self.worker.settings.tr("manage_send_list:window:title"))

        self.btn_add_files.setText(self.worker.settings.tr("generic:add_files"))
        self.btn_add_folder.setText(self.worker.settings.tr("generic:add_folders"))
        self.btn_remove.setText(self.worker.settings.tr("manage_send_list:btn:remove_selected"))
        self.btn_clear.setText(self.worker.settings.tr("generic:clear_list"))

        self.btn_ok.setText(self.worker.settings.tr("generic:ok"))
        self.btn_cancel.setText(self.worker.settings.tr("generic:cancel"))



    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.list_widget.files_dropped.connect(self._add_files)
        self.list_widget.itemDoubleClicked.connect(
            lambda item: app_utils.reveal_in_file_manager(item.text())
        )

        self.btn_add_files.clicked.connect(self._click_add_files_button)
        self.btn_add_folder.clicked.connect(self._click_add_folder_button)
        self.btn_remove.clicked.connect(self._click_remove_selected_button)
        self.btn_clear.clicked.connect(self._click_clear_all_button)

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self._click_cancel_button)

    def _populate(self):
        """Populate the file list with the contents of FileListWindow._paths."""

        self._clear_list()

        # Pass folders first, then files
        self._create_list_items(self._paths["folders"], "folders")
        self._create_list_items(self._paths["files"], "files")

    def _create_list_items(self, paths: set[Path], item_tyoe: str) -> None:
        """Create QListWidgetItem objects that will be used to populate the main list."""

        if item_tyoe == "folders":
            icon: QIcon = self._get_folder_icon()
        else:
            icon: QIcon = self._get_file_icon()
        
        for path in paths:
            list_item = QListWidgetItem(str(path))
            list_item.setIcon(icon)
            self.list_widget.addItem(list_item)

    def _clear_list(self) -> None:
        self.list_widget.clear()
    
    def _get_folder_icon(self) -> QIcon:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)

    def _get_file_icon(self) -> QIcon:
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)



    def raise_modal(self, paths: dict[str, Path]) -> int:
        """Raise this window as a modal and handle passing of the current paths more directly."""

        # Copy the paths so we don't alter the passed paths list directly
        self._paths = paths.copy()
        self._populate()

        result = self.exec()

        # If the user chooses cancel, their changes will not be sent back to the main window
        if result == QDialog.DialogCode.Rejected:
            return
        
        return result
    

    def _add_files(self, paths: set[str]):
        """Add files to the list."""

        # Filter out paths
        final_paths: set[Path] = self._filter_paths(paths)

        # Do nothing if no valid files were added
        if not final_paths:
            return
        
        # Mark dirty
        self._mark_dirty()

        # Update and populate
        self._paths["files"].update(final_paths)
        self._populate()

    def _add_folders(self, paths: set[str]):
        """Add folders to the list."""

        # Filter out paths
        final_paths: set[Path] = self._filter_paths(paths)

        # Do nothing if no valid folders were added
        if not final_paths:
            return
        
        # Mark dirty
        self._mark_dirty()

        # Update and populate
        self._paths["folders"].update(final_paths)
        self._populate()

    def _remove_selected(self):
        """Removes the selected list items from the list."""

        # Determine selected items
        selected_items: set[str] = {item.text() for item in self.list_widget.selectedItems()}

        # Do nothing if nothing was selected
        if not selected_items:
            return
        
        # Mark dirty
        self._mark_dirty()

        # Update the dictionary
        self._paths["folders"] = set([path for path in self._paths["folders"] if str(path) not in selected_items])
        self._paths["files"] = set([path for path in self._paths["files"] if str(path) not in selected_items])

        # Repopulate
        self._populate()

        if not self._paths:
            self._clear_all()
            return

    def _clear_all(self):
        """Clear all of the files from the file list by reverting them to empty sets, then emit a signal alerting other listening scripts that all files were cleared."""

        # Replace both values with empty sets
        self._paths["files"] = set()
        self._paths["folders"] = set()

        self.files_cleared.emit()
        self.accept()

    def _check_if_selected_is_dir_and_is_empty(self, path: Path) -> bool:
        """Checks if a path is a directory and if it's empty. Empty directories will be filtered out elsewhere becasue croc can't do anything with them."""

        # If the path isn't a directory
        if not path.is_dir():
            return False
        
        # If the path contains nothing
        if any(path.iterdir()):
            return False
        
        return True

    def _filter_paths(self, paths: set[str]) -> set[Path]:
        """Filter out paths that are invalid and return a clean set."""

        final_paths: set[Path] = set()

        # Check each path for unwanted things before adding it to the final set
        for path in paths:
            path = Path(path)
            if self._check_if_selected_is_dir_and_is_empty(path):
                continue

            final_paths.add(path)

        return final_paths
    
    def _mark_dirty(self) -> None:
        """Marks the current list dirty and will prevent the user from cancelling unless they confirm."""

        self._dirty = True
    
    def _clear_dirty(self) -> None:
        """Clears the dirty state."""

        self._dirty = False



    def _click_add_files_button(self) -> None:
        dialog = QFileDialog(self, self.worker.settings.tr("file_dialog:choose_files"))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        # Do nothing if the dialog was cancelled
        if not dialog.exec():
            return

        # Pass paths as strings to be added
        self._add_files(dialog.selectedFiles())

    def _click_add_folder_button(self) -> None:
        dialog = app_utils.MultiFolderDialog(self, self.worker.settings.tr("file_dialog:choose_folders"))

        # Do nothing if the dialog was cancelled
        if not dialog.exec():
            return

        # Pass paths as strings to be added
        self._add_folders(dialog.selectedFiles())

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

    def _click_cancel_button(self) -> None:
        if not self._dirty:
            self.reject()
            return

        result = QMessageBox.question(
            self,
            self.worker.settings.tr("dialog:cancel_path_change_confirm:title"),
            self.worker.settings.tr("dialog:cancel_path_change_confirm:body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self.reject()



    def accept(self):
        self.files_changed.emit(self._paths)
        self._clear_dirty()
        super().accept()

    def reject(self):
        self._clear_dirty()
        super().reject()