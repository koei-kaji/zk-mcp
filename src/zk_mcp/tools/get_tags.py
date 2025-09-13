import subprocess
from pathlib import Path

from .models import GetTags


def get_tags(cwd: Path) -> str:
    command = ["zk", "tag", "list", "--format", "{{name}}"]

    tags: list[str] = []
    try:
        stdout = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            check=True,
        )
        results = stdout.stdout.strip().splitlines()

        for line in results:
            tags.append(line)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"zkコマンド実行エラー: {e.stderr}") from e

    return GetTags(tags=tags).model_dump_json()
