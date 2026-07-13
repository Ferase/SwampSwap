from copy import deepcopy
from typing import Any

from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QStatusBar, QMessageBox,
    QMenuBar, QMenu, QApplication, QPushButton,
    QGroupBox, QVBoxLayout, QHBoxLayout, QStyle,
    QGridLayout, QScrollArea, QLabel, QWidget,
    QComboBox, QLineEdit, QCheckBox
)
from PyQt6.QtGui import QAction, QDesktopServices, QIcon, QRegularExpressionValidator
from PyQt6.QtCore import QUrl, QRegularExpression, pyqtSignal

import app.utils as app_utils
from app.enums import CrocState, CrocOperation, CrocAction
from app.workers.worker_croc import CrocWorker
from app.widgets.widget_send import SendWidget
from app.widgets.widget_receive import ReceiveWidget

_PADDING: int = 10



# Main window
class SettingsWidget(QWidget):

    settings_changed = pyqtSignal(bool)

    # Init
    def __init__(self, worker: CrocWorker, parent=None) -> None:
        # Run base init
        super().__init__(parent)

        self.worker: CrocWorker = worker
        self.dirty = False

        # Build UI
        self._build_central()

        self._connect_signals()

    # Construct main UI
    def _build_central(self) -> None:
        layout = QVBoxLayout(self)

        self.scrollarea_main = self._build_main_scrollarea()
        self.button_row = self._build_buttons()

        layout.addWidget(self.scrollarea_main)
        layout.addWidget(self.button_row)

    def _build_main_scrollarea(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Example content
        group_general_settings = self._build_general_settings_group()
        group_relay_settings = self._build_relay_settings_group()
        group_network_settings = self._build_network_settings_group()
        group_flags_settings = self._build_flags_settings_group()

        layout.addWidget(group_general_settings)
        layout.addSpacing(_PADDING)
        layout.addWidget(group_relay_settings)
        layout.addSpacing(_PADDING)
        layout.addWidget(group_network_settings)
        layout.addSpacing(_PADDING)
        layout.addWidget(group_flags_settings)

        layout.addStretch()

        scroll.setWidget(widget)

        return scroll
    
    def _build_general_settings_group(self) -> QGroupBox:
        self.general_group = QGroupBox(self.worker.settings.tr("options:heading:general"))
        layout = QVBoxLayout(self.general_group)
        
        self.label_lang = QLabel(self.worker.settings.tr("options:language:label"))
        self.label_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))

        self.combo_lang = app_utils.NoScrollComboBox()
        self.combo_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))
        self.combo_lang.addItems(self.worker.settings.lang_list)
        self.combo_lang.setCurrentText(self.worker.settings.lang)

        self.label_theme = QLabel(self.worker.settings.tr("options:theme:label"))
        self.label_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))

        self.combo_theme = app_utils.NoScrollComboBox()
        self.combo_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))
        self.combo_theme.addItems(self.worker.settings.theme_list)
        self.combo_theme.setCurrentText(self.worker.settings.theme)

        self.checkbox_startup_console = QCheckBox(self.worker.settings.tr("options:startup_console:label"))
        self.checkbox_startup_console.setToolTip(self.worker.settings.tr("options:startup_console:tooltip"))
        self.checkbox_startup_console.setChecked(self.worker.settings.startup_console)

        self.checkbox_startup_croc_updates_check = QCheckBox(self.worker.settings.tr("options:startup_croc_updates_check:label"))
        self.checkbox_startup_croc_updates_check.setToolTip(self.worker.settings.tr("options:startup_croc_updates_check:tooltip"))
        self.checkbox_startup_croc_updates_check.setChecked(self.worker.settings.startup_swampswap_updates_check)

        self.checkbox_startup_swampswap_updates_check = QCheckBox(self.worker.settings.tr("options:startup_swampswap_updates_check:label"))
        self.checkbox_startup_swampswap_updates_check.setToolTip(self.worker.settings.tr("options:startup_swampswap_updates_check:tooltip"))
        self.checkbox_startup_swampswap_updates_check.setChecked(self.worker.settings.startup_swampswap_updates_check)

        layout.addWidget(self.label_lang)
        layout.addWidget(self.combo_lang)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_theme)
        layout.addWidget(self.combo_theme)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.checkbox_startup_console)
        layout.addWidget(self.checkbox_startup_croc_updates_check)
        layout.addWidget(self.checkbox_startup_swampswap_updates_check)

        return self.general_group
    
    def _build_relay_settings_group(self) -> QGroupBox:
        self.relays_group = QGroupBox(self.worker.settings.tr("options:heading:relays"))
        layout = QVBoxLayout(self.relays_group)
        
        self.label_relay = QLabel(self.worker.settings.tr("options:relay:label"))
        self.label_relay.setToolTip(self.worker.settings.tr("options:relay:tooltip"))

        self.lineedit_relay = QLineEdit()
        self.lineedit_relay.setToolTip(self.worker.settings.tr("options:relay:tooltip"))
        self.lineedit_relay.setText(self.worker.settings.relay)

        self.label_relay6 = QLabel(self.worker.settings.tr("options:relay6:label"))
        self.label_relay6.setToolTip(self.worker.settings.tr("options:relay6:tooltip"))

        self.lineedit_relay6 = QLineEdit()
        self.lineedit_relay6.setToolTip(self.worker.settings.tr("options:relay6:tooltip"))
        self.lineedit_relay6.setText(self.worker.settings.relay6)

        self.label_pass = QLabel(self.worker.settings.tr("options:password:label"))
        self.label_pass.setToolTip(self.worker.settings.tr("options:password:tooltip"))

        self.lineedit_pass = QLineEdit()
        self.lineedit_pass.setToolTip(self.worker.settings.tr("options:password:tooltip"))
        self.lineedit_pass.setText(self.worker.settings.password)
        self.lineedit_pass.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(self.label_relay)
        layout.addWidget(self.lineedit_relay)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_relay6)
        layout.addWidget(self.lineedit_relay6)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.lineedit_pass)

        return self.relays_group
    
    def _build_network_settings_group(self) -> QGroupBox:
        self.network_group = QGroupBox(self.worker.settings.tr("options:heading:network"))
        layout = QVBoxLayout(self.network_group)
        
        self.label_curve = QLabel(self.worker.settings.tr("options:curve:label"))
        self.label_curve.setToolTip(self.worker.settings.tr("options:curve:tooltip"))

        self.combo_curve = app_utils.NoScrollComboBox()
        self.combo_curve.setToolTip(self.worker.settings.tr("options:curve:tooltip"))
        self.combo_curve.addItems(self.worker.settings.curve_list)
        self.combo_curve.setCurrentText(self.worker.settings.curve)

        self.label_ip = QLabel(self.worker.settings.tr("options:ip:label"))
        self.label_ip.setToolTip(self.worker.settings.tr("options:ip:tooltip"))

        self.lineedit_ip = QLineEdit()
        self.lineedit_ip.setToolTip(self.worker.settings.tr("options:ip:tooltip"))
        self.lineedit_ip.setPlaceholderText("e.g. 10.0.0.1:9009")
        self.lineedit_ip.setText(self.worker.settings.ip)

        self.label_multicast = QLabel(self.worker.settings.tr("options:multicast:label"))
        self.label_multicast.setToolTip(self.worker.settings.tr("options:multicast:tooltip"))

        self.lineedit_multicast = QLineEdit()
        self.lineedit_multicast.setToolTip(self.worker.settings.tr("options:multicast:tooltip"))
        self.lineedit_multicast.setText(self.worker.settings.multicast)

        self.label_socks5 = QLabel(self.worker.settings.tr("options:socks5:label"))
        self.label_socks5.setToolTip(self.worker.settings.tr("options:socks5:tooltip"))

        self.lineedit_socks5 = QLineEdit()
        self.lineedit_socks5.setToolTip(self.worker.settings.tr("options:socks5:tooltip"))
        self.lineedit_socks5.setText(self.worker.settings.socks5)

        self.label_connect = QLabel(self.worker.settings.tr("options:connect:label"))
        self.label_connect.setToolTip(self.worker.settings.tr("options:connect:tooltip"))

        self.lineedit_connect = QLineEdit()
        self.lineedit_connect.setToolTip(self.worker.settings.tr("options:connect:tooltip"))
        self.lineedit_connect.setText(self.worker.settings.connect)

        self.label_throttleupload = QLabel(self.worker.settings.tr("options:throttleupload:label"))
        self.label_throttleupload.setToolTip(self.worker.settings.tr("options:throttleupload:tooltip"))

        self.lineedit_throttleupload = QLineEdit()
        self.lineedit_throttleupload.setToolTip(self.worker.settings.tr("options:throttleupload:tooltip"))
        self.lineedit_throttleupload.setPlaceholderText("e.g. 500k")
        self.lineedit_throttleupload.setText(self.worker.settings.throttleupload)

        layout.addWidget(self.label_curve)
        layout.addWidget(self.combo_curve)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_ip)
        layout.addWidget(self.lineedit_ip)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_multicast)
        layout.addWidget(self.lineedit_multicast)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_socks5)
        layout.addWidget(self.lineedit_socks5)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_connect)
        layout.addWidget(self.lineedit_connect)
        layout.addSpacing(_PADDING)
        layout.addWidget(self.label_throttleupload)
        layout.addWidget(self.lineedit_throttleupload)

        return self.network_group
    
    def _build_flags_settings_group(self) -> QGroupBox:
        self.flags_group = QGroupBox(self.worker.settings.tr("options:heading:flags"))
        layout = QVBoxLayout(self.flags_group)

        self.checkbox_yes = QCheckBox(self.worker.settings.tr("options:yes:label"))
        self.checkbox_yes.setToolTip(self.worker.settings.tr("options:yes:tooltip"))
        self.checkbox_yes.setChecked(self.worker.settings.yes)

        self.checkbox_classic = QCheckBox(self.worker.settings.tr("options:classic:label"))
        self.checkbox_classic.setToolTip(self.worker.settings.tr("options:classic:tooltip"))
        self.checkbox_classic.setChecked(self.worker.settings.classic)

        self.checkbox_internaldns = QCheckBox(self.worker.settings.tr("options:internaldns:label"))
        self.checkbox_internaldns.setToolTip(self.worker.settings.tr("options:internaldns:tooltip"))
        self.checkbox_internaldns.setChecked(self.worker.settings.internaldns)

        self.checkbox_nocompress = QCheckBox(self.worker.settings.tr("options:nocompress:label"))
        self.checkbox_nocompress.setToolTip(self.worker.settings.tr("options:nocompress:tooltip"))
        self.checkbox_nocompress.setChecked(self.worker.settings.nocompress)

        self.checkbox_local = QCheckBox(self.worker.settings.tr("options:local:label"))
        self.checkbox_local.setToolTip(self.worker.settings.tr("options:local:tooltip"))
        self.checkbox_local.setChecked(self.worker.settings.local)

        layout.addWidget(self.checkbox_yes)
        layout.addWidget(self.checkbox_classic)
        layout.addWidget(self.checkbox_internaldns)
        layout.addWidget(self.checkbox_nocompress)
        layout.addWidget(self.checkbox_local)

        return self.flags_group
    
    def _build_buttons(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.btn_save = QPushButton(self.worker.settings.tr("generic:save"))
        self.btn_reset = QPushButton(self.worker.settings.tr("generic:reset_defaults"))

        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_reset)

        return widget
    


    def _retranslate(self) -> None:
        """Retranslate everything on language change."""

        self.setWindowTitle(self.worker.settings.tr("options:window:title"))

        self.general_group.setTitle(self.worker.settings.tr("options:heading:general"))
        self.label_lang.setText(self.worker.settings.tr("options:language:label"))
        self.label_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))
        self.combo_lang.setToolTip(self.worker.settings.tr("options:language:tooltip"))
        self.label_theme.setText(self.worker.settings.tr("options:theme:label"))
        self.label_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))
        self.combo_theme.setToolTip(self.worker.settings.tr("options:theme:tooltip"))
        self.checkbox_startup_console.setText(self.worker.settings.tr("options:startup_console:label"))
        self.checkbox_startup_console.setToolTip(self.worker.settings.tr("options:startup_console:tooltip"))
        self.checkbox_startup_croc_updates_check.setText(self.worker.settings.tr("options:startup_croc_updates_check:label"))
        self.checkbox_startup_croc_updates_check.setToolTip(self.worker.settings.tr("options:startup_croc_updates_check:tooltip"))
        self.checkbox_startup_swampswap_updates_check.setText(self.worker.settings.tr("options:startup_swampswap_updates_check:label"))
        self.checkbox_startup_swampswap_updates_check.setToolTip(self.worker.settings.tr("options:startup_swampswap_updates_check:tooltip"))

        self.relays_group.setTitle(self.worker.settings.tr("options:heading:relays"))
        self.label_relay.setText(self.worker.settings.tr("options:relay:label"))
        self.label_relay.setToolTip(self.worker.settings.tr("options:relay:tooltip"))
        self.lineedit_relay.setToolTip(self.worker.settings.tr("options:relay:tooltip"))
        self.label_relay6.setText(self.worker.settings.tr("options:relay6:label"))
        self.label_relay6.setToolTip(self.worker.settings.tr("options:relay6:tooltip"))
        self.lineedit_relay6.setToolTip(self.worker.settings.tr("options:relay6:tooltip"))
        self.label_pass.setText(self.worker.settings.tr("options:password:label"))
        self.label_pass.setToolTip(self.worker.settings.tr("options:password:tooltip"))
        self.lineedit_pass.setToolTip(self.worker.settings.tr("options:password:tooltip"))

        self.network_group.setTitle(self.worker.settings.tr("options:heading:network"))
        self.label_curve.setText(self.worker.settings.tr("options:curve:label"))
        self.label_curve.setToolTip(self.worker.settings.tr("options:curve:tooltip"))
        self.combo_curve.setToolTip(self.worker.settings.tr("options:curve:tooltip"))
        self.label_ip.setText(self.worker.settings.tr("options:ip:label"))
        self.label_ip.setToolTip(self.worker.settings.tr("options:ip:tooltip"))
        self.lineedit_ip.setToolTip(self.worker.settings.tr("options:ip:tooltip"))
        self.label_multicast.setText(self.worker.settings.tr("options:multicast:label"))
        self.label_multicast.setToolTip(self.worker.settings.tr("options:multicast:tooltip"))
        self.lineedit_multicast.setToolTip(self.worker.settings.tr("options:multicast:tooltip"))
        self.label_socks5.setText(self.worker.settings.tr("options:socks5:label"))
        self.label_socks5.setToolTip(self.worker.settings.tr("options:socks5:tooltip"))
        self.lineedit_socks5.setToolTip(self.worker.settings.tr("options:socks5:tooltip"))
        self.label_connect.setText(self.worker.settings.tr("options:connect:label"))
        self.label_connect.setToolTip(self.worker.settings.tr("options:connect:tooltip"))
        self.lineedit_connect.setToolTip(self.worker.settings.tr("options:connect:tooltip"))
        self.label_throttleupload.setText(self.worker.settings.tr("options:throttleupload:label"))
        self.label_throttleupload.setToolTip(self.worker.settings.tr("options:throttleupload:tooltip"))
        self.lineedit_throttleupload.setToolTip(self.worker.settings.tr("options:throttleupload:tooltip"))

        self.flags_group.setTitle(self.worker.settings.tr("options:heading:flags"))
        self.checkbox_yes.setText(self.worker.settings.tr("options:yes:label"))
        self.checkbox_yes.setToolTip(self.worker.settings.tr("options:yes:tooltip"))
        self.checkbox_classic.setText(self.worker.settings.tr("options:classic:label"))
        self.checkbox_classic.setToolTip(self.worker.settings.tr("options:classic:tooltip"))
        self.checkbox_internaldns.setText(self.worker.settings.tr("options:internaldns:label"))
        self.checkbox_internaldns.setToolTip(self.worker.settings.tr("options:internaldns:tooltip"))
        self.checkbox_nocompress.setText(self.worker.settings.tr("options:nocompress:label"))
        self.checkbox_nocompress.setToolTip(self.worker.settings.tr("options:nocompress:tooltip"))
        self.checkbox_local.setText(self.worker.settings.tr("options:local:label"))
        self.checkbox_local.setToolTip(self.worker.settings.tr("options:local:tooltip"))

        self.btn_reset.setText(self.worker.settings.tr("generic:reset_defaults"))
        self.btn_save.setText(self.worker.settings.tr("generic:save"))



    def _connect_signals(self) -> None:
        """Connect all necessary Qt signals."""

        self.worker.settings.locale_manager.language_changed.connect(self._retranslate)

        self.combo_lang.currentTextChanged.connect(self._change_language)
        self.combo_theme.currentTextChanged.connect(self._change_theme)

        self.btn_reset.clicked.connect(self._click_reset_button)
        self.btn_save.clicked.connect(self._click_save_button)

        # Mark changed settings as dirty
        self.combo_lang.currentIndexChanged.connect(self._mark_dirty)
        self.combo_theme.currentIndexChanged.connect(self._mark_dirty)
        self.checkbox_startup_console.toggled.connect(self._mark_dirty)
        self.checkbox_startup_croc_updates_check.toggled.connect(self._mark_dirty)
        self.checkbox_startup_swampswap_updates_check.toggled.connect(self._mark_dirty)

        self.lineedit_relay.textChanged.connect(self._mark_dirty)
        self.lineedit_relay6.textChanged.connect(self._mark_dirty)
        self.lineedit_pass.textChanged.connect(self._mark_dirty)

        self.combo_curve.currentTextChanged.connect(self._mark_dirty)

        self.lineedit_ip.textChanged.connect(self._mark_dirty)
        self.lineedit_multicast.textChanged.connect(self._mark_dirty)
        self.lineedit_socks5.textChanged.connect(self._mark_dirty)
        self.lineedit_connect.textChanged.connect(self._mark_dirty)
        self.lineedit_throttleupload.textChanged.connect(self._mark_dirty)

        self.checkbox_yes.toggled.connect(self._mark_dirty)
        self.checkbox_classic.toggled.connect(self._mark_dirty)
        self.checkbox_internaldns.toggled.connect(self._mark_dirty)
        self.checkbox_nocompress.toggled.connect(self._mark_dirty)
        self.checkbox_local.toggled.connect(self._mark_dirty)

    def _change_language(self, text: str) -> None:
        self.worker.settings.lang = text
        self.worker.settings.change_language()
        self.worker.settings.save_single_setting("lang", text)

    def _change_theme(self, text: str) -> None:
        self.worker.settings.theme = text
        self.worker.settings.change_theme()

    def _load_from_settings(self) -> None:
        self.combo_lang.setCurrentText(self.worker.settings.lang)
        self.combo_theme.setCurrentText(self.worker.settings.theme)
        self.checkbox_startup_console.setChecked(self.worker.settings.startup_console)
        self.checkbox_startup_croc_updates_check.setChecked(self.worker.settings.startup_croc_updates_check)
        self.checkbox_startup_swampswap_updates_check.setChecked(self.worker.settings.startup_swampswap_updates_check)

        self.lineedit_relay.setText(self.worker.settings.relay)
        self.lineedit_relay6.setText(self.worker.settings.relay6)
        self.lineedit_pass.setText(self.worker.settings.password)

        self.combo_curve.setCurrentText(self.worker.settings.curve)
        self.lineedit_ip.setText(self.worker.settings.ip)
        self.lineedit_multicast.setText(self.worker.settings.multicast)
        self.lineedit_socks5.setText(self.worker.settings.socks5)
        self.lineedit_connect.setText(self.worker.settings.connect)
        self.lineedit_throttleupload.setText(self.worker.settings.throttleupload)

        self.checkbox_yes.setChecked(self.worker.settings.yes)
        self.checkbox_classic.setChecked(self.worker.settings.classic)
        self.checkbox_internaldns.setChecked(self.worker.settings.internaldns)
        self.checkbox_nocompress.setChecked(self.worker.settings.nocompress)
        self.checkbox_local.setChecked(self.worker.settings.local)

    def _save_to_settings(self) -> None:
        self.worker.settings.lang = self.combo_lang.currentText()
        self.worker.settings.theme = self.combo_theme.currentText()
        self.worker.settings.startup_console = self.checkbox_startup_console.isChecked()
        self.worker.settings.startup_croc_updates_check = self.checkbox_startup_croc_updates_check.isChecked()
        self.worker.settings.startup_swampswap_updates_check = self.checkbox_startup_swampswap_updates_check.isChecked()

        self.worker.settings.relay = self.lineedit_relay.text()
        self.worker.settings.relay6 = self.lineedit_relay6.text()
        self.worker.settings.password = self.lineedit_pass.text()

        self.worker.settings.curve = self.combo_curve.currentText()
        self.worker.settings.ip = self.lineedit_ip.text()
        self.worker.settings.multicast = self.lineedit_multicast.text()
        self.worker.settings.socks5 = self.lineedit_socks5.text()
        self.worker.settings.connect = self.lineedit_connect.text()
        self.worker.settings.throttleupload = self.lineedit_throttleupload.text()

        self.worker.settings.yes = self.checkbox_yes.isChecked()
        self.worker.settings.classic = self.checkbox_classic.isChecked()
        self.worker.settings.internaldns = self.checkbox_internaldns.isChecked()
        self.worker.settings.nocompress = self.checkbox_nocompress.isChecked()
        self.worker.settings.local = self.checkbox_local.isChecked()

    def _ui_settings_to_dict(self) -> dict[str, Any]:
        return {
            "lang": self.combo_lang.currentText(),
            "theme": self.combo_theme.currentText(),
            "startup_console": self.checkbox_startup_console.isChecked(),
            "startup_croc_updates_check": self.checkbox_startup_croc_updates_check.isChecked(),
            "startup_swampswap_updates_check": self.checkbox_startup_swampswap_updates_check.isChecked(),
            
            "relay": self.lineedit_relay.text(),
            "relay6": self.lineedit_relay6.text(),
            "password": self.lineedit_pass.text(),

            "curve": self.combo_curve.currentText(),
            "ip": self.lineedit_ip.text(),
            "multicast": self.lineedit_multicast.text(),
            "socks5": self.lineedit_socks5.text(),
            "connect": self.lineedit_connect.text(),
            "throttleupload": self.lineedit_throttleupload.text(),

            "yes": self.checkbox_yes.isChecked(),
            "classic": self.checkbox_classic.isChecked(),
            "internaldns": self.checkbox_internaldns.isChecked(),
            "nocompress": self.checkbox_nocompress.isChecked(),
            "local": self.checkbox_local.isChecked()
        }

    def _mark_dirty(self):
        saved_settings: dict[str, Any] = self.worker.settings.serialize_to_dict()
        ui_settings: dict[str, Any] = self._ui_settings_to_dict()

        for setting, value in saved_settings.items():
            if ui_settings[setting] == value:
                continue

            self.dirty = True
            self.settings_changed.emit(True)
            return
        
        self._clear_dirty()

    def _clear_dirty(self):
        self.dirty = False
        self.settings_changed.emit(False)



    def _click_reset_button(self) -> None:
        if self.worker.settings.are_settings_default():
            box = QMessageBox.information(
                self,
                self.worker.settings.tr("dialog:settings_are_default:title"),
                self.worker.settings.tr("dialog:settings_are_default:body"),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok
            )
            return

        box2 = QMessageBox.question(
            self,
            self.worker.settings.tr("dialog:default_settings:title"),
            self.worker.settings.tr("dialog:default_settings:body"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if box2 == QMessageBox.StandardButton.Yes:
            self.worker.settings.set_defaults()
            self._load_from_settings()
            self.worker.settings.save_settings()

    def _click_save_button(self) -> None:
        self._save_to_settings()
        self.worker.settings.save_settings()
        self._clear_dirty()

        box = QMessageBox.information(
            self,
            self.worker.settings.tr("dialog:saved_settings:title"),
            self.worker.settings.tr("dialog:saved_settings:body"),
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )