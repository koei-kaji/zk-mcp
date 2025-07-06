from pathlib import Path

from ._validate_path import _validate_path
from .get_notes import get_notes
from .models import GetLinkingNotePathsResponse


def get_linking_notes(cwd: Path, path: str) -> str:
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
        _validate_path(path, cwd)

        link_to_notes = get_notes(cwd, ["--link-to", path])
        linked_by_notes = get_notes(cwd, ["--linked-by", path])
        related_notes = get_notes(cwd, ["--related", path])

        return GetLinkingNotePathsResponse(
            link_to_notes=link_to_notes,
            linked_by_notes=linked_by_notes,
            related_notes=related_notes,
        ).json()
    except ValueError as e:
        raise RuntimeError(f"無効なパス: {e}") from e
