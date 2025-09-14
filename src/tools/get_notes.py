import subprocess
from pathlib import Path

from .models import Note


def get_notes(cwd: Path, cmd_args: list[str]) -> list[Note]:
    """zkコマンドを実行してファイル一覧を取得する。

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
        *cmd_args,
    ]

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
            # パイプ文字を含むタイトルに対応するため、逆方向から分割
            # 最後のパイプでtagsを、最初のパイプでpathを分離
            last_pipe_idx = line.rfind("|")
            if last_pipe_idx == -1:
                continue  # パイプが見つからない場合はスキップ

            tags_part = line[last_pipe_idx + 1 :]
            remaining = line[:last_pipe_idx]

            first_pipe_idx = remaining.find("|")
            if first_pipe_idx == -1:
                continue  # パイプが見つからない場合はスキップ

            path = remaining[:first_pipe_idx]
            title = remaining[first_pipe_idx + 1 :]

            if tags_part == "":
                tags = []
            else:
                tags = tags_part.split(",")

            note = Note(path=Path(path), title=title, tags=tags)
            notes.append(note)

        return notes
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"zkコマンド実行エラー: {e.stderr}") from e
