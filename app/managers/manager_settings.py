import json
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal

from app.managers.manager_locale import LocaleManager
import app.utils as app_utils

_DEFAULTS: dict[str, Any] = {
    # General
    "lang": "English",
    "startup_console": False,

    # Relay
    "relay": "178.105.79.46:9009",
    "relay6": "[2a01:4f9:c013:7b04::1]:9009",
    "password": "pass123",

    # Network
    "curve": "p256",
    "ip": "",
    "multicast": "239.255.255.250",
    "socks5": "",
    "connect": "",
    "throttleupload": "",

    # Flags
    "yes": False,
    "classic": False,
    "internaldns": False,
    "nocompress": False,
    "local": False
}

_LOOKUP_TABLE: dict[str, str] = {
    # Relay
    "relay": "--relay",
    "relay6": "--relay6",
    "password": "--pass",

    # Network
    "curve": "--curve",
    "ip": "--ip",
    "multicast": "--multicast",
    "socks5": "--socks5",
    "connect": "--connect",
    "throttleupload": "--throttleUpload",

    # Flags
    "yes": "--yes",
    "classic": "--classic",
    "internaldns": "--internal-dns",
    "nocompress": "--no-compress",
    "local": "--local"
}



class SettingsManager():
    def __init__(self, app_name: str, app_version: str):
        self._settings_file_path: Path = app_utils.determine_filepath("settings.json", 2)

        self.app_name = app_name
        self.app_version = app_version

        # General
        self.lang: str | None = None
        self.startup_console: bool | None = None

        # Relays
        self.relay: str | None = None
        self.relay6: str | None = None
        self.password: str | None = None

        # Network
        self.curve: str | None = None
        self.curve_list: list[str] = ["p256", "p384", "p521", "siec", "ed25519"]
        self.ip: str | None = None
        self.multicast: str | None = None
        self.socks5: str | None = None
        self.connect: str | None = None
        self.throttleupload: str | None = None

        # Flags
        self.yes: bool | None = None
        self.classic: bool | None = None
        self.internaldns: bool | None = None
        self.nocompress: bool | None = None
        self.local: bool | None = None

        self.locale_manager = LocaleManager()
        self.lang_list: list[str] = self.locale_manager.get_lang_list()

        self._load_settings()

    def _load_settings(self) -> None:
        self.set_defaults()
        
        if not self._settings_file_path.exists():
            return

        with open(self._settings_file_path, "r") as s:
            json_data: dict[str, Any] = json.load(s)
            self.set_all_from_dict(json_data)



    def set_all_from_dict(self, dictionary: dict[str, Any]) -> None:
        for key, value in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.change_language()

    def set_defaults(self) -> None:
        self.set_all_from_dict(_DEFAULTS)

    def serialize_to_dict(self) -> dict[str, Any]:
        new_dict: dict[str, Any] = {}

        for key in _DEFAULTS.keys():
            if hasattr(self, key):
                value: str | bool | None = getattr(self, key)

                if value is None:
                    value = _DEFAULTS[key]

                new_dict[key] = value

        return new_dict
    
    def save_settings(self) -> None:
        new_dict: dict[str, Any] = self.serialize_to_dict()

        with open(self._settings_file_path, "w") as s:
            json.dump(new_dict, s, indent=4, ensure_ascii=False)

    def save_single_setting(self, key: str, value: Any) -> None:
        setting: dict[str, Any] = {
            key: value
        }
        with open(self._settings_file_path, "w") as s:
            json.dump(setting, s, indent=4, ensure_ascii=False)

    def get_changed_settings(self) -> list[str]:
        changed_settings: list[str] = []
        for key, value in _DEFAULTS.items():
            if hasattr(self, key):
                if getattr(self, key) != value:
                    changed_settings.append(key)
                
        return changed_settings

    def are_settings_default(self) -> bool:
        changed_settings: list[str] = self.get_changed_settings()
        return not bool(changed_settings)



    def build_flags(self) -> list[str]:
        flags: list[str] = []

        for setting_name, flag_name in _LOOKUP_TABLE.items():
            value = getattr(self, setting_name)
            default = _DEFAULTS[setting_name]

            # Skip defaults
            if value == default:
                continue

            # Boolean flag
            if isinstance(value, bool):
                if value:
                    flags.append(flag_name)

            # Value flag
            elif value not in (None, ""):
                flags.extend([flag_name, str(value)])

        return flags



    def change_language(self) -> None:
        self.locale_manager.select_lang(self.lang)

    def tr(self, text: str) -> str:
        return self.locale_manager.get(text)