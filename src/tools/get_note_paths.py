from pathlib import Path
from typing import Literal

from ._validate_path import _validate_path
from .get_notes import get_notes
from .models import GetNotePathsResponse


def get_note_paths(
    cwd: Path,
    path: str | None = None,
    include_str: list[str] = [],
    include_str_operand: Literal["AND", "OR"] = "AND",
    exclude_str: list[str] = [],
    include_tags: list[str] = [],
    include_tags_operand: Literal["AND", "OR"] = "AND",
    exclude_tags: list[str] = [],
) -> str:
    """zk CLI を使用してフィルタ条件に一致するノートのパス一覧を取得する。

    Args:
        include_str (list[str]): コンテンツまたはファイル名に含まれる
            文字列でノートを絞り込む
        include_str_operand (Literal['AND', 'OR']): 複数のinclude_str
            フィルタに適用する論理演算子('AND'または'OR')
        exclude_str (list[str]): コンテンツまたはファイル名に
            これらの文字列を含むノートを除外する
        include_tags (list[str]): 指定したタグを持つノートに絞り込む
        include_tags_operand (Literal['AND', 'OR']): 複数のinclude_tags
            に適用する論理演算子('AND'または'OR')
        exclude_tags (list[str]): 指定したタグを持つノートを除外する

    Returns:
        str: フィルタ条件に一致するノートのファイルパスとタイトル
            情報リストを含むJSON文字列。
    """
    additional_args: list[str] = []

    if path is not None:
        _validate_path(path, cwd)
        additional_args.extend([path])

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

    notes = get_notes(cwd, additional_args)

    return GetNotePathsResponse(notes=notes).model_dump_json()
