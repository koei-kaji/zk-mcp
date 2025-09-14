import subprocess
from pathlib import Path

from ._validate_path import _validate_path


def get_note(cwd: Path, path: str) -> str:
    """指定されたパスのノートの内容を読み込んで返す。

    Args:
        path (str): 読み込むノートファイルへのパス

    Returns:
        str: ノートのコンテンツ
    """
    command = [
        "zk",
        "list",
        "--quiet",
        "--format",
        "{{raw-content}}",
        path,
    ]

    try:
        _validate_path(path, cwd)

        stdout = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )
        return stdout.stdout
    except ValueError as e:
        raise RuntimeError(f"zkコマンド実行エラー: {e}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"zkコマンド実行エラー: {e.stderr}") from e
