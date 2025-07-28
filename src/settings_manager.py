import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional


class SettingsManager:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / 'config.json'
        self._default_settings = {
            'window': {
                'x': 100,
                'y': 100,
                'width': 800,
                'height': 600
            },
            'recent_files': [],
            'recent_index': 0,
            'directory_history': [],
        }

    def _get_config_dir(self) -> Path:
        if sys.platform == 'win32':
            config_base = Path.home() / 'AppData' / 'Local'
        elif sys.platform == 'darwin':
            config_base = Path.home() / 'Library' / 'Application Support'
        else:
            config_base = Path.home() / '.config'

        config_dir = config_base / 'ImageViewer'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def load_settings(self) -> Dict[str, Any]:
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._default_settings.copy()
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"設定ファイルの読み込みエラー: {e}")
            return self._default_settings.copy()

    def save_settings(self, settings: Dict[str, Any]):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存エラー: {e}")

    def get_window_geometry(self) -> Dict[str, int]:
        settings = self.load_settings()
        return settings.get('window', self._default_settings['window'])

    def save_window_geometry(self, x: int, y: int, width: int, height: int):
        settings = self.load_settings()
        settings['window'] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.save_settings(settings)

    def get_recent_files(self) -> List[Path]:
        settings = self.load_settings()
        recent_files_str = settings.get('recent_files', [])
        return [Path(f) for f in recent_files_str]

    def get_recent_index(self) -> int:
        settings = self.load_settings()
        return int(settings.get('recent_index', 0))

    def save_recent_files(self, files: List[Path], current_index: int):
        if not files:
            return
            
        settings = self.load_settings()
        settings['recent_files'] = [str(f.resolve()) for f in files]
        settings['recent_index'] = str(current_index)
        self.save_settings(settings)

    def get_directory_history(self) -> List[Dict[str, Any]]:
        settings = self.load_settings()
        history = settings.get('directory_history', [])
        
        # 旧形式（文字列リスト）から新形式（辞書リスト）へ変換
        if history and isinstance(history[0], str):
            history = [{'path': path, 'include_subdirs': False} for path in history]
            settings['directory_history'] = history
            self.save_settings(settings)
        
        return history

    def add_directory_to_history(self, directory_path: str, include_subdirs: bool = False):
        settings = self.load_settings()
        history = self.get_directory_history()
        
        new_entry = {'path': directory_path, 'include_subdirs': include_subdirs}
        
        # 既存の同じパスを削除
        history = [item for item in history if item.get('path') != directory_path]
        
        # 先頭に追加
        history.insert(0, new_entry)
        
        # 最大10個まで保持
        settings['directory_history'] = history[:10]
        self.save_settings(settings)