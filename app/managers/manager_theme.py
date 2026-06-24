from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QWheelEvent, QPalette, QColor
from PyQt6.QtCore import Qt, QObject, pyqtSignal



class SwampSwapPalette():
    def __init__(
            self,
            name: str,
            bg_front: QColor,
            bg_back: QColor,
            text: QColor,
            highlight: QColor,
            text_highlight: QColor,
            disabled: QColor,
            text_placeholder: QColor
        ):

        self.name = name

        self.palette = QPalette()
        self.bg_front: QColor = bg_front
        self.bg_back: QColor = bg_back
        self.text: QColor = text
        self.highlight: QColor = highlight
        self.text_highlight: QColor = text_highlight
        self.disabled: QColor = disabled
        self.text_placeholder: QColor = text_placeholder

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



_PALETTES: list[SwampSwapPalette] = [
    SwampSwapPalette(
        name="Deep Dark",
        bg_front=QColor(22, 22, 22),
        bg_back=QColor(8, 8, 8),
        text=QColor(255, 255, 255),
        highlight=QColor(170, 30, 128),
        text_highlight=QColor(255, 255, 255),
        disabled=QColor(60, 60, 60),
        text_placeholder=QColor(180, 180, 180)
    ),
    SwampSwapPalette(
        name="Dark",
        bg_front=QColor(45, 45, 45),
        bg_back=QColor(30, 30, 30),
        text=QColor(220, 220, 220),
        highlight=QColor(170, 30, 128),
        text_highlight=QColor(255, 255, 255),
        disabled=QColor(120, 120, 120),
        text_placeholder=QColor(120, 120, 120)
    ),
    SwampSwapPalette(
        name="Light",
        bg_front=QColor(215, 215, 215),
        bg_back=QColor(220, 220, 220),
        text=QColor(30, 30, 30),
        highlight=QColor(170, 30, 128),
        text_highlight=QColor(255, 255, 255),
        disabled=QColor(120, 120, 120),
        text_placeholder=QColor(60, 60, 60)
    ),
    SwampSwapPalette(
        name="Steam 1.0",
        bg_front=QColor(75, 88, 68),
        bg_back=QColor(62, 70, 55),
        text=QColor(222, 223, 214),
        highlight=QColor(196, 181, 80),
        text_highlight=QColor(0, 0, 0),
        disabled=QColor(41, 44, 33),
        text_placeholder=QColor(216, 222, 211)
    ),
    SwampSwapPalette(
        name="Pink",
        bg_front=QColor(50, 0, 34),
        bg_back=QColor(36, 0, 23),
        text=QColor(255, 233, 255),
        highlight=QColor(170, 30, 128),
        text_highlight=QColor(255, 255, 255),
        disabled=QColor(206, 144, 182),
        text_placeholder=QColor(206, 144, 182)
    ),
    SwampSwapPalette(
        name="Red",
        bg_front=QColor(50, 0, 0),
        bg_back=QColor(36, 0, 0),
        text=QColor(255, 233, 255),
        highlight=QColor(170, 30, 30),
        text_highlight=QColor(255, 255, 255),
        disabled=QColor(206, 144, 144),
        text_placeholder=QColor(206, 144, 144)
    )
]



class SwampSwapPaletteList(list):
    def __init__(self):
        super().__init__()

    def __getitem__(self, palette_name: str) -> SwampSwapPalette:
        return next((l for l in self if l.name.lower() == palette_name.lower()), None)
    
    def has_palette(self, palette_name: str) -> bool:
        if self.__getitem__(palette_name):
            return True
        
        return False
    
    def get_list(self) -> list[str]:
        return [palette.name for palette in self]



class ThemeManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.palettes = SwampSwapPaletteList()
        self.selected_palette: SwampSwapPalette | None = None

        self._define_palettes()

    def _define_palettes(self) -> None:
        for pallete in _PALETTES:
            self.palettes.append(pallete)



    def select_theme(self, palette_name: str) -> None:
        theme = self.palettes[palette_name]

        if theme is None:
            theme = self.langs["Dark"]

        self.selected_palette = theme
        QApplication.setPalette(self.selected_palette.palette)
    
    def get_theme_list(self) -> list[str]:
        return self.palettes.get_list()