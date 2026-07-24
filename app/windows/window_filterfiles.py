from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QDialogButtonBox,
    QGroupBox, QLineEdit, QListWidget, QLabel
)
from PyQt6.QtGui import QBrush
from PyQt6.QtCore import Qt

from app.workers.worker_croc import CrocWorker
from app.managers.manager_sendfiles import SendableFileFolder



class FilterFilesDialog(QDialog):
    """Checkable tree for excluding files/folders, plus filetype exclusions."""

    def __init__(self, sendable: SendableFileFolder, worker: CrocWorker, parent=None):
        super().__init__(parent)

        self.worker = worker

        self.sendable = sendable

        self.setWindowTitle(self.worker.settings.tr("filetree:window:title"))
        self.setFixedSize(500, 500)

        self._build_central()
        self._connect_signals()
        
        self._populate_tree()
        self._populate_filetypes()
        self._refresh_filetype_colors()

    def _build_central(self):
        root = QVBoxLayout(self)
        root.setSpacing(8)

        tree_group = self._build_filetree_group()
        filetype_group = self._build_filetype_group()
        buttons_group = self._build_buttons_group()

        root.addWidget(tree_group)
        root.addWidget(filetype_group)
        root.addWidget(buttons_group)

    def _build_filetree_group(self) -> QGroupBox:
        self.tree_group = QGroupBox(self.worker.settings.tr("filetree:group:filetree_heading"))
        layout = QVBoxLayout(self.tree_group)

        self.tree_files = QTreeWidget()
        self.tree_files.setHeaderHidden(True)
        self.tree_files.setAnimated(True)

        btn_check_row = QHBoxLayout()
        self.btn_check_all = QPushButton(self.worker.settings.tr("generic:check_all"))
        self.btn_uncheck_all = QPushButton(self.worker.settings.tr("generic:uncheck_all"))

        layout.addWidget(self.tree_files)

        btn_check_row.addWidget(self.btn_check_all)
        btn_check_row.addWidget(self.btn_uncheck_all)
        layout.addLayout(btn_check_row)

        return self.tree_group

    def _build_filetype_group(self) -> QGroupBox:
        self.filetype_group = QGroupBox(self.worker.settings.tr("filetree:group:filetype_heading"))
        layout = QVBoxLayout(self.filetype_group)

        input_row = QHBoxLayout()

        self.lineedit_filetype = QLineEdit()
        self.lineedit_filetype.setPlaceholderText(".txt")

        self.btn_add_filetype = QPushButton(self.worker.settings.tr("generic:add"))

        self.list_filetypes = QListWidget()
        self.list_filetypes.setMaximumHeight(90)
        self.btn_remove_filetype = QPushButton(self.worker.settings.tr("filetree:btn:remove_filetype"))

        input_row.addWidget(self.lineedit_filetype)
        input_row.addWidget(self.btn_add_filetype)
        layout.addLayout(input_row)

        layout.addWidget(self.list_filetypes)
        layout.addWidget(self.btn_remove_filetype)

        return self.filetype_group

    def _build_buttons_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QHBoxLayout(group)

        self.btn_ok = QPushButton(self.worker.settings.tr("generic:ok"))
        self.btn_cancel = QPushButton(self.worker.settings.tr("generic:cancel"))

        layout.addStretch()
        layout.addWidget(self.btn_ok)
        layout.addWidget(self.btn_cancel)

        return group



    def _retranslate(self) -> None:
        self.setWindowTitle(self.worker.settings.tr("filetree:window:title"))

        self.tree_group.setTitle(self.worker.settings.tr("filetree:group:filetree_heading"))
        self.btn_check_all.setText(self.worker.settings.tr("generic:check_all"))
        self.btn_uncheck_all.setText(self.worker.settings.tr("generic:uncheck_all"))

        self.filetype_group.setTitle(self.worker.settings.tr("filetree:group:filetype_heading"))
        self.btn_add_filetype.setText(self.worker.settings.tr("generic:add"))
        self.btn_remove_filetype.setText(self.worker.settings.tr("filetree:btn:remove_filetype"))



    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.tree_files.itemChanged.connect(self._on_item_changed)

        self.btn_check_all.clicked.connect(
            lambda: self._set_all(Qt.CheckState.Checked)
        )
        self.btn_uncheck_all.clicked.connect(
            lambda: self._set_all(Qt.CheckState.Unchecked)
        )

        self.btn_add_filetype.clicked.connect(self._add_filetypes)
        self.lineedit_filetype.returnPressed.connect(self._add_filetypes)
        self.btn_remove_filetype.clicked.connect(self._remove_filetype)

        self.btn_ok.clicked.connect(self._apply_and_accept)
        self.btn_cancel.clicked.connect(self.reject)



    def _populate_tree(self):
        self.tree_files.clear()

        excluded = self.sendable.get_all_excluded_files() or set()
        self._populate_dir(None, self.sendable.root_path, excluded)

        if self.tree_files.topLevelItemCount():
            self.tree_files.topLevelItem(0).setExpanded(True)

        self._refresh_filetype_colors()

    def _populate_dir(self, parent, folder: Path, excluded: set[Path]):
        try:
            entries = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        for entry in entries:
            relative = entry.relative_to(self.sendable.root_path)

            # Check if this entry OR any of its ancestors is excluded
            is_excluded = any(
                relative == ex or ex in relative.parents
                for ex in excluded
            )

            state = Qt.CheckState.Unchecked if is_excluded else Qt.CheckState.Checked

            item = QTreeWidgetItem([entry.name])
            item.setCheckState(0, state)
            item.setData(0, Qt.ItemDataRole.UserRole, entry)

            if self._is_filetype_excluded(entry):
                item.setForeground(0, Qt.GlobalColor.red)

            if parent is None:
                self.tree_files.addTopLevelItem(item)
            else:
                parent.addChild(item)

            if entry.is_dir():
                self._populate_dir(item, entry, excluded)

    def _populate_filetypes(self):
        self.list_filetypes.clear()
        for ft in self.sendable.excluded_filetypes:
            self.list_filetypes.addItem(ft)

    def _is_filetype_excluded(self, path: Path) -> bool:
        """Return True if this file's extension is in the excluded filetypes list."""

        if path.is_dir():
            return False
        
        for i in range(self.list_filetypes.count()):
            if path.suffix.lower() == self.list_filetypes.item(i).text().lower():
                return True
            
        return False

    def _refresh_filetype_colors(self) -> None:
        def walk(item: QTreeWidgetItem):
            path: Path = item.data(0, Qt.ItemDataRole.UserRole)

            if path and self._is_filetype_excluded(path):
                item.setForeground(0, Qt.GlobalColor.red)
            else:
                item.setForeground(0, QBrush())

            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.tree_files.topLevelItemCount()):
            walk(self.tree_files.topLevelItem(i))



    def _on_item_changed(self, item, _col):
        self.tree_files.itemChanged.disconnect(self._on_item_changed)
        self._propagate(item, item.checkState(0))
        self.tree_files.itemChanged.connect(self._on_item_changed)

    def _propagate(self, item, state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self._propagate(child, state)

    def _set_all(self, state):
        self.tree_files.itemChanged.disconnect(self._on_item_changed)

        for i in range(self.tree_files.topLevelItemCount()):
            top = self.tree_files.topLevelItem(i)
            top.setCheckState(0, state)
            self._propagate(top, state)

        self.tree_files.itemChanged.connect(self._on_item_changed)


    def _add_filetype(self, text: str) -> None:
        normalized = text if text.startswith(".") else f".{text}"
        
        if not self.list_filetypes.findItems(normalized, Qt.MatchFlag.MatchExactly):
            self.list_filetypes.addItem(normalized)

    def _add_filetypes(self):
        """Add filetypes to exclude separated by commas."""

        text: str = self.lineedit_filetype.text()

        if not text:
            return

        filetypes: list[str] = self.lineedit_filetype.text().strip().split(",")

        if not filetypes:
            return

        for filetype in filetypes:
            self._add_filetype(filetype)

        self.lineedit_filetype.clear()
        self._refresh_filetype_colors()

    def _remove_filetype(self):
        for item in self.list_filetypes.selectedItems():
            self.list_filetypes.takeItem(self.list_filetypes.row(item))

        self._refresh_filetype_colors()



    def _apply_and_accept(self):
        self.sendable.clear_excluded_files()
        self._collect_unchecked(None)

        self.sendable.clear_excluded_filetypes()
        for i in range(self.list_filetypes.count()):
            self.sendable.add_excluded_filetype(self.list_filetypes.item(i).text())

        self.accept()

    def _collect_unchecked(self, parent):
        if parent is None:
            count = self.tree_files.topLevelItemCount()
            getter = self.tree_files.topLevelItem
        else:
            count = parent.childCount()
            getter = parent.child

        for i in range(count):
            item = getter(i)

            path: Path = item.data(0, Qt.ItemDataRole.UserRole)
            if item.checkState(0) == Qt.CheckState.Unchecked:
                self.sendable.add_excluded_file(path)
            else:
                self._collect_unchecked(item)