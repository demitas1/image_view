from typing import Callable

from PyQt6.QtWidgets import QMenuBar, QMenu, QMainWindow
from PyQt6.QtGui import QAction, QKeySequence


class UIManager:
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window

    def create_menu_bar(self, 
                       on_open_files: Callable,
                       on_open_directory: Callable) -> QMenuBar:
        menubar = self.main_window.menuBar()

        file_menu = menubar.addMenu("File")

        open_files_action = QAction("Open Files", self.main_window)
        open_files_action.triggered.connect(on_open_files)
        file_menu.addAction(open_files_action)

        open_dir_action = QAction("Open Directory", self.main_window)
        open_dir_action.triggered.connect(on_open_directory)
        file_menu.addAction(open_dir_action)

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