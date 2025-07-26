import random
from pathlib import Path
from typing import List, Optional

from natural_sort import natural_path_sort_key


class ImageListManager:
    def __init__(self):
        self._image_files: List[Path] = []
        self._current_index = 0
        self._shuffle = False
        self._shuffle_table: List[int] = []

    def set_image_files(self, files: List[Path], current_index: int = 0):
        self._image_files = self._filter_image_files(files)
        self._current_index = min(current_index, len(self._image_files) - 1) if self._image_files else 0
        self._generate_shuffle_table()

    def get_image_files(self) -> List[Path]:
        return self._image_files.copy()

    def get_current_index(self) -> int:
        if self._shuffle and self._shuffle_table:
            return self._shuffle_table[self._current_index]
        return self._current_index

    def get_raw_current_index(self) -> int:
        return self._current_index

    def set_current_index(self, index: int):
        if self._image_files:
            self._current_index = max(0, min(index, len(self._image_files) - 1))

    def get_current_image_path(self) -> Optional[Path]:
        if not self._image_files:
            return None
        
        actual_index = self.get_current_index()
        if 0 <= actual_index < len(self._image_files):
            return self._image_files[actual_index]
        return None

    def has_images(self) -> bool:
        return len(self._image_files) > 0

    def get_image_count(self) -> int:
        return len(self._image_files)

    def move_to_next(self):
        if self._image_files:
            self._current_index = (self._current_index + 1) % len(self._image_files)

    def move_to_previous(self):
        if self._image_files:
            self._current_index = (self._current_index - 1) % len(self._image_files)

    def is_shuffle_enabled(self) -> bool:
        return self._shuffle

    def set_shuffle(self, enabled: bool):
        if enabled != self._shuffle:
            if self._shuffle and not enabled:
                actual_index = self._shuffle_table[self._current_index]
                self._current_index = actual_index
            
            self._shuffle = enabled

    def toggle_shuffle(self):
        self.set_shuffle(not self._shuffle)

    def _filter_image_files(self, files: List[Path]) -> List[Path]:
        valid_files = []
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        
        for f in files:
            if not isinstance(f, Path):
                f = Path(f)
            if f.exists() and f.suffix.lower() in supported_extensions:
                valid_files.append(f)
        
        return sorted(valid_files, key=natural_path_sort_key)

    def _generate_shuffle_table(self):
        if not self._image_files:
            self._shuffle_table = []
            return

        n_images = len(self._image_files)
        if n_images > 0:
            sequence = list(range(n_images))
            random.shuffle(sequence)
            self._shuffle_table = sequence
        else:
            self._shuffle_table = []

    def add_files(self, files: List[Path]):
        all_files = self._image_files + files
        self.set_image_files(all_files, self._current_index)