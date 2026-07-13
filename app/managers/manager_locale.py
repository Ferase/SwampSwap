import json
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

import app.utils as app_utils



class SwampSwapLang():
    """A class for storing language strings from a dictionary and making them callable via subscripting. Also stores metadata about the translation."""

    def __init__(self, dictionary: dict[str, dict[str, str] | str] | None = None):
        if dictionary is None:
            return
        
        self.load(dictionary)

    def load(self, dictionary: dict[str, dict[str, str] | str]) -> None:
        """Loads a provided dictionary of language strings and store metadata for this translation."""

        # Pop off the metadata and pass it into class variables
        meta = dictionary.pop("_meta")
        self.language: str = meta["language"]
        self.author: str = meta["author"]

        self._locale_dict: dict[str, str] = dictionary
    
    def __getitem__(self, key: str) -> str:
        """Get a translated string from a key"""

        # If the key exists, return the corresponding text
        if key in self._locale_dict.keys():
            return self._locale_dict[key]

        # Retrun the key itself as a fallback
        return key

class SwampSwapLanguageList(list):
    """A list subclass made to store SwampSwapLang instances."""

    def __init__(self):
        super().__init__()

    def __getitem__(self, lang_name: str) -> SwampSwapLang:
        """Gets the language with the name pertaining to the given language name."""

        return next((l for l in self if l.language.lower() == lang_name.lower()), None)
    
    def has_language(self, lang_name: str) -> bool:
        """Check if a specific language has been loaded."""

        if self.__getitem__(lang_name):
            return True
        
        return False
    
    def get_list(self) -> list[str]:
        """Return the full list of languages."""

        return [lang.language for lang in self]
    


class LocaleManager(QObject):
    """A manager object for Swamp Swap's locale system. Acts as an easy-to-use wrapper that holds and switches the selected language and pulls translated phrases on demand."""

    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self._lang_path: Path = app_utils.determine_filepath("lang", 2)

        self.langs: SwampSwapLanguageList = SwampSwapLanguageList()
        self.selected_lang: SwampSwapLang | None = None

        self._load_langs()

    def _load_langs(self) -> None:
        """Load all language files."""

        # Get all JSON files, then open each one and create a SwampSwapLang for it
        lang_files: list[Path] = list(self._lang_path.glob("*.json"))
        for lang_file in lang_files:
            with open(lang_file, "r") as l:
                json_data: dict[str, dict[str, dict[str, str] | str]] = json.load(l)
                ss_language = SwampSwapLang(json_data)
                self.langs.append(ss_language)

    def reload_langs(self) -> None:
        """Reload all fo the language files."""

        self.langs.clear()
        self._load_langs()

    def get(self, key: str) -> str:
        """Get a translated phrase from the selected language."""

        if self.selected_lang is None:
            return key

        return self.selected_lang[key]
    
    def get_lang_list(self) -> list[str]:
        """Get a full list of all the loaded languages."""

        return self.langs.get_list()

    def select_lang(self, lang_name: str) -> None:
        """Select a new current language by name."""

        # Get the current language as SwampSwapLang or None if it isn't found
        lang: SwampSwapLang | None = self.langs[lang_name]

        # Default to English if the language is invalid
        if lang is None:
            lang = self.langs["English"]

        self.selected_lang = lang
        self.language_changed.emit(self.selected_lang.language)