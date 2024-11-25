#!/usr/bin/env python3
from pathlib import Path
import json
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QKeyEvent, QTransform
from pathlib import Path


class ImageViewer(QMainWindow):
    def __init__(self, image_files):
        super().__init__()

        # 設定ファイルのパスを設定
        self.config_dir = self.get_config_dir()
        self.config_file = self.config_dir / 'config.json'

        # 設定を読み込む
        self.load_settings()

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

        # QTransformを使用して左右反転
        # TODO: 左右反転フラグを作成し、キーアサインでトグルする
        transform = QTransform()
        transform.scale(-1, 1)  # x軸方向に-1をかけることで左右反転
        flipped_pixmap = scaled_pixmap.transformed(transform)

        self.image_label.setPixmap(flipped_pixmap)
        self.setWindowTitle(f'Image Viewer - {self.image_files[self.current_index].name}')


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_label.pixmap():
            self.show_current_image()


    def get_config_dir(self):
        """プラットフォームに応じた設定ディレクトリのパスを返す"""
        if sys.platform == 'win32':
            config_base = Path.home() / 'AppData' / 'Local'
        elif sys.platform == 'darwin':
            config_base = Path.home() / 'Library' / 'Application Support'
        else:  # Linux/Unix
            config_base = Path.home() / '.config'

        config_dir = config_base / 'ImageViewer'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir


    def load_settings(self):
        """設定をJSONファイルから読み込む"""
        default_settings = {
            'window': {
                'x': 100,
                'y': 100,
                'width': 800,
                'height': 600
            }
        }

        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # window設定を適用
                window_settings = settings.get('window', default_settings['window'])
                self.setGeometry(
                    window_settings['x'],
                    window_settings['y'],
                    window_settings['width'],
                    window_settings['height']
                )
            else:
                # デフォルト設定を適用
                window_settings = default_settings['window']
                self.setGeometry(
                    window_settings['x'],
                    window_settings['y'],
                    window_settings['width'],
                    window_settings['height']
                )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            # エラーの場合はデフォルト設定を使用
            window_settings = default_settings['window']
            self.setGeometry(
                window_settings['x'],
                window_settings['y'],
                window_settings['width'],
                window_settings['height']
            )


    def save_settings(self):
        """設定をJSONファイルに保存"""
        settings = {
            'window': {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            }
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存エラー: {e}")


    def closeEvent(self, event):
        # ウィンドウを閉じる際に設定を保存
        self.save_settings()
        super().closeEvent(event)


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
    # TODO: natural-sort.py を参考に argparse を実装する

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
