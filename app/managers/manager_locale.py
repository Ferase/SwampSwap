import json
from pathlib import Path
from typing import Any, SupportsIndex

from PyQt6.QtCore import QObject, pyqtSignal

import app.utils as app_utils



class SwampSwapLang():
    def __init__(self, dictionary: dict[str, Any] | None = None):
        if dictionary is None:
            return
        
        self.load(dictionary)

    def load(self, dictionary: dict[str, Any]) -> None:
        meta = dictionary.pop("_meta")
        self.language: str = meta["language"]
        self.author: str = meta["author"]
        self.version: str = meta["version"]

        self._locale_dict: dict[str, str] = dictionary
    
    def __getitem__(self, key: str) -> str:
        if key in self._locale_dict.keys():
            return self._locale_dict[key]

        return key

class SwampSwapLanguageList(list):
    def __init__(self):
        super().__init__()

    def __getitem__(self, lang_name: str) -> SwampSwapLang:
        return next((l for l in self if l.language.lower() == lang_name.lower()), None)
    
    def has_language(self, lang_name: str) -> bool:
        if self.__getitem__(lang_name):
            return True
        
        return False
    
    def get_list(self) -> list[str]:
        return [lang.language for lang in self]
    


class LocaleManager(QObject):

    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._lang_path: Path = app_utils.determine_filepath("lang", 2)

        self.langs: SwampSwapLanguageList = SwampSwapLanguageList()
        self.selected_lang: SwampSwapLang | None = None

        self._load_langs()

    def _load_langs(self) -> None:
        lang_files: list[Path] = list(self._lang_path.glob("*.json"))
        for lang_file in lang_files:
            with open(lang_file, "r") as l:
                json_data: dict[str, Any] = json.load(l)
                ss_language = SwampSwapLang(json_data)
                self.langs.append(ss_language)

    def reload_langs(self) -> None:
        self.langs.clear()
        self._load_langs()

    def get(self, key: str) -> str:
        if self.selected_lang is None:
            return key

        return self.selected_lang[key]
    
    def get_lang_list(self) -> list[str]:
        return self.langs.get_list()

    def select_lang(self, lang_name: str) -> None:
        lang = self.langs[lang_name]

        if lang is None:
            lang = self.langs["English"]

        self.selected_lang = lang
        self.language_changed.emit(self.selected_lang.language)