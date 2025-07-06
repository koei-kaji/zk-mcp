import subprocess
from pathlib import Path

from .models import Note


def get_notes(cwd: Path, cmd_args: list[str]) -> list[Note]:
    """zkコマンドを実行してノート一覧を取得する。

    Args:
        cmd_args: zkコマンドに追加する引数のリスト

    Returns:
        ノートオブジェクトのリスト

    Raises:
        RuntimeError: zkコマンドの実行に失敗した場合
    """
    command = [
        "zk",
        "list",
        "--quiet",
        "--sort",
        "modified-",
        "--limit",
        "50",
        "--format",
        '{{path}}|{{title}}|{{join tags ","}}',
    ] + cmd_args

    try:
        stdout = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True,
        )
        results = stdout.stdout.strip().splitlines()

        notes: list[Note] = []
        for line in results:
            parts = line.split("|", 2)  # (path, title, tags)

            path = parts[0]
            title = parts[1]
            if parts[2] == "":
                tags = []
            else:
                tags = parts[2].split(",")

            note = Note(path=Path(path), title=title, tags=tags)
            notes.append(note)

        return notes
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"zkコマンド実行エラー： {e.stderr}") from e
