import subprocess
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from models import GetLinkingNotePathsResponse, GetNotePathsResponse, GetTags, Note
from settings import Settings

mcp = FastMCP("Zk")
settings = Settings()  # type: ignore[call-arg]


def _get_notes(cmd_args: list[str]) -> list[Note]:
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
            cwd=str(settings.zk_dir),
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


@mcp.tool()
def get_note_paths(
    include_str: list[str] = [],
    include_str_operand: Literal["AND", "OR"] = "AND",
    exclude_str: list[str] = [],
    include_tags: list[str] = [],
    include_tags_operand: Literal["AND", "OR"] = "AND",
    exclude_tags: list[str] = [],
) -> str:
    """zk CLI を使用してフィルタ条件に一致するノートのパス一覧を取得する。

    Args:
        include_str (list[str]): コンテンツまたはファイル名に含まれる文字列でノートを絞り込む
        include_str_operand (Literal['AND', 'OR']): 複数のinclude_strフィルタに適用する論理演算子（'AND'または'OR'）
        exclude_str (list[str]): コンテンツまたはファイル名にこれらの文字列を含むノートを除外する
        include_tags (list[str]): 指定したタグを持つノートに絞り込む
        include_tags_operand (Literal['AND', 'OR']): 複数のinclude_tagsに適用する論理演算子（'AND'または'OR'）
        exclude_tags (list[str]): 指定したタグを持つノートを除外する

    Returns:
        str: フィルタ条件に一致するノートのファイルパスとタイトル情報リストを含むJSON文字列。
    """
    additional_args: list[str] = []

    if len(include_str) > 0:
        if include_str_operand == "AND":
            delimiter = " "
        else:
            delimiter = " OR "

        con = f"{delimiter}".join(include_str)
        additional_args.extend(["--match", con])

    if len(exclude_str) > 0:
        con = " AND ".join([f"{item}-" for item in exclude_str])
        additional_args.extend(["--match", con])

    if len(include_tags) > 0:
        if include_tags_operand == "AND":
            delimiter = ", "
        else:
            delimiter = " OR "

        con = f"{delimiter}".join(include_tags)
        additional_args.extend(["--tag", con])

    if len(exclude_tags) > 0:
        con = ", ".join([f"-{item}" for item in exclude_tags])
        additional_args.extend(["--tag", con])

    notes = _get_notes(additional_args)

    return GetNotePathsResponse(notes=notes).json()


@mcp.tool()
def get_linking_notes(path: str) -> str:
    """指定されたノートに関連するすべてのリンク情報を取得する。

    このツールは、特定のノートパスに対して以下の3種類のリンク関係を持つノートを検索する：
    1. 指定されたノートからリンクしているノート（link_to）
    2. 指定されたノートにリンクしているノート（linked_by）
    3. 指定されたノートに関連するノート（related）

    Args:
        path (str): リンク情報を取得するノートファイルへのパス

    Returns:
        str: リンク情報を含むJSON文字列。3つの異なるリンクタイプ（link_to_notes, linked_by_notes, related_notes）
            のノートリストが含まれる。
    """
    link_to_notes = _get_notes(["--link-to", path])
    linked_by_notes = _get_notes(["--linked-by", path])
    related_notes = _get_notes(["--related", path])

    return GetLinkingNotePathsResponse(
        link_to_notes=link_to_notes,
        linked_by_notes=linked_by_notes,
        related_notes=related_notes,
    ).json()


@mcp.tool()
def get_tags() -> str:
    command = ["zk", "tag", "list", "--format", "{{name}}"]

    tags: list[str] = []
    try:
        stdout = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(settings.zk_dir),
            check=True,
        )
        results = stdout.stdout.strip().splitlines()

        for line in results:
            tags.append(line)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"zkコマンド実行エラー： {e.stderr}") from e

    return GetTags(tags=tags).json()


@mcp.tool()
def get_note(path: str) -> str:
    """指定されたパスのノートの内容を読み込んで返す。

    Args:
        path (str): 読み込むノートファイルへのパス

    Returns:
        str: ノートのコンテンツ
    """
    note_path = settings.zk_dir / path

    try:
        with open(note_path, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents
    except FileNotFoundError:
        raise RuntimeError(f"ノートが見つかりません: {path}")
    except IOError as e:
        raise RuntimeError(f"ノートの読み込みエラー: {path}") from e


if __name__ == "__main__":
    mcp.run(transport="stdio")
