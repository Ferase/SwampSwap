import numpy as np
from pathlib import Path

from PyQt6.QtGui import QMovie, QImage, QPixmap, QColor
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QSize, Qt

import app.utils as app_utils
from app.enums import CrocOperation, CrocAction

NEUTRAL_BLACK  = (0, 0, 0)
NEUTRAL_WHITE  = (255, 255, 255)
NEUTRAL_WATER  = (123, 203, 239)
NEUTRAL_BOX    = (246, 241, 216)
NEUTRAL_CROC   = (141, 192, 86)
NEUTRAL_BIRD   = (244, 206, 132)
NEUTRAL_FOLDER = (192, 142, 86)

NEUTRAL_SLOTS: dict[str, tuple[int, int, int]] = {
    "anim_black": NEUTRAL_BLACK,
    "anim_white": NEUTRAL_WHITE,
    "anim_water": NEUTRAL_WATER,
    "anim_box": NEUTRAL_BOX,
    "anim_croc": NEUTRAL_CROC,
    "anim_bird": NEUTRAL_BIRD,
    "anim_folder": NEUTRAL_FOLDER,
}

DISPLAY_SIZE = QSize(200, 110)



class AnimationManager(QObject):
    """A manager for the GIF animations played at the bottom of the window."""

    status_changed = pyqtSignal(CrocOperation, CrocAction)
    animation_changed = pyqtSignal()
    frame_ready = pyqtSignal(QPixmap)

    def __init__(self) -> None:
        super().__init__()
        self._tracked_operation: CrocOperation = CrocOperation.IDLE
        self._idle_timeout = QTimer()
        self._idle_timeout_time: int = 5000

        self.animations: dict[CrocAction, QMovie] = {}

        self._theme_colors: dict[str, QColor] = {}
        self._movie_slot_index_cache: dict[int, dict[str, int]] = {}

        self._load_animations()

        self.current_anim: QMovie = self.animations[CrocAction.NONE]
        self._connect_signals()

        self.current_anim: QMovie = self.animations[CrocAction.NONE]
        self._connect_signals()
        self.current_anim.start()
        self._emit_recolored_frame(self.current_anim)

    def _get_anim_path(self, anim_name: str) -> Path:
        return app_utils.get_assets_path() / "gif" / f"{anim_name}.gif"

    def _load_anim(self, anim_name: str) -> QMovie:
        """Load an animation and connect its frame changed signal."""

        movie = QMovie(str(self._get_anim_path(anim_name)))
        movie.frameChanged.connect(self._on_frame_changed)
        return movie

    def _load_animations(self) -> None:
        """Load GIF animations as QMovie objects into the manager."""

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
        """Connect all necessary Qt signals."""

        self.status_changed.connect(self._change_animation)
        self._idle_timeout.timeout.connect(self._return_idle_animation)



    def _change_animation(self, operation: CrocOperation, action: CrocAction) -> None:
        """Change the currently playing animation."""

        using_operation: CrocOperation = operation
        if self._tracked_operation != CrocOperation.IDLE and operation == CrocOperation.IDLE:
            using_operation = self._tracked_operation

        previous_anim = self.current_anim

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

        if previous_anim is not self.current_anim:
            previous_anim.stop()
            self.current_anim.start()
            self._emit_recolored_frame(self.current_anim)

        self.animation_changed.emit()

    def _return_idle_animation(self) -> None:
        """Return the current animation to the idle animation."""

        self._change_animation(CrocOperation.IDLE, CrocAction.NONE)

    def apply_theme_colors(self, theme_colors: dict[str, QColor]) -> None:
        """Apply the current theme's colors to the frame."""

        self._theme_colors = theme_colors
        self._emit_recolored_frame(self.current_anim)

    def _on_frame_changed(self, frame_number: int) -> None:
        """Whenever the QMoive object changes frame, push out the recolored frame."""

        movie = self.sender()
        if movie is not self.current_anim:
            return

        self._emit_recolored_frame(movie)

    def _emit_recolored_frame(self, movie: QMovie) -> None:
            """Emit the recolored frame via a signal so it can be displayed."""

            image = movie.currentImage()
            if image.isNull():
                return

            recolored = self._recolor_frame(image)

            pixmap = QPixmap.fromImage(recolored)
            pixmap = pixmap.scaled(
                DISPLAY_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )

            self.frame_ready.emit(pixmap)



    def _recolor_frame(self, image: QImage) -> QImage:
        """Recolor a frame of the current animation using the theme colors as the palette."""

        if not self._theme_colors:
            return image

        image = image.convertToFormat(QImage.Format.Format_ARGB32).copy()

        width = image.width()
        height = image.height()
        bytes_per_line = image.bytesPerLine()

        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())

        # View as (rows, stride_pixels, 4), then trim off any row padding
        arr = np.frombuffer(ptr, dtype=np.uint8)
        arr = arr.reshape((height, bytes_per_line // 4, 4))[:, :width, :]

        # Little-endian, BGRA
        blue, green, red, alpha = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]

        for slot_key, (nr, ng, nb) in NEUTRAL_SLOTS.items():
            target_color = self._theme_colors.get(slot_key)
            if target_color is None:
                continue

            mask = (red == nr) & (green == ng) & (blue == nb) & (alpha == 255)
            if not mask.any():
                continue

            arr[mask, 0] = target_color.blue()
            arr[mask, 1] = target_color.green()
            arr[mask, 2] = target_color.red()
            arr[mask, 3] = target_color.alpha()

        return image

    def _get_slot_index_map(self, movie: QMovie, image: QImage) -> dict[str, int]:
        """Get a map of all of the colors in the animation image."""

        cache_key = id(movie)
        cached = self._movie_slot_index_cache.get(cache_key)
        if cached is not None:
            return cached

        color_table = image.colorTable()
        slot_index_map: dict[str, int] = {}

        for slot_key, neutral_rgb in NEUTRAL_SLOTS.items():
            target_rgb = QColor(*neutral_rgb).rgb()
            for index, entry in enumerate(color_table):
                if QColor(entry).rgb() == target_rgb:
                    slot_index_map[slot_key] = index
                    break

        self._movie_slot_index_cache[cache_key] = slot_index_map
        return slot_index_map
