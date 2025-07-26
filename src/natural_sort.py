import re
import os
from typing import List, Union


def natural_sort_key_component(s: str) -> List[Union[str, int]]:
    """
    文字列内の数値部分を考慮したソートのためのキー関数
    例: 'file-1.jpg' -> ['file-', 1, '.jpg']

    Args:
        s (str): ソート対象の文字列

    Returns:
        List[Union[str, int]]: 文字列を数値とテキストに分割したリスト
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def natural_path_sort_key(path: str) -> List[List[Union[str, int]]]:
    """
    ファイルパス全体に対して自然順ソートのためのキー関数を提供します。
    パスの各コンポーネント（ディレクトリ名、ファイル名）にnatural sortを適用します。

    Args:
        path (str): ソート対象のファイルパス

    Returns:
        List[List[Union[str, int]]]: パスの各コンポーネントをnatural sortしたリストのリスト

    Example:
        '/path/dir-2/file-1.jpg' -> [
            ['path'],
            ['dir-', 2],
            ['file-', 1, '.jpg']
        ]
    """
    # パスを正規化してコンポーネントに分割
    normalized_path = os.path.normpath(path)
    components = normalized_path.split(os.sep)

    # 各コンポーネントにnatural sort keyを適用
    return [natural_sort_key_component(component) for component in components]
