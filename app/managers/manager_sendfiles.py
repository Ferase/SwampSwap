from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

import app.utils as app_utils
from app.workers.worker_croc import CrocWorker



class SendableFileFolder():
    def __init__(self, path: Path | str):
        self.root_path = Path(path)
        self.excluded_filetypes: dict[str, set[Path]] = {}
        self.excluded_files: set[Path] = set()

        self.is_folder: bool = self._is_folder()

    def __hash__(self):
        return hash(self.root_path)

    def __eq__(self, other):
        if isinstance(other, SendableFileFolder):
            return self.root_path == other.root_path
        
        return False

    def _is_folder(self) -> bool:
        return self.root_path.is_dir()

    

    def add_excluded_file(self, path: Path) -> None:
        if not self.is_folder:
            return

        if not path.is_relative_to(self.root_path):
            return

        relative_path: Path = path.relative_to(self.root_path)

        self.excluded_files.add(relative_path)

    def remove_excluded_file(self, path: Path) -> None:
        if not self.is_folder:
            return
        
        if path in self.excluded_files:
            self.excluded_files.remove(path)

    def add_excluded_filetype(self, filetype: str) -> None:
        if not self.is_folder:
            return
        
        normalized_filetype: str = filetype if filetype.startswith(".") else f".{filetype}"

        for file in self.root_path.rglob("*" + normalized_filetype):
            relative_path: Path = file.relative_to(self.root_path)

            if normalized_filetype in self.excluded_filetypes.keys():
                self.excluded_filetypes[normalized_filetype].add(relative_path)
            else:
                self.excluded_filetypes[normalized_filetype] = {relative_path}

    def remove_excluded_filetype(self, filetype: str) -> None:
        if not self.is_folder:
            return
        
        normalized_filetype: str = filetype if filetype.startswith(".") else f".{filetype}"

        if normalized_filetype in self.excluded_filetypes.keys():
            self.excluded_filetypes.pop(normalized_filetype)

    def clear_excluded_files(self) -> None:
        self.excluded_files = set()

    def clear_excluded_filetypes(self) -> None:
        self.excluded_filetypes.clear()



    def are_no_exclusions(self) -> bool:
        return not (self.combine_excluded_files() or self.combine_excluded_filetypes())

    

    def get_root_path(self) -> Path:
        return self.root_path

    def combine_excluded_filetypes(self) -> set[Path]:
        if not self.is_folder:
            return set()

        final_set: set[Path] = set()
        for exlusion_set in self.excluded_filetypes.values():
            final_set.update(exlusion_set)

        return final_set

    def get_all_excluded_files(self) -> set[Path]:
        if not self.is_folder:
            return set()
        
        return self.excluded_files | self.combine_excluded_filetypes()



class SendFilesManager(QObject):

    selected_files_changed = pyqtSignal(set)
    file_count_updated = pyqtSignal(dict)

    def __init__(self, worker: CrocWorker, parent=None):
        super().__init__(parent)

        self.worker = worker

        self.selected_paths: set[SendableFileFolder] = set()
        self.selected_paths_count: dict[str, int] = {
            "files": 0,
            "folders": 0
        }

    def _sort_selected_paths(self) -> None:
        if not self.selected_paths:
            self.calculate_file_folder_count()
            return
        
        folder_set: set[SendableFileFolder] = set()
        file_set: set[SendableFileFolder] = set()
        for item in self.selected_paths:
            if item.is_folder:
                folder_set.add(item)
            else:
                file_set.add(item)

        self.selected_paths = folder_set | file_set
        self.calculate_file_folder_count()
        self.selected_files_changed.emit(self.selected_paths)

    def _add_to_sendable_file_set(self, sendable: SendableFileFolder) -> None:
        self.selected_paths.add(sendable)
        self._sort_selected_paths()

    def _remove_from_sendable_file_set(self, sendable: SendableFileFolder) -> None:
        if not sendable in self.selected_paths:
            return

        self.selected_paths.remove(sendable)
        self._sort_selected_paths()

    def _find_sendable(self, path: Path) -> SendableFileFolder | None:
        for s in self.selected_paths:
            if s.root_path == path:
                return s
            
        return None

    def _is_path_relative_to_paths(self, target_path: Path, path_set: set[Path]) -> bool:
        for path in path_set:
            if target_path.is_relative_to(path):
                return True

        return False

    def calculate_file_folder_count(self) -> None:
        file_count = 0
        folder_count = 0

        if not self.selected_paths:
            self.selected_paths_count["files"] = 0
            self.selected_paths_count["folders"] = 0
            self.file_count_updated.emit(self.selected_paths_count)
            return
        
        for sendable in self.selected_paths:
            path = sendable.root_path

            if path.is_dir():
                excluded_files = sendable.get_all_excluded_files()

                for item in path.rglob("*"):
                    relative = item.relative_to(path)
                    
                    if relative in excluded_files:
                        continue

                    if self._is_path_relative_to_paths(relative, excluded_files):
                        continue

                    if item.is_file():
                        file_count += 1
                    elif item.is_dir():
                        folder_count += 1

            else:
                file_count += 1

        self.selected_paths_count["files"] = file_count
        self.selected_paths_count["folders"] = folder_count
        self.file_count_updated.emit(self.selected_paths_count)



    def _connect_signals(self) -> None:
        pass



    def get_sendable(self, path: Path) -> SendableFileFolder | None:
        return self._find_sendable(path)

    def set_paths(self, paths: set[Path] | set[SendableFileFolder]) -> None:
        self.selected_paths = [SendableFileFolder(path) if not isinstance(path, SendableFileFolder) else path for path in paths]
        self._sort_selected_paths()

    def add_path(self, path: Path | SendableFileFolder) -> None:
        if not isinstance(path, SendableFileFolder):
            path = SendableFileFolder(path)

        self._add_to_sendable_file_set(path)

    def add_paths(self, paths: set[Path] | set[SendableFileFolder]) -> None:
        for path in paths:
            self.add_path(path)

    def remove_path(self, path: Path) -> None:
        sendable = self._find_sendable(path)
        if sendable:
            self.selected_paths.discard(sendable)
            self._sort_selected_paths()

    def remove_paths(self, paths: set[Path]) -> None:
        for path in paths:
            self.remove_path(path)

    def clear_selected_file_set(self) -> None:
        self.selected_paths.clear()
        self._sort_selected_paths()



    def is_path_in_selected(self, path: Path) -> bool:
        return bool(SendableFileFolder(path) in self.selected_paths)

    def is_path_already_accounted_for(self, path: Path) -> bool:
        """Checks to see if the provided path might be a child of an already provided path. If it is, it will not be added since its redundant."""

        for sendable in self.selected_paths:
            if self.is_path_in_selected(path) or path.is_relative_to(sendable.get_root_path()):
                return True

        return False