from pathlib import Path
import sys
import argparse

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QSizePolicy,
)
from PyQt6.QtGui import QKeyEvent, QIcon

from image_display_manager import ImageDisplayManager
from image_list_manager import ImageListManager
from settings_manager import SettingsManager
from clipboard_manager import ClipboardManager
from file_dialog_manager import FileDialogManager
from ui_manager import UIManager


class ImageViewer(QMainWindow):
    def __init__(self, image_files, recursive=False):
        super().__init__()
        
        self._recursive = recursive
        self._setup_window_icon()
        self._initialize_managers()
        self._setup_window()
        self._load_initial_data(image_files)
        self._setup_ui()
        self._show_current_image()

    def _setup_window_icon(self):
        icon = QIcon()
        import os
        if getattr(sys, 'frozen', False):
            # PyInstallerでビルドされた場合
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, 'icon')
        else:
            # 開発環境の場合
            icon_path = '../icon'
        
        icon.addFile(f'{icon_path}/icon_16.png', QSize(16, 16))
        icon.addFile(f'{icon_path}/icon_32.png', QSize(32, 32))
        icon.addFile(f'{icon_path}/icon_48.png', QSize(48, 48))
        icon.addFile(f'{icon_path}/icon_64.png', QSize(64, 64))
        icon.addFile(f'{icon_path}/icon_128.png', QSize(128, 128))
        icon.addFile(f'{icon_path}/icon_256.png', QSize(256, 256))
        self.setWindowIcon(icon)

    def _initialize_managers(self):
        self.settings_manager = SettingsManager()
        self.image_list_manager = ImageListManager()
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(0, 0)
        
        self.image_display_manager = ImageDisplayManager(self.image_label)
        self.ui_manager = UIManager(self)

    def _setup_window(self):
        self.setWindowTitle('Image Viewer')
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(100, 100)
        
        window_geometry = self.settings_manager.get_window_geometry()
        self.setGeometry(
            window_geometry['x'],
            window_geometry['y'],
            window_geometry['width'],
            window_geometry['height']
        )

    def _load_initial_data(self, image_files):
        if image_files:
            self.image_list_manager.set_image_files(image_files, 0)
            # コマンドライン引数からディレクトリが指定された場合の履歴記録
            # メニューバー作成後に更新するためフラグを設定
            self._pending_directory_record = image_files
        else:
            recent_files = self.settings_manager.get_recent_files()
            recent_index = self.settings_manager.get_recent_index()
            self.image_list_manager.set_image_files(recent_files, recent_index)
            self._pending_directory_record = None

    def _setup_ui(self):
        self.setCentralWidget(self.image_label)
        
        recent_directories = self.settings_manager.get_directory_history()
        self.ui_manager.create_menu_bar(
            self._open_file_dialog,
            self._open_directory_dialog,
            self._open_recent_directory,
            recent_directories
        )
        
        self.ui_manager.setup_copy_shortcut(self._copy_image_to_clipboard)
        
        # 保留中のディレクトリ記録があれば処理
        if hasattr(self, '_pending_directory_record') and self._pending_directory_record:
            self._record_directory_from_files(self._pending_directory_record)
            self._pending_directory_record = None

    def _show_current_image(self):
        current_path = self.image_list_manager.get_current_image_path()
        self.image_display_manager.load_and_display_image(current_path)
        self._update_window_title()

    def _update_window_title(self):
        filename = self.image_display_manager.get_current_image_filename()
        if filename:
            self.setWindowTitle(f'Image Viewer - {filename}')
        else:
            self.setWindowTitle('Image Viewer - No Image')

    def _open_file_dialog(self):
        selected_files = FileDialogManager.select_files()
        if selected_files:
            self.image_list_manager.set_image_files(selected_files, 0)
            self._show_current_image()

    def _open_directory_dialog(self):
        result = FileDialogManager.select_directory()
        if result:
            directory = Path(result.directory)
            if directory.is_dir():
                files = FileDialogManager.get_directory_files(directory, result.include_subdirs)
                self.image_list_manager.set_image_files(files, 0)
                if self.image_list_manager.has_images():
                    self.settings_manager.add_directory_to_history(str(directory), result.include_subdirs)
                    self._update_recent_directories_menu()
                self._show_current_image()

    def _copy_image_to_clipboard(self):
        current_path = self.image_list_manager.get_current_image_path()
        ClipboardManager.copy_image_to_clipboard(current_path)

    def _copy_image_path(self):
        current_path = self.image_list_manager.get_current_image_path()
        ClipboardManager.copy_image_path(current_path)

    def _toggle_h_flip(self):
        self.image_display_manager.toggle_h_flip()
        self.image_display_manager.refresh_display()

    def _toggle_shuffle(self):
        self.image_list_manager.toggle_shuffle()

    def _show_context_menu(self, position=None):
        context_menu = self.ui_manager.create_context_menu(
            self._open_file_dialog,
            self._open_directory_dialog,
            self._copy_image_to_clipboard,
            self._copy_image_path,
            self._toggle_h_flip,
            self._toggle_shuffle,
            self.close,
            self.image_display_manager.is_h_flip_enabled(),
            self.image_list_manager.is_shuffle_enabled()
        )
        
        if position:
            context_menu.exec(self.image_label.mapToGlobal(position))
        else:
            context_menu.exec(self.mapToGlobal(self.rect().center()))

    def _show_next_image(self):
        self.image_list_manager.move_to_next()
        self._show_current_image()

    def _show_prev_image(self):
        self.image_list_manager.move_to_previous()
        self._show_current_image()

    def _resize_window(self, increase: bool):
        current_width = self.width()
        current_height = self.height()
        current_x = self.x()
        current_y = self.y()

        if increase:
            if current_height >= 3000:
                return
            new_height = min(int(current_height * 1.1), 3000)
            new_width = int(new_height * (current_width / current_height))
        else:
            if current_height <= 500:
                return
            new_height = max(int(current_height * 0.9), 500)
            new_width = int(new_height * (current_width / current_height))

        width_delta = new_width - current_width
        height_delta = new_height - current_height

        new_x = current_x - width_delta // 2
        new_y = current_y - height_delta // 2

        self.setGeometry(new_x, new_y, new_width, new_height)
        self.image_display_manager.refresh_display()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image_label.pixmap():
            self.image_display_manager.refresh_display()

    def closeEvent(self, event):
        if self.image_list_manager.has_images():
            files = self.image_list_manager.get_image_files()
            current_index = self.image_list_manager.get_current_index()
            self.settings_manager.save_recent_files(files, current_index)
        
        self.settings_manager.save_window_geometry(
            self.x(), self.y(), self.width(), self.height()
        )
        super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Q:
            self.close()
        elif event.key() == Qt.Key.Key_Right:
            self._show_next_image()
        elif event.key() == Qt.Key.Key_Left:
            self._show_prev_image()
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self._resize_window(increase=True)
        elif event.key() == Qt.Key.Key_Minus:
            self._resize_window(increase=False)
        elif event.key() == Qt.Key.Key_R:
            self._toggle_shuffle()
        elif event.key() == Qt.Key.Key_H:
            self._toggle_h_flip()
        elif event.key() == Qt.Key.Key_Space:
            self._show_context_menu()

    def mousePressEvent(self, event):
        pos = event.pos()

        if event.button() == Qt.MouseButton.LeftButton:
            self._show_next_image()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_prev_image()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self._show_context_menu(position=pos)

    def _open_recent_directory(self, entry):
        directory_path = entry.get('path', '')
        include_subdirs = entry.get('include_subdirs', False)
        
        directory = Path(directory_path)
        print(f'open recent dir: {directory_path}, include_subdirs: {include_subdirs}')
        if directory.is_dir():
            files = FileDialogManager.get_directory_files(directory, include_subdirs)
            self.image_list_manager.set_image_files(files, 0)
            if self.image_list_manager.has_images():
                self.settings_manager.add_directory_to_history(str(directory), include_subdirs)
                self._update_recent_directories_menu()
            self._show_current_image()

    def _update_recent_directories_menu(self):
        recent_directories = self.settings_manager.get_directory_history()
        self.ui_manager.update_recent_directories_menu(recent_directories, self._open_recent_directory)

    def _record_directory_from_files(self, image_files):
        if not image_files or not self.image_list_manager.has_images():
            return
        
        # 最初のファイルの親ディレクトリを取得
        first_file = image_files[0]
        directory = first_file.parent
        
        # すべてのファイルが同じディレクトリにあるかチェック
        same_directory = all(f.parent == directory for f in image_files)
        
        if same_directory:
            self.settings_manager.add_directory_to_history(str(directory), self._recursive)
            self._update_recent_directories_menu()


def main():
    parser = argparse.ArgumentParser(description='Simple Image Viewer')
    parser.add_argument('files', nargs='*', help='image files or directories.')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='search subdirectories too.')
    args = parser.parse_args()

    image_files = []
    for path in args.files:
        p = Path(path).resolve()
        if p.is_file():
            image_files.append(p)
        elif p.is_dir():
            if args.recursive:
                image_files.extend([f.resolve() for f in p.glob('**/*') if f.is_file()])
            else:
                image_files.extend([f.resolve() for f in p.glob('*') if f.is_file()])

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)

    viewer = ImageViewer(image_files, args.recursive)
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()