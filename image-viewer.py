#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QKeyEvent
from pathlib import Path


class ImageViewer(QMainWindow):
    def __init__(self, image_files):
        super().__init__()

        # 画像ファイルのリストをフィルタリング
        self.image_files = [
            f for f in image_files 
            if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        ]

        if not self.image_files:
            print("表示可能な画像ファイルが見つかりませんでした。")
            sys.exit(1)

        self.current_index = 0

        # メインウィンドウの設定
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)

        # 画像表示用のラベルを作成
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.image_label)

        # 最初の画像を表示
        self.show_current_image()


    def show_current_image(self):
        # 画像を読み込み
        image_path = str(self.image_files[self.current_index])
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"画像の読み込みに失敗しました: {image_path}")
            return

        # ウィンドウサイズに合わせて画像をスケール
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.setWindowTitle(f'Image Viewer - {self.image_files[self.current_index].name}')


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_label.pixmap():
            self.show_current_image()


    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Q:
            self.close()
        elif event.key() == Qt.Key.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.show_current_image()
        elif event.key() == Qt.Key.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.show_current_image()


def main():
    if len(sys.argv) < 2:
        print("使用方法: python image_viewer.py [画像ファイル/ディレクトリ ...]")
        sys.exit(1)

    # 画像ファイルのリストを作成
    image_files = []
    for path in sys.argv[1:]:
        p = Path(path)
        if p.is_file():
            image_files.append(p)
        elif p.is_dir():
            image_files.extend(p.glob('*'))

    app = QApplication(sys.argv)
    viewer = ImageViewer(image_files)
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
