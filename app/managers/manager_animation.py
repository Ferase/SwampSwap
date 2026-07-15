from pathlib import Path

from PyQt6.QtGui import QMovie
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QSize

import app.utils as app_utils
from app.enums import CrocOperation, CrocAction



class AnimationManager(QObject):
    """A manager for the GIF animations played at the bottom of the window."""

    status_changed = pyqtSignal(CrocOperation, CrocAction)
    animation_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._tracked_operation: CrocOperation = CrocOperation.IDLE
        self._idle_timeout = QTimer()
        self._idle_timeout_time: int = 5000

        self.animations: dict[CrocAction, QMovie] = {}

        self._load_animations()

        self.current_anim: QMovie = self.animations[CrocAction.NONE]
        self._connect_signals()

    def _get_anim_path(self, anim_name: str) -> Path:
        return app_utils.get_assets_path() / "gif" / f"{anim_name}.gif"

    def _load_anim(self, anim_name: str) -> QMovie:
        movie = QMovie(str(self._get_anim_path(anim_name)))
        movie.setScaledSize(QSize(200, 110))
        return movie

    def _load_animations(self) -> None:
        self.animations = {
            CrocAction.NONE: self._load_anim("idle"),

            CrocAction.WAIT_FOR_PEER: self._load_anim("wait_for_peer"),
            CrocAction.SEND_IN_PROGRESS: self._load_anim("send_receive_in_progress"),

            CrocAction.CONNECTING_TO_PEER: self._load_anim("connecting_to_peer"),
            CrocAction.WAIT_FOR_APPROVAL: self._load_anim("wait_for_approval"),
            CrocAction.RECEIVE_IN_PROGRESS: self._load_anim("send_receive_in_progress"),
            
            CrocAction.CANCELLED: self._load_anim("cancelled"),
            CrocAction.ERROR: self._load_anim("error"),

            CrocAction.COMPLETED: {
                CrocOperation.IDLE: self._load_anim("idle"),
                CrocOperation.SENDING: self._load_anim("completed_send"),
                CrocOperation.RECEIVING: self._load_anim("completed_receive")
            }
        }



    def _connect_signals(self) -> None:
        self.status_changed.connect(self._change_animation)
        self._idle_timeout.timeout.connect(self._return_idle_animation)

    def _change_animation(self, operation: CrocOperation, action: CrocAction) -> None:
        using_operation: CrocOperation = operation
        if self._tracked_operation != CrocOperation.IDLE and operation == CrocOperation.IDLE:
            using_operation = self._tracked_operation

        if action == CrocAction.COMPLETED:
            self.current_anim = self.animations[CrocAction.COMPLETED][using_operation]
        else:
            self.current_anim = self.animations[action]

        if operation != CrocOperation.IDLE:
            self._tracked_operation = operation

        if action in [CrocAction.COMPLETED, CrocAction.CANCELLED, CrocAction.ERROR]:
            self._idle_timeout.start(self._idle_timeout_time)
        else:
            self._idle_timeout.stop()

        self.animation_changed.emit()

    def _return_idle_animation(self) -> None:
        self.current_anim = self.animations[CrocAction.NONE]
        self._tracked_operation = CrocOperation.IDLE
        self.animation_changed.emit()
