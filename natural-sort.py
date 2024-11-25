import re
import os
import sys
import argparse
import glob
from pathlib import Path
from itertools import chain


def natural_sort_key(s):
    """
    ファイル名の数値部分を考慮したソートのためのキー関数
    例: 'file-1.jpg' -> ['file-', 1, '.jpg']
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


def list_files_natural_sort(directory='.', patterns=None, recursive=False):
    """
    指定されたディレクトリ内のファイルを自然な順序でソートして表示する

    Args:
        directory (str): リストアップするディレクトリのパス
        patterns (list): 検索パターン（ワイルドカード）のリスト
        recursive (bool): サブディレクトリを含めて検索するかどうか
    """
    try:
        # デフォルトパターンの設定
        if patterns is None:
            patterns = ['*']

        # Pathオブジェクトを作成
        base_path = Path(directory)

        # すべてのパターンに対して検索を実行
        files = set()  # 重複を避けるためにsetを使用
        for pattern in patterns:
            # 検索パターンを構築
            if recursive:
                # サブディレクトリを含む場合は '**' を使用
                search_pattern = f"**/{pattern}"
            else:
                search_pattern = pattern

            # ファイルを検索
            matched_files = [
                str(file_path.relative_to(base_path))
                for file_path in base_path.glob(search_pattern)
                if file_path.is_file()
            ]
            files.update(matched_files)

        # 自然な順序でソート
        sorted_files = sorted(files, key=natural_sort_key)

        # 結果
        if not sorted_files:
            return None

        sorted_files_path = []
        for file in sorted_files:
            sorted_files_path.append((os.path.join(directory, file)))

        return sorted_files_path

    except Exception as e:
        print(f"Error while listing files: {str(e)}", file=sys.stderr)
        raise


def parse_arguments():
    """
    コマンドライン引数を処理する関数

    Returns:
        argparse.Namespace: パースされた引数オブジェクト
    """
    parser = argparse.ArgumentParser(
        description='指定されたディレクトリ内のファイルを自然な順序でソートして表示します。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  %(prog)s -d /path/to/dir                         # 指定ディレクトリ内のすべてのファイルを表示
  %(prog)s -d /path/to/dir -p "*.jpg" "*.jpeg"    # JPGファイルとJPEGファイルを表示
  %(prog)s -d /path/to/dir -r                      # サブディレクトリを含めて表示
  %(prog)s -p "file-*.txt" "data-*.csv"           # 複数のパターンに一致するファイルを表示
  %(prog)s -d /path/to/dir -r -p "*.jpg" "*.png"  # 画像ファイルをサブディレクトリも含めて表示
"""
    )
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='リストアップするディレクトリのパス（デフォルト: カレントディレクトリ）'
    )
    parser.add_argument(
        '-p', '--patterns',
        nargs='+',  # 1つ以上の引数を受け取る
        default=['*'],
        metavar='PATTERN',
        help='検索パターン（ワイルドカード）（複数指定可能、デフォルト: *）'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='サブディレクトリを含めて検索する'
    )
    return parser.parse_args()


if __name__ == "__main__":
    # コマンドライン引数を処理
    args = parse_arguments()

    try:
        # 指定されたディレクトリが存在するか確認
        if not os.path.exists(args.directory):
            raise FileNotFoundError(f"指定されたディレクトリが存在しません: {args.directory}")
        if not os.path.isdir(args.directory):
            raise NotADirectoryError(f"指定されたパスはディレクトリではありません: {args.directory}")

        # パターンを表示
        patterns_str = '" "'.join(args.patterns)
        print(f'Directory "{args.directory}" files matching patterns: "{patterns_str}" in natural sort order:')

        # ディレクトリ内のファイルをリストアップ
        sorted_files = list_files_natural_sort(
            directory=args.directory,
            patterns=args.patterns,
            recursive=args.recursive
        )

        # 結果を表示
        if sorted_files:
            for file in sorted_files:
                print(file)
        else:
            patterns_str = '" "'.join(patterns)
            print(f'No files found matching patterns: "{patterns_str}"')

    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"エラー: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {str(e)}", file=sys.stderr)
        sys.exit(1)
