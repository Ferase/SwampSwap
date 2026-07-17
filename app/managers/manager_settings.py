import json
from pathlib import Path

from app.managers.manager_locale import LocaleManager
from app.managers.manager_theme import ThemeManager
import app.utils as app_utils

# Default settings
_DEFAULTS: dict[str, bool | str] = {
    # General
    "lang": "English",
    "theme": "Swamp",
    "startup_console": False,
    "startup_croc_updates_check": True,
    "startup_swampswap_updates_check": True,

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

# Lookup table for croc flags
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
    """A mananager class that handles loading and applying settings as well as handing off flags to CrocWorker."""

    def __init__(self, app_name: str, app_version: str):
        self._settings_file_path: Path = app_utils.determine_filepath("settings.json", 2)

        self.app_name = app_name
        self.app_version = app_version

        # General
        self.lang: str | None = None
        self.theme: str | None = None
        self.startup_console: bool | None = None
        self.startup_croc_updates_check: bool | None = None
        self.startup_swampswap_updates_check: bool | None = None

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

        # Locale manager and language list
        self.locale_manager = LocaleManager()
        self.lang_list: list[str] = self.locale_manager.get_lang_list()

        # The emanager and list
        self.theme_manager = ThemeManager()
        self.theme_list: list[str] = self.theme_manager.get_theme_list()

        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from settings.json file in program root. Load defaults otherwise."""

        self.set_defaults()
        
        if not self._settings_file_path.exists():
            return

        # Open settings.json and pull out changed settings
        with open(self._settings_file_path, "r") as s:
            json_data: dict[str, bool | str] = json.load(s)
            self.set_all_from_dict(json_data)



    def set_all_from_dict(self, dictionary: dict[str, bool | str]) -> None:
        """Runs through all of the settings in the provided dictionary and changes any matching attributes of this manager to the values present in the dictionary."""

        # If this manager has the attribute, set it using the value in the dictionary
        for key, value in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.change_language()
        self.change_theme()

    def set_defaults(self) -> None:
        """Passes the _DEFAULTS constant to set_all_from_dict(), resetting all settings to default."""

        self.set_all_from_dict(_DEFAULTS)

    def serialize_to_dict(self) -> dict[str, bool | str]:
        """Serialize the settings to a dict[str, bool | str]."""

        new_dict: dict[str, bool | str] = {}

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

        new_dict: dict[str, bool | str] = self.serialize_to_dict()

        # Open the settings file and write the dictionary to it
        with open(self._settings_file_path, "w") as s:
            json.dump(new_dict, s, indent=4, ensure_ascii=False)

    def save_single_setting(self, key: str, value: bool | str) -> None:
        """Save a single setting into settings.json"""

        setting: dict[str, bool | str] = {
            key: value
        }

        # Try to re-read the JSON file if it exists, otherwise just write it
        try:
            with open(self._settings_file_path, "r") as s1:
                data: dict[str, bool | str] = json.load(s1)
                data.update(setting)
                setting = data
        except FileNotFoundError:
            pass

        # Open the settings file and write the dictionary to it
        with open(self._settings_file_path, "w") as s2:
            json.dump(setting, s2, indent=4, ensure_ascii=False)

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



    def build_flags(self) -> list[str]:
        """Build the flags that will be sent to croc when sending or receiving files."""

        flags: list[str] = []

        # Get the corresponding flag string for each setting
        for setting_name, flag_name in _LOOKUP_TABLE.items():
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