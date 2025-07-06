import os.path
import subprocess
from pathlib import Path

from ._validate_directory import _validate_directory
from ._validate_title import _validate_title
from .models import CreateNoteResponse


def create_note(cwd: Path, title: str, directory: str = "") -> str:
    """指定されたタイトルで新しいノートを作成する。

    Args:
        title (str): 作成するノートのタイトル
        directory (str): ノートを作成するディレクトリ（オプション）

    Returns:
        str: 作成されたノートのパス情報を含むJSON文字列
    """
    try:
        # 入力値の検証
        validated_title = _validate_title(title)
        validated_directory = _validate_directory(directory)

        command = ["zk", "new", "--print-path", "--title", validated_title]

        if validated_directory:
            command.extend([validated_directory])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )

        # 作成されたファイルパスを取得
        created_path = result.stdout.strip()

        # ZK_DIRからの相対パスに変換
        relative_path = os.path.relpath(created_path, cwd)

        return CreateNoteResponse(
            path=Path(relative_path), title=validated_title
        ).json()

    except ValueError as e:
        raise RuntimeError(f"入力値エラー: {e}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ノート作成エラー: {e.stderr}") from e
