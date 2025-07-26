from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import QFileDialog

from open_dir_dialog import DialogResult, CustomDirectoryDialog


class FileDialogManager:
    @staticmethod
    def select_files() -> Optional[List[Path]]:
        selected_files, _ = QFileDialog.getOpenFileNames(
            None,
            "Select Files",
            "",
            "All Files (*)"
        )
        
        if selected_files:
            return [Path(f) for f in selected_files]
        return None

    @staticmethod
    def select_directory() -> Optional[DialogResult]:
        dialog = CustomDirectoryDialog()
        result = dialog.get_result()
        return result

    @staticmethod
    def get_directory_files(directory: Path, include_subdirs: bool = False) -> List[Path]:
        if not directory.is_dir():
            return []

        if include_subdirs:
            return list(directory.glob('**/*'))
        else:
            return list(directory.glob('*'))