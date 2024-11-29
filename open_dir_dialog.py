from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QFileDialog, QCheckBox, QVBoxLayout, QWidget,
)


@dataclass
class DialogResult:
    directory: str
    include_subdirs: bool


class CustomDirectoryDialog(QFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Directory")
        self.setFileMode(QFileDialog.FileMode.Directory)
        self.setOption(QFileDialog.Option.ShowDirsOnly)

        # デフォルトのレイアウトを取得
        layout = self.layout()

        # チェックボックスを含む追加のウィジェットを作成
        additional_widget = QWidget()
        additional_layout = QVBoxLayout(additional_widget)

        # チェックボックスの作成と追加
        self.subdirs_checkbox = QCheckBox("Include subdirectories")
        additional_layout.addWidget(self.subdirs_checkbox)
        additional_layout.setContentsMargins(0, 0, 0, 0)

        # 追加のウィジェットをメインレイアウトに追加
        # （FileTypeコンボボックスの下に配置）
        layout.addWidget(additional_widget, 4, 0, 1, -1)

    def get_result(self):
        if self.exec() == QFileDialog.DialogCode.Accepted:
            selected_dirs = self.selectedFiles()
            if selected_dirs:
                return DialogResult(
                    directory=selected_dirs[0],
                    include_subdirs=self.subdirs_checkbox.isChecked()
                )
        return None


