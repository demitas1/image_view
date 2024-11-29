from pathlib import Path
import json
import sys

from natural_sort import natural_path_sort_key

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QFileDialog,
    QMenu, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QKeyEvent, QTransform, QAction

from open_dir_dialog import DialogResult, CustomDirectoryDialog


class ImageViewer(QMainWindow):
    def __init__(self, image_files):
        super().__init__()

        # 設定ファイルのパスを設定
        self.config_dir = self.get_config_dir()
        self.config_file = self.config_dir / 'config.json'

        # 設定を読み込む
        self.load_settings()

        # コマンドライン引数で画像ファイルが指定された場合はそれを使用
        if image_files:
            self.image_files = self.filter_image_files(image_files)
        # 指定がない場合は保存されていた最近のファイルリストを使用
        else:
            self.image_files = self.filter_image_files(self.recent_files)

        self.current_index = 0

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
        valid_files = []
        for f in files:
            if not isinstance(f, Path):
                f = Path(f)
            if f.exists() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                valid_files.append(f)
        return self.sort_image_files(valid_files)


    def sort_image_files(self, files):
        sorted_files = sorted(files, key=natural_path_sort_key)
        return sorted_files


    def create_blank_image(self):
        """黒い画像を生成"""
        width = self.image_label.width()
        height = self.image_label.height()
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.black)
        return QPixmap.fromImage(image)


    def setup_context_menu(self):
        """コンテキストメニューの設定"""
        self.image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_label.customContextMenuRequested.connect(self.show_context_menu)


    def show_context_menu(self, position):
        """コンテキストメニューを表示"""
        # TODO: H-flip の追加
        # TODO: フォントサイズ調整

        context_menu = QMenu(self)

        # Open Files アクション
        open_action = QAction("Open Files", self)
        open_action.triggered.connect(self.open_file_dialog)
        context_menu.addAction(open_action)

        # Open Directory アクション
        open_action = QAction("Open Directory", self)
        open_action.triggered.connect(self.open_directory_dialog)
        context_menu.addAction(open_action)

        # セパレータを追加
        context_menu.addSeparator()

        # Quit アクション
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        context_menu.addAction(quit_action)

        # メニューを表示
        context_menu.exec(self.image_label.mapToGlobal(position))


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
            new_files = [Path(f) for f in selected_files_sorted]
            self.image_files = self.filter_image_files(new_files)
            self.current_index = 0
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
                new_files = [Path(f) for f in selected_files_sorted]
                self.image_files = self.filter_image_files(new_files)
                self.current_index = 0
                self.show_current_image()


    def show_current_image(self):
        """現在の画像を表示"""
        if not self.image_files:
            # 画像ファイルが無い場合は黒画像を表示
            pixmap = self.create_blank_image()
        else:
            # 画像を読み込み
            image_path = str(self.image_files[self.current_index])
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
        transform = QTransform()
        transform.scale(-1, 1)  # x軸方向に-1をかけることで左右反転
        flipped_pixmap = scaled_pixmap.transformed(transform)

        self.image_label.setPixmap(flipped_pixmap)

        # ウィンドウタイトルを更新
        if self.image_files:
            self.setWindowTitle(f'Image Viewer - {self.image_files[self.current_index].name}')
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
            'recent_files': []  # 最近開いたファイルのリスト
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


    def save_settings(self):
        """設定をJSONファイルに保存"""
        # TODO: カレントファイルも保存
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


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_next_image()
        if event.button() == Qt.MouseButton.MiddleButton:
            self.show_prev_image()


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
    # TODO: argparse
    #   --fresh: パス設定を読み込まない
    if len(sys.argv) < 2:
        app = QApplication(sys.argv)
        viewer = ImageViewer([])
        viewer.show()
        sys.exit(app.exec())

    # 画像ファイルのリストを作成
    # TODO: natural sort
    # TODO: random 機能
    image_files = []
    for path in sys.argv[1:]:
        p = Path(path)
        if p.is_file():
            image_files.append(p)
        elif p.is_dir():
            image_files.extend(p.glob('**/*'))

    app = QApplication(sys.argv)
    viewer = ImageViewer(image_files)
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
