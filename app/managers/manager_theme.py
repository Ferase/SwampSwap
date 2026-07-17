import json
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QObject

from app.managers.manager_animation import AnimationManager

THEMES_FILE_PATH = Path.cwd() / "themes.json"



class SwampSwapPalette():
    """A wrapper class that makes creating palettes for Swamp Swap slightly easier."""

    def __init__(
            self,
            name: str,
            bg_front: list[int],
            bg_back: list[int],
            text: list[int],
            highlight: list[int],
            text_highlight: list[int],
            disabled: list[int],
            text_placeholder: list[int],

            anim_black: list[int],
            anim_white: list[int],
            anim_water: list[int],
            anim_box: list[int],
            anim_croc: list[int],
            anim_bird: list[int],
            anim_folder: list[int]
        ):

        # Palette display name
        self.name = name

        # Palette object and colors
        self.palette = QPalette()
        self.bg_front = QColor(*bg_front)
        self.bg_back = QColor(*bg_back)
        self.text = QColor(*text)
        self.highlight = QColor(*highlight)
        self.text_highlight = QColor(*text_highlight)
        self.disabled = QColor(*disabled)
        self.text_placeholder = QColor(*text_placeholder)

        # croc and bird palettes
        self.anim_black = QColor(*anim_black)
        self.anim_white = QColor(*anim_white)
        self.anim_water = QColor(*anim_water)
        self.anim_box = QColor(*anim_box)
        self.anim_croc = QColor(*anim_croc)
        self.anim_bird = QColor(*anim_bird)
        self.anim_folder = QColor(*anim_folder)

        # Pass init values to palette
        self.palette.setColor(QPalette.ColorRole.Window, self.bg_front)
        self.palette.setColor(QPalette.ColorRole.WindowText, self.text)
        self.palette.setColor(QPalette.ColorRole.Base, self.bg_back)
        self.palette.setColor(QPalette.ColorRole.AlternateBase, self.bg_front)
        self.palette.setColor(QPalette.ColorRole.ToolTipBase, self.bg_front)
        self.palette.setColor(QPalette.ColorRole.ToolTipText, self.text)
        self.palette.setColor(QPalette.ColorRole.Text, self.text)
        self.palette.setColor(QPalette.ColorRole.Button, self.bg_front)
        self.palette.setColor(QPalette.ColorRole.ButtonText, self.text)
        self.palette.setColor(QPalette.ColorRole.BrightText, self.text_highlight)
        self.palette.setColor(QPalette.ColorRole.Highlight, self.highlight)
        self.palette.setColor(QPalette.ColorRole.HighlightedText, self.text_highlight)
        self.palette.setColor(QPalette.ColorRole.PlaceholderText, self.text_placeholder)

        self.palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.Text,
            self.disabled
        )
        self.palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            self.disabled
        )



class SwampSwapPaletteList(list):
    """A subclass of list that handles containing SwampSwapPalette instances."""

    def __init__(self):
        super().__init__()

    def __getitem__(self, palette_name: str) -> SwampSwapPalette:
        """Get the palette by name."""

        return next((l for l in self if l.name.lower() == palette_name.lower()), None)
    
    def has_palette(self, palette_name: str) -> bool:
        """Check if the given palette exists in the list."""

        if self.__getitem__(palette_name):
            return True
        
        return False
    
    def get_list(self) -> list[str]:
        """Return the full list of all of the currently loaded palettes."""

        return [palette.name for palette in self]



class ThemeManager(QObject):
    """The main manager object for Swamp Swap's themes. It handles loading in each theme as well aschanging the program's styles in real time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.animation_manager = AnimationManager()

        self.palettes = SwampSwapPaletteList()
        self.selected_palette: SwampSwapPalette | None = None

        self._load_palettes()

    def _load_palettes(self) -> None:
        """Load palettes from the _PALETTES constant."""

        with open(THEMES_FILE_PATH, "r") as t:
            json_data = json.load(t)
            for palette in json_data:
                self.palettes.append(SwampSwapPalette(**palette))



    def select_theme(self, palette_name: str) -> None:
        """Applies the specified theme to the application's stylesheet."""

        # Get the theme
        theme = self.palettes[palette_name]

        # Fall back to the Pink theme if we somehow try to load an nonexistent theme
        if theme is None:
            theme = self.palettes["Swamp"]

        # Save to self and then apply via the application
        self.selected_palette = theme
        QApplication.setPalette(self.selected_palette.palette)

        self.animation_manager.apply_theme_colors(self._build_animation_color_map(theme))

    def _build_animation_color_map(self, theme: SwampSwapPalette) -> dict:
        """Maps GIF color slots to the given theme's color values."""

        return {
            "anim_black": theme.anim_black,
            "anim_white": theme.anim_white,
            "anim_water": theme.anim_water,
            "anim_box": theme.anim_box,
            "anim_croc": theme.anim_croc,
            "anim_bird": theme.anim_bird,
            "anim_folder": theme.anim_folder,
        }
    
    def get_theme_list(self) -> list[str]:
        """Returns a full list of all of the loaded palettes."""

        return self.palettes.get_list()