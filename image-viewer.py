from pathlib import Path
import json
import sys
import random
import argparse

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog,
    QMenu, QSizePolicy,
)
from PyQt6.QtGui import (
    QPixmap, QImage, QKeyEvent, QTransform,
    QAction, QKeySequence, QIcon,
)

from open_dir_dialog import DialogResult, CustomDirectoryDialog
from natural_sort import natural_path_sort_key


class ImageViewer(QMainWindow):
    def __init__(self, image_files):
        super().__init__()

        # 複数サイズのアイコンを含むQIconを作成
        icon = QIcon()
        icon.addFile('icon/icon_16.png', QSize(16, 16))
        icon.addFile('icon/icon_32.png', QSize(32, 32))
        icon.addFile('icon/icon_48.png', QSize(48, 48))
        icon.addFile('icon/icon_64.png', QSize(64, 64))
        icon.addFile('icon/icon_128.png', QSize(128, 128))
        icon.addFile('icon/icon_256.png', QSize(256, 256))

        # アプリケーションにアイコンを設定
        self.setWindowIcon(icon)

        # 設定ファイルのパスを設定
        self.config_dir = self.get_config_dir()
        self.config_file = self.config_dir / 'config.json'

        # 設定を読み込む
        self.load_settings()

        # 水平反転設定
        self.h_flip = False

        # ランダム設定
        self.shuffle = False

        # コマンドライン引数で画像ファイルが指定された場合はそれを使用
        if image_files:
            self.image_files = self.filter_image_files(image_files)
            self.current_index = 0
        # 指定がない場合は保存されていた最近のファイルリストを使用
        else:
            self.image_files = self.filter_image_files(self.recent_files)
            self.current_index = self.recent_index

        # シャッフルテーブルの作製
        self.generate_shuffle_table()

        # メインウィンドウの設定
        self.setWindowTitle('Image Viewer')
        # リサイズを許可
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # ウィンドウの最小サイズを設定
        self.setMinimumSize(100, 100)

        # 画像表示用のラベルを作成
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # ラベルの最小サイズを0に設定
        self.image_label.setMinimumSize(0, 0)
        self.setCentralWidget(self.image_label)

        # コンテキストメニューの設定
        self.setup_context_menu()

        # 最初の画像を表示
        self.show_current_image()


    def filter_image_files(self, files):
        """有効な画像ファイルをフィルタリング"""
        # TODO: better function name
        valid_files = []
        for f in files:
            if not isinstance(f, Path):
                f = Path(f)
            if f.exists() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                valid_files.append(f)
        # ソート
        sorted_files = sorted(valid_files, key=natural_path_sort_key)
        return sorted_files


    def generate_shuffle_table(self):
        if not self.image_files:
            self.shuffle_table = []
            return

        n_images = len(self.image_files)
        if n_images > 0:
            sequence = list(range(n_images + 1))
            random.shuffle(sequence)
            self.shuffle_table = sequence
        else:
            self.shuffle_table = []


    def toggle_h_flip(self):
        # 水平反転フラグの反転
        self.h_flip = not self.h_flip
        # 画像更新
        self.show_current_image()


    def toggle_shuffle(self):
        if self.shuffle:
            # シャッフルをOFFにする場合、シャッフル後のインデックスを使用する
            index = self.shuffle_table[self.current_index]
            self.current_index = index

        # シャッフルフラグの反転
        self.shuffle = not self.shuffle


    def copy_image_path(self):
        """現在の画像のパスをクリップボードにコピー"""
        if self.image_files:
            # クリップボードに画像のパスをコピー
            clipboard = QApplication.clipboard()
            clipboard.setText(str(self.image_files[self.current_index].absolute()))


    def create_blank_image(self):
        """黒い画像を生成"""
        width = self.image_label.width()
        height = self.image_label.height()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.black)
        return QPixmap.fromImage(image)


    def setup_context_menu(self):
        # Copy アクションをショートカットキーと共に作成
        # OS 標準の Ctrl+C を使用する
        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.copy_image_path)
        self.addAction(self.copy_action)


    def show_context_menu(self, position=None):
        """コンテキストメニューを表示"""
        context_menu = QMenu(self)
        # フォントサイズ調整
        context_menu.setStyleSheet(f'QMenu {{ font-size: 12pt; }}')

        # Open Files アクション
        open_action = QAction("Open Files", self)
        open_action.triggered.connect(self.open_file_dialog)
        context_menu.addAction(open_action)

        # Open Directory アクション
        open_action = QAction("Open Directory", self)
        open_action.triggered.connect(self.open_directory_dialog)
        context_menu.addAction(open_action)

        # Copy アクション
        context_menu.addAction(self.copy_action)

        # 水平反転
        if self.h_flip:
            text_toggle = "H-Flip OFF"
        else:
            text_toggle = "H-Flip ON"
        open_action = QAction(text_toggle, self)
        open_action.triggered.connect(self.toggle_h_flip)
        context_menu.addAction(open_action)

        # シャッフルON/OFF
        if self.shuffle:
            text_toggle = "Shuffle OFF"
        else:
            text_toggle = "Shuffle ON"
        open_action = QAction(text_toggle, self)
        open_action.triggered.connect(self.toggle_shuffle)
        context_menu.addAction(open_action)

        # セパレータを追加
        context_menu.addSeparator()

        # Quit アクション
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        context_menu.addAction(quit_action)

        # メニューを表示
        if position:
            context_menu.exec(self.image_label.mapToGlobal(position))
        else:
            context_menu.exec(self.mapToGlobal(self.rect().center()))


    def open_file_dialog(self):
        """ファイル選択ダイアログを表示"""
        selected_files, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Files",
            "",
            "All Files (*)"
        )
        if selected_files:
            # 新しい画像ファイルをリストに追加
            selected_files_sorted = self.filter_image_files(selected_files)
            self.image_files = [Path(f) for f in selected_files_sorted]
            self.current_index = 0

            # シャッフルテーブルの作製
            self.generate_shuffle_table()

            # 新しい画像の表示
            self.show_current_image()


    def open_directory_dialog(self):
        # ディレクトリ選択
        dialog = CustomDirectoryDialog()
        result = dialog.get_result()

        if result:
            p = Path(result.directory)
            if p.is_dir():
                # 新しい画像ファイルをリストに追加
                if result.include_subdirs:
                    selected_files = p.glob('**/*')
                else:
                    selected_files = p.glob('*')

                selected_files_sorted = self.filter_image_files(selected_files)
                self.image_files = [Path(f) for f in selected_files_sorted]
                self.current_index = 0

                # シャッフルテーブルの作製
                self.generate_shuffle_table()

                # 新しい画像の表示
                self.show_current_image()


    def show_current_image(self):
        """現在の画像を表示"""
        if not self.image_files:
            # 画像ファイルが無い場合は黒画像を表示
            pixmap = self.create_blank_image()
        else:
            # シャッフル
            if self.shuffle:
                index = self.shuffle_table[self.current_index]
            else:
                index = self.current_index

            # 画像を読み込み
            image_path = str(self.image_files[index])
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                # 画像の読み込みに失敗した場合は黒画像を表示
                pixmap = self.create_blank_image()

        # ウィンドウサイズに合わせて画像をスケール
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # QTransformを使用して左右反転
        if self.h_flip:
            transform = QTransform()
            transform.scale(-1, 1)  # x軸方向に-1をかけることで左右反転
            flipped_pixmap = scaled_pixmap.transformed(transform)
        else:
            flipped_pixmap = scaled_pixmap

        # 画像更新
        self.image_label.setPixmap(flipped_pixmap)

        # ウィンドウタイトルを更新
        if self.image_files:
            self.setWindowTitle(f'Image Viewer - {self.image_files[index].name}')
        else:
            self.setWindowTitle('Image Viewer - No Image')


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
            },
            'recent_files': [],  # 最近開いたファイルのリスト
            'recent_index': 0,
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

                # 最近開いたファイルのリストを取得
                self.recent_files = [Path(f) for f in settings.get('recent_files', [])]
                self.recent_index = int(settings.get('recent_index', '0'))
            else:
                # デフォルト設定を適用
                window_settings = default_settings['window']
                self.setGeometry(
                    window_settings['x'],
                    window_settings['y'],
                    window_settings['width'],
                    window_settings['height']
                )
                self.recent_files = []
                self.recent_index = 0
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
            self.recent_files = []
            self.recent_index = 0


    def save_settings(self):
        """設定をJSONファイルに保存"""
        try:
            # 既存の設定を読み込む
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = {}

            # ウィンドウ設定を更新
            settings['window'] = {
                'x': self.x(),
                'y': self.y(),
                'width': self.width(),
                'height': self.height()
            }

            # 画像ファイルリストが空でない場合のみ、recent_filesを更新
            if self.image_files:
                settings['recent_files'] = [str(f) for f in self.image_files]
                if self.shuffle:
                    # シャッフルをOFFにする場合、シャッフル後のインデックスを使用する
                    index = self.shuffle_table[self.current_index]
                else:
                    index = self.current_index
                settings['recent_index'] = str(index)

            # 設定を保存
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
            self.show_next_image()
        elif event.key() == Qt.Key.Key_Left:
            self.show_prev_image()
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:  # '='キーも'+'として扱う
            self.resize_window(increase=True)
        elif event.key() == Qt.Key.Key_Minus:
            self.resize_window(increase=False)
        elif event.key() == Qt.Key.Key_R:
            self.toggle_shuffle()
        elif event.key() == Qt.Key.Key_H:
            self.toggle_h_flip()
        elif event.key() == Qt.Key.Key_Space:
            self.show_context_menu()


    def mousePressEvent(self, event):
        pos = event.pos()

        if event.button() == Qt.MouseButton.LeftButton:
            self.show_next_image()
        if event.button() == Qt.MouseButton.RightButton:
            self.show_prev_image()
        if event.button() == Qt.MouseButton.MiddleButton:
            self.show_context_menu(position=pos)


    def show_prev_image(self):
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.show_current_image()


    def show_next_image(self):
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.show_current_image()


    def resize_window(self, increase: bool):
        """ウィンドウサイズを変更する"""
        current_width = self.width()
        current_height = self.height()
        current_x = self.x()
        current_y = self.y()

        if increase:
            # 拡大（10%増加）
            if current_height >= 3000:  # 最大サイズに達している場合
                return

            new_height = min(int(current_height * 1.1), 3000)
            # アスペクト比を維持
            new_width = int(new_height * (current_width / current_height))

        else:
            # 縮小（10%減少）
            if current_height <= 500:  # 最小サイズに達している場合
                return

            new_height = max(int(current_height * 0.9), 500)
            # アスペクト比を維持
            new_width = int(new_height * (current_width / current_height))

        # サイズの変更量
        width_delta = new_width - current_width
        height_delta = new_height - current_height

        # 新しい位置（中心を基準に調整）
        new_x = current_x - width_delta // 2
        new_y = current_y - height_delta // 2

        # ウィンドウの位置とサイズを更新
        self.setGeometry(new_x, new_y, new_width, new_height)

        # 画像を新しいサイズで表示し直す
        self.show_current_image()


def main():
    # argparse
    parser = argparse.ArgumentParser(
        description='Simple Image Viewer'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='image files or directories.'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='search subdirectories too.'
    )
    args = parser.parse_args()

    image_files = []

    # 画像ファイルのリストを作成
    for path in args.files:
        p = Path(path)
        if p.is_file():
            image_files.append(p)
        elif p.is_dir():
            if args.recursive:
                image_files.extend(p.glob('**/*'))
            else:
                image_files.extend(p.glob('*'))

    # High DPIサポートを有効化
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)

    viewer = ImageViewer(image_files)
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
