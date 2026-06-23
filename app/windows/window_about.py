import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QCheckBox,
    QGroupBox, QFileDialog, QTextEdit, QAbstractItemView,
    QSizePolicy, QApplication, QScrollArea, QFrame,
    QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QDir, QUrl
from PyQt6.QtGui import QFont, QPixmap, QFont, QPalette, QColor, QDesktopServices

import app.utils as app_utils
from app.enums import CrocState, CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.managers.manager_locale import SwampSwapLang, SwampSwapLanguageList

_CROC_DEVELOPERS = ["Zack Schollz"]
_UI_DEVELOPERS = ["Ferase"]
_TESTERS = ["OctoToon"]



class AboutWindow(QDialog):

    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self._credit_labels: dict[str, QLabel] = {}
        self.bold_font = QFont()
        self.bold_font.setBold(True)

        self.worker = worker

        # Define window title and size
        self.setWindowTitle(self.worker.settings.tr("about:window:title"))
        self.setFixedSize(480, 350)

        # Build UI
        self._build_central()

        self._connect_signals()

    # Construct the UI
    def _build_central(self) -> None:
        # Create box layout container
        root = QGridLayout(self)
        root.setSpacing(8)

        hero_group = self._build_hero_group()
        scrollarea = self._build_scrollable_group()
        buttons_group = self._build_buttons()

        # Add widgets to box layout
        root.addWidget(hero_group, 0, 0)
        root.addWidget(scrollarea, 0, 1)
        root.addWidget(buttons_group, 1, 0, 1, -1)

    def _build_hero_group(self) -> QScrollArea:
        group = QGroupBox()
        layout = QVBoxLayout(group)

        group.setMaximumWidth(200)
        
        border_color: QColor = QApplication.palette().color(QPalette.ColorRole.Highlight).toRgb()
        border_color_css: str = f"rgb({border_color.red()}, {border_color.green()}, {border_color.blue()})"

        group.setStyleSheet("""
            QGroupBox {
                border-top: 0px solid transparent;
                border-left: 0px solid transparent;
                border-bottom: 0px solid transparent;
                border-right: 1px solid """ + border_color_css + ";}")
        
        layout.setContentsMargins(0, 0, 30, 0)

        image_size: int = 128

        label_icon = QLabel()
        label_icon.setFixedSize(image_size, image_size)
        label_icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        pixmap = QPixmap(app_utils.determine_icon_filepath("icon.ico", 2)).scaled(
            image_size, image_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        label_icon.setPixmap(pixmap)

        self.label_name = QLabel(self.worker.settings.app_name)
        hero_font = QFont()
        hero_font.setBold(True)
        hero_font.setPointSize(16)
        self.label_name.setFont(hero_font)
        self.label_name.setWordWrap(True)

        self.label_version = QLabel(f"GUI version {self.worker.settings.app_version}")
        self.label_version.setWordWrap(True)

        self.label_croc_version = QLabel(self.worker.croc_version)
        self.label_croc_version.setWordWrap(True)

        self.disclaimer_label = QLabel(self.worker.settings.tr("about:disclaimer"))
        self.disclaimer_label.setWordWrap(True)

        layout.addWidget(label_icon)
        layout.addWidget(self.label_name)
        layout.addWidget(self.label_version)
        layout.addWidget(self.label_croc_version)
        layout.addStretch()
        layout.addWidget(self.disclaimer_label)

        return group

    def _build_scrollable_group(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        credits_group = self._build_credits_group()
        links_group = self._build_links_group()

        layout.addWidget(credits_group)
        layout.addWidget(links_group)

        layout.addStretch()

        scroll.setWidget(widget)

        return scroll
    
    # Credits
    def _build_credits_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)
        
        app_utils.hide_group_box_border(group)
        
        credits_croc = self._build_single_credit(self.worker.settings.tr("about:credits:croc"), _CROC_DEVELOPERS)
        credits_ui_developers = self._build_single_credit(self.worker.settings.tr("about:credits:ui_developers"), _UI_DEVELOPERS)
        credits_testers = self._build_single_credit(self.worker.settings.tr("about:credits:testers"), _TESTERS)
        credits_languages = self._build_single_credit(self.worker.settings.tr("about:credits:languages"), self._get_language_credits_list())

        layout.addWidget(credits_croc)
        layout.addWidget(credits_ui_developers)
        layout.addWidget(credits_testers)
        layout.addWidget(credits_languages)

        return group
    
    # Links
    def _build_links_group(self) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)
        
        app_utils.hide_group_box_border(group)
        
        self.btn_github_croc = QPushButton("GitHub (croc)")
        self.btn_github_croc.setMinimumHeight(50)

        self.btn_github_swampswap = QPushButton("GitHub (SwampSwap)")
        self.btn_github_swampswap.setMinimumHeight(50)

        layout.addWidget(self.btn_github_croc)
        layout.addWidget(self.btn_github_swampswap)

        return group
    
    def _build_buttons(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        self.btn_close = QPushButton(self.worker.settings.tr("generic:close"))

        layout.addStretch()
        layout.addWidget(self.btn_close)

        return widget
    
    def _build_single_credit(self, label_key: str, credits_list: list[str]) -> QGroupBox:
        group = QGroupBox()
        layout = QVBoxLayout(group)
        
        app_utils.hide_group_box_border(group)
        
        label = QLabel(label_key)
        label.setFont(self.bold_font)
        self._credit_labels[label_key] = label

        layout.addWidget(label)

        for idx, credit in enumerate(credits_list):
            label_credit = QLabel(f"    {credit}")
            layout.addWidget(label_credit)

        return group
    


    def _retranslate(self) -> None:
        self.btn_close.setText(self.worker.settings.tr("generic:close"))

        self.disclaimer_label.setText(self.worker.settings.tr("about:disclaimer"))

        for key, label in self._credit_labels.items():
            label.setText(key)
    


    def _connect_signals(self) -> None:
        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.btn_github_croc.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/schollz/croc"))
        )
        self.btn_github_swampswap.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://github.com/Ferase/SwampSwap"))
        )
        
        self.btn_close.clicked.connect(self.reject)

    def _get_language_credits_list(self) -> list[str]:
        languages: SwampSwapLanguageList = self.worker.settings.locale_manager.langs

        lang_credits: list[str] = []
        for lang in languages:
            lang_credits.append(f"{lang.author} ({lang.language})")

        return lang_credits