from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QMimeData
from PyQt6.QtGui import QImage, QPixmap, QColorSpace


class ClipboardManager:
    @staticmethod
    def copy_image_path(image_path: Optional[Path]):
        if image_path is None:
            return
            
        clipboard = QApplication.clipboard()
        clipboard.setText(str(image_path.absolute()))

    @staticmethod
    def copy_image_to_clipboard(image_path: Optional[Path]):
        if image_path is None:
            return

        try:
            image = QImage(str(image_path))
            if image.isNull():
                return
                
            image.setColorSpace(QColorSpace())
            pixmap = QPixmap.fromImage(image)

            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setImageData(pixmap.toImage())
            clipboard.setMimeData(mime_data)
        except Exception as e:
            print(f"クリップボードコピーエラー: {e}")

    @staticmethod
    def copy_image_data_to_clipboard(image: Optional[QImage]):
        if image is None or image.isNull():
            return

        try:
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setImageData(image)
            clipboard.setMimeData(mime_data)
        except Exception as e:
            print(f"クリップボードコピーエラー: {e}")