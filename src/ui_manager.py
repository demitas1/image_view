from typing import Callable, List, Dict, Any

from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow
from PyQt6.QtGui import QAction, QKeySequence


class UIManager:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window

    def create_menu_bar(self, 
                       on_open_files: Callable,
                       on_open_directory: Callable,
                       on_recent_directory: Callable = None,
                       recent_directories: List[Dict[str, Any]] = None) -> QMenuBar:
        menubar = self.main_window.menuBar()

        file_menu = menubar.addMenu("File")

        open_files_action = QAction("Open Files", self.main_window)
        open_files_action.triggered.connect(on_open_files)
        file_menu.addAction(open_files_action)

        open_dir_action = QAction("Open Directory", self.main_window)
        open_dir_action.triggered.connect(on_open_directory)
        file_menu.addAction(open_dir_action)

        # Recent Directoriesサブメニューを追加
        if on_recent_directory:
            file_menu.addSeparator()
            recent_menu = file_menu.addMenu("Recent Directories")
            self._populate_recent_menu(recent_menu, recent_directories or [], on_recent_directory)

        return menubar

    def create_context_menu(self,
                          on_open_files: Callable,
                          on_open_directory: Callable,
                          on_copy_image: Callable,
                          on_copy_path: Callable,
                          on_toggle_h_flip: Callable,
                          on_toggle_shuffle: Callable,
                          on_quit: Callable,
                          h_flip_enabled: bool,
                          shuffle_enabled: bool) -> QMenu:
        context_menu = QMenu(self.main_window)
        context_menu.setStyleSheet('QMenu { font-size: 12pt; }')

        open_files_action = QAction("Open Files", self.main_window)
        open_files_action.triggered.connect(on_open_files)
        context_menu.addAction(open_files_action)

        open_dir_action = QAction("Open Directory", self.main_window)
        open_dir_action.triggered.connect(on_open_directory)
        context_menu.addAction(open_dir_action)

        copy_action = QAction("Copy", self.main_window)
        copy_action.triggered.connect(on_copy_image)
        context_menu.addAction(copy_action)

        copy_path_action = QAction("Copy Path", self.main_window)
        copy_path_action.triggered.connect(on_copy_path)
        context_menu.addAction(copy_path_action)

        h_flip_text = "H-Flip OFF" if h_flip_enabled else "H-Flip ON"
        h_flip_action = QAction(h_flip_text, self.main_window)
        h_flip_action.triggered.connect(on_toggle_h_flip)
        context_menu.addAction(h_flip_action)

        shuffle_text = "Shuffle OFF" if shuffle_enabled else "Shuffle ON"
        shuffle_action = QAction(shuffle_text, self.main_window)
        shuffle_action.triggered.connect(on_toggle_shuffle)
        context_menu.addAction(shuffle_action)

        context_menu.addSeparator()

        quit_action = QAction("Quit", self.main_window)
        quit_action.triggered.connect(on_quit)
        context_menu.addAction(quit_action)

        return context_menu

    def setup_copy_shortcut(self, on_copy: Callable) -> QAction:
        copy_action = QAction("Copy", self.main_window)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(on_copy)
        self.main_window.addAction(copy_action)
        return copy_action

    def _populate_recent_menu(self, menu: QMenu, recent_directories: List[Dict[str, Any]], on_select: Callable):
        menu.clear()
        
        if not recent_directories:
            no_recent_action = QAction("(No Recent Directories)", self.main_window)
            no_recent_action.setEnabled(False)
            menu.addAction(no_recent_action)
        else:
            for entry in recent_directories:
                path = entry.get('path', '')
                include_subdirs = entry.get('include_subdirs', False)
                
                # サブディレクトリ含む場合は表示に[R]を追加
                display_text = f"{path} [R]" if include_subdirs else path
                
                action = QAction(display_text, self.main_window)
                action.triggered.connect(lambda checked, e=entry: on_select(e))
                menu.addAction(action)

    def update_recent_directories_menu(self, recent_directories: List[Dict[str, Any]], on_recent_directory: Callable):
        menubar = self.main_window.menuBar()
        file_menu = menubar.actions()[0].menu()
        
        # Recent Directoriesメニューを探す
        for action in file_menu.actions():
            if action.menu() and action.text() == "Recent Directories":
                self._populate_recent_menu(action.menu(), recent_directories, on_recent_directory)
                break