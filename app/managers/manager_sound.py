from pathlib import Path

from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QObject, QUrl

import app.utils as app_utils
from app.enums import CrocState, CrocAction, CrocWAV
from app.managers.manager_settings import SettingsManager

_WAV_DIR: Path = app_utils.determine_filepath(Path("assets/wav"))


class SoundManager(QObject):
    """Manages loading and playing short sound effects used throughout the program."""

    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)

        self.settings = settings

        self._sound_effects: dict[CrocWAV, QSoundEffect] = {}
        self._enable_sound: QSoundEffect | None = None
        self._last_action: CrocAction = CrocAction.NONE

        self._load_effects()

    def _load_effects(self) -> None:
        for wav in CrocWAV:
            sound = QSoundEffect(self)
            sound.setSource(self._wav_url(wav))
            sound.setVolume(self.settings.sound_volume)
            self._sound_effects[wav] = sound

        self._enable_sound = QSoundEffect(self)
        self._enable_sound.setSource(self._wav_url("enabled"))
        self._enable_sound.setVolume(self.settings.sound_volume)

    def _wav_url(self, wav: CrocWAV) -> QUrl:
        return QUrl.fromLocalFile(str(_WAV_DIR / f"{wav}.wav"))

    def on_state_change(self, state: CrocState) -> None:
        if not self.settings.enable_sound:
            return

        wav = None

        match state.action:
            case CrocAction.WAIT_FOR_PEER:
                wav = CrocWAV.START
            case CrocAction.CONNECTING_TO_PEER:
                wav = CrocWAV.START
            case CrocAction.ERROR:
                wav = CrocWAV.ERROR
            case CrocAction.CANCELLED:
                wav = CrocWAV.CANCEL
            case CrocAction.WAIT_FOR_APPROVAL:
                wav = CrocWAV.AWAITING_APPROVAL
            case CrocAction.COMPLETED:
                wav = CrocWAV.COMPLETE
            case _:
                return

        effect = self._sound_effects.get(wav)
        if effect is None:
            return
        
        if self._last_action == state.action:
            return
        
        self._last_action = state.action

        effect.play()

    def play_enable_sound(self) -> None:
        if self._enable_sound.isPlaying():
            self._enable_sound.stop()

        self._enable_sound.play()

    def set_volume(self, volume: float) -> None:
        for effect in self._sound_effects.values():
            effect.setVolume(volume)

        self._enable_sound.setVolume(volume)

    def silence_all(self) -> None:
        self.set_volume(0.0)