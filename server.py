import os.path
import subprocess
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

from models import (
    CreateNoteResponse,
    GetLinkingNotePathsResponse,
    GetNotePathsResponse,
    GetTags,
    Note,
)
from settings import Settings

mcp = FastMCP("Zk")
settings = Settings()  # type: ignore[call-arg]


def _validate_path(path: str) -> Path:
    """パスの安全性を検証し、ディレクトリトラバーサル攻撃を防ぐ。
    
    Args:
        path: 検証するパス文字列
        
    Returns:
        Path: 検証済みの安全なパス
        
    Raises:
        ValueError: パスが安全でない場合
    """
    # 空文字列チェック
    if not path or not path.strip():
        raise ValueError("パスが空です")
    
    # パス長制限
    if len(path) > 1000:
        raise ValueError("パスが長すぎます")
    
    # 相対パスに変換
    normalized_path = Path(path).resolve()
    zk_dir_resolved = settings.zk_dir.resolve()
    
    # zkディレクトリ内のパスかチェック
    try:
        normalized_path.relative_to(zk_dir_resolved)
    except ValueError:
        raise ValueError("指定されたパスはzkディレクトリ外です")
    
    # 実際のファイルパスを返す
    return settings.zk_dir / path


def _validate_directory(directory: str) -> str:
    """ディレクトリ名の安全性を検証し、コマンドインジェクション攻撃を防ぐ。
    
    Args:
        directory: 検証するディレクトリ名
        
    Returns:
        str: 検証済みの安全なディレクトリ名
        
    Raises:
        ValueError: ディレクトリ名が安全でない場合
    """
    # 空文字列の場合は許可
    if not directory:
        return directory
    
    # ディレクトリ名の長さ制限
    if len(directory) > 200:
        raise ValueError("ディレクトリ名が長すぎます")
    
    # 危険な文字をチェック
    dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '[', ']', '>', '<', '!', '~', '*', '?', '"', "'", '\\']
    for char in dangerous_chars:
        if char in directory:
            raise ValueError(f"ディレクトリ名に危険な文字が含まれています: {char}")
    
    # パストラバーサル防止
    if '..' in directory or directory.startswith('/'):
        raise ValueError("ディレクトリ名にパストラバーサルが検出されました")
    
    # 制御文字チェック
    if any(ord(char) < 32 for char in directory):
        raise ValueError("ディレクトリ名に制御文字が含まれています")
    
    return directory


def _validate_title(title: str) -> str:
    """タイトルの安全性を検証し、コマンドインジェクション攻撃を防ぐ。
    
    Args:
        title: 検証するタイトル
        
    Returns:
        str: 検証済みの安全なタイトル
        
    Raises:
        ValueError: タイトルが安全でない場合
    """
    # 空文字列チェック
    if not title or not title.strip():
        raise ValueError("タイトルが空です")
    
    # タイトルの長さ制限
    if len(title) > 500:
        raise ValueError("タイトルが長すぎます")
    
    # 制御文字チェック
    if any(ord(char) < 32 for char in title if char not in ['\t', '\n', '\r']):
        raise ValueError("タイトルに制御文字が含まれています")
    
    return title


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
    try:
        # パスの安全性を検証
        _validate_path(path)
        
        link_to_notes = _get_notes(["--link-to", path])
        linked_by_notes = _get_notes(["--linked-by", path])
        related_notes = _get_notes(["--related", path])

        return GetLinkingNotePathsResponse(
            link_to_notes=link_to_notes,
            linked_by_notes=linked_by_notes,
            related_notes=related_notes,
        ).json()
    except ValueError as e:
        raise RuntimeError(f"無効なパス: {e}") from e


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
    try:
        # パスの安全性を検証
        note_path = _validate_path(path)
        
        with open(note_path, "r", encoding="utf-8") as f:
            contents = f.read()
        return contents
    except ValueError as e:
        raise RuntimeError(f"無効なパス: {e}") from e
    except FileNotFoundError:
        raise RuntimeError(f"ノートが見つかりません: {path}")
    except IOError as e:
        raise RuntimeError(f"ノートの読み込みエラー: {path}") from e


@mcp.tool()
def create_note(title: str, directory: str = "") -> str:
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
            cwd=str(settings.zk_dir),
            check=True,
        )

        # 作成されたファイルパスを取得
        created_path = result.stdout.strip()

        # ZK_DIRからの相対パスに変換
        relative_path = os.path.relpath(created_path, settings.zk_dir)

        return CreateNoteResponse(path=Path(relative_path), title=validated_title).json()

    except ValueError as e:
        raise RuntimeError(f"入力値エラー: {e}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ノート作成エラー: {e.stderr}") from e


if __name__ == "__main__":
    mcp.run(transport="stdio")
