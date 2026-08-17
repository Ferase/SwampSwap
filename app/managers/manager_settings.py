import json
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from app.managers.manager_locale import LocaleManager
from app.managers.manager_theme import ThemeManager
import app.utils as app_utils

_SETTINGS_VERSION: int = 1

# Default settings
_DEFAULTS: dict[str, bool | str | float] = {
    # General
    "startup_console": False,
    "startup_croc_updates_check": True,
    "startup_swampswap_updates_check": True,

    # UI
    "lang": "English",
    "theme": "Swamp",
    "animation_matches_theme": True,
    "enable_sound": True,
    "sound_volume": 0.5,

    # Send
    "raise_filter_window": False,
    "zip": False,
    "hash": "xxhash",
    "git": False,
    "nolocal": False,
    "nomulti": False,
    "clear_filelist_after": False,

    # Receive
    "default_receive_path": str(app_utils.determine_received_path("received")),
    "overwrite": False,

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
    "local": False,

    # Advabced
    "croc_path": "croc"
}

# Lookup table for croc flags
_LOOKUP_TABLE_GENERAL: dict[str, str] = {
    # Receive
    "overwrite": "--overwrite",

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

# Lookup table for croc's send-only flags
_LOOKUP_TABLE_SEND: dict[str, str] = {
    "zip": "--zip",
    "hash": "--hash",
    "git": "--git",
    "nolocal": "--no-local",
    "nomulti": "--no-multi"
}



class SettingsManager(QObject):
    """A mananager class that handles loading and applying settings as well as handing off flags to CrocWorker."""

    settings_saved = pyqtSignal()

    def __init__(self, app_name: str, app_version: str, parent=None):
        super().__init__(parent)

        self.app_name = app_name
        self.app_version = app_version
        self.settings_file_path: Path = app_utils.get_settings_path(self.app_name) / "settings.json"

        # Settings integrity
        self.settings_version_baseline: int = _SETTINGS_VERSION
        self.settings_version: int | None = None

        # General
        self.startup_console: bool | None = None
        self.startup_croc_updates_check: bool | None = None
        self.startup_swampswap_updates_check: bool | None = None

        # UI
        self.lang: str | None = None
        self.theme: str | None = None
        self.animation_matches_theme: bool | None = None
        self.enable_sound: bool | None = None
        self.sound_volume: float | None = None

        # Send
        self.raise_filter_window: bool | None = None
        self.zip: bool | None = None
        self.hash: str | None = None
        self.hash_list: list[str] = ["xxhash", "imohash", "md5", "highway"]
        self.git: bool | None = None
        self.nolocal: bool | None = None
        self.nomulti: bool | None = None
        self.clear_filelist_after: bool | None = None

        # Receive
        self.default_receive_path: str | None = None
        self.overwrite: bool | None = None

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

        # Advanced
        self.croc_path: str | None = None

        # Locale manager and language list
        self.locale_manager = LocaleManager()
        self.lang_list: list[str] = self.locale_manager.get_lang_list()

        # The emanager and list
        self.theme_manager = ThemeManager()
        self.theme_list: list[str] = self.theme_manager.get_theme_list()

        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from settings.json file in program root. Load defaults otherwise."""

        self.set_defaults()
        
        if not self.settings_file_path.exists():
            return

        # Open settings.json and pull out changed settings
        with open(self.settings_file_path, "r") as s:
            json_data: dict[str, bool | str | float] = json.load(s)
            self.set_all_from_dict(json_data)

    def _get_defualt_receive_path(self) -> str:
        defualt_path: str = str(app_utils.determine_received_path("received"))
        return defualt_path



    def set_all_from_dict(self, dictionary: dict[str, bool | str | float]) -> None:
        """Runs through all of the settings in the provided dictionary and changes any matching attributes of this manager to the values present in the dictionary."""

        # If this manager has the attribute, set it using the value in the dictionary
        for key, value in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.change_language()
        self.change_theme()
        self.change_animation_matches_theme()

    def set_defaults(self) -> None:
        """Passes the _DEFAULTS constant to set_all_from_dict(), resetting all settings to default."""

        self.set_all_from_dict(_DEFAULTS)
        self.default_receive_path = self._get_defualt_receive_path()

    def serialize_to_dict(self) -> dict[str, bool | str | float]:
        """Serialize the settings to a dict[str, bool | str | float]."""

        new_dict: dict[str, bool | str | float] = {
            "settings_version": self.settings_version_baseline
        }

        # Iterate through the keys of the default settings since they contain all possible settings
        for key in _DEFAULTS.keys():
            if hasattr(self, key):
                # Get the value of the setting (key) in the manager
                value: str | bool | None = getattr(self, key)

                # If no vlaue was captured, get the default value
                if value is None:
                    value = _DEFAULTS[key]

                # Pass the value to the output dictionary
                new_dict[key] = value

        return new_dict
    
    def save_settings(self) -> None:
        """Serializes settings and then saves all settings to a new settings.json file."""

        new_dict: dict[str, bool | str | float] = self.serialize_to_dict()

        # Open the settings file and write the dictionary to it
        with open(self.settings_file_path, "w") as s:
            json.dump(new_dict, s, indent=4, ensure_ascii=False)

        self.settings_saved.emit()

    def save_single_setting(self, key: str, value: bool | str | float) -> None:
        """Save a single setting into settings.json"""

        setting: dict[str, bool | str | float] = {
            key: value
        }

        # Try to re-read the JSON file if it exists, otherwise just write it
        try:
            with open(self.settings_file_path, "r") as s1:
                data: dict[str, bool | str | float] = json.load(s1)
                data.update(setting)
                setting = data
        except FileNotFoundError:
            pass

        # Open the settings file and write the dictionary to it
        with open(self.settings_file_path, "w") as s2:
            json.dump(setting, s2, indent=4, ensure_ascii=False)

        self.settings_saved.emit()

    def get_changed_settings(self) -> list[str]:
        """Gets a list of the names of settings that are no longer default."""

        changed_settings: list[str] = []

        # Iterat ethrough the default dictionary and test each attribute of the manager
        for key, value in _DEFAULTS.items():
            if hasattr(self, key):
                if getattr(self, key) != value:
                    changed_settings.append(key)
                
        return changed_settings

    def are_settings_default(self) -> bool:
        """Return true if the settings are totally default."""

        # If no changed settings are found, then everything's default.
        changed_settings: list[str] = self.get_changed_settings()

        return not bool(changed_settings)



    def build_general_flags(self) -> list[str]:
        """Build the flags that will be sent to croc when sending or receiving files."""

        flags: list[str] = []

        # Get the corresponding flag string for each setting
        for setting_name, flag_name in _LOOKUP_TABLE_GENERAL.items():
            # Get the value of the current setting as well as its default
            value = getattr(self, setting_name)
            default = _DEFAULTS[setting_name]

            # Skip settings that are default
            if value == default:
                continue

            # If the flag is a boolean expression, just add the flag
            if isinstance(value, bool):
                if value:
                    flags.append(flag_name)
                    continue

            # If the flag is a value, ensure it's not empty or (somehow) None and then extend the flag list with the flag name and value
            if value not in (None, ""):
                flags.extend([flag_name, str(value)])

        return flags
    
    def build_send_flags(self) -> list[str]:
        """Build the flags that will be sent to croc strictly when sending files."""

        flags: list[str] = []

        # Get the corresponding flag string for each setting
        for setting_name, flag_name in _LOOKUP_TABLE_SEND.items():
            # Get the value of the current setting as well as its default
            value = getattr(self, setting_name)
            default = _DEFAULTS[setting_name]

            # Skip settings that are default
            if value == default:
                continue

            # If the flag is a boolean expression, just add the flag
            if isinstance(value, bool):
                if value:
                    flags.append(flag_name)
                    continue

            # If the flag is a value, ensure it's not empty or (somehow) None and then extend the flag list with the flag name and value
            if value not in (None, ""):
                flags.extend([flag_name, str(value)])

        return flags



    def change_language(self) -> None:
        """Tell the language manager to change the current language."""

        self.locale_manager.select_lang(self.lang)

    def tr(self, text: str) -> str:
        """Shortcut to locale_manager.get() for getting translated strings from locale keys."""

        return self.locale_manager.get(text)
    


    def change_theme(self) -> None:
        """Tell the theme manager to change the current theme."""

        self.theme_manager.select_theme(self.theme)

    def change_animation_matches_theme(self) -> None:
        """Tell the theme manager whether animations should be recolored to match the theme."""

        self.theme_manager.set_animation_matches_theme(self.animation_matches_theme)



    def delete_settings_file(self) -> None:
        if self.settings_file_path.exists():
            self.settings_file_path.unlink()