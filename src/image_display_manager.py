from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage, QTransform, QColorSpace


class ImageDisplayManager:
    def __init__(self, image_label: QLabel):
        self.image_label = image_label
        self.h_flip = False
        self._current_image_path: Optional[Path] = None

    def set_h_flip(self, enabled: bool):
        self.h_flip = enabled

    def toggle_h_flip(self):
        self.h_flip = not self.h_flip

    def is_h_flip_enabled(self) -> bool:
        return self.h_flip

    def set_current_image_path(self, image_path: Optional[Path]):
        self._current_image_path = image_path

    def get_current_image_path(self) -> Optional[Path]:
        return self._current_image_path

    def get_current_image_filename(self) -> Optional[str]:
        if self._current_image_path:
            return self._current_image_path.name
        return None

    def create_blank_image(self) -> QPixmap:
        width = self.image_label.width()
        height = self.image_label.height()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.black)
        return QPixmap.fromImage(image)

    def load_and_display_image(self, image_path: Optional[Path] = None):
        if image_path is not None:
            self._current_image_path = image_path

        if self._current_image_path is None:
            pixmap = self.create_blank_image()
        else:
            pixmap = QPixmap(str(self._current_image_path))
            if pixmap.isNull():
                pixmap = self.create_blank_image()

        scaled_pixmap = self._scale_image_to_fit(pixmap)
        final_pixmap = self._apply_transformations(scaled_pixmap)
        
        self.image_label.setPixmap(final_pixmap)

    def refresh_display(self):
        self.load_and_display_image()

    def _scale_image_to_fit(self, pixmap: QPixmap) -> QPixmap:
        return pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def _apply_transformations(self, pixmap: QPixmap) -> QPixmap:
        if self.h_flip:
            transform = QTransform()
            transform.scale(-1, 1)
            return pixmap.transformed(transform)
        return pixmap

    def get_current_image_for_clipboard(self) -> Optional[QImage]:
        if self._current_image_path is None:
            return None
        
        image = QImage(str(self._current_image_path))
        if image.isNull():
            return None
            
        image.setColorSpace(QColorSpace())
        return image