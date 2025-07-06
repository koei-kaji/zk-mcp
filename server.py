from typing import Literal

from mcp.server.fastmcp import FastMCP

import tools
from settings import Settings

mcp = FastMCP("Zk")
settings = Settings()  # type: ignore[call-arg]


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

    return tools.get_note_paths(
        settings.zk_dir,
        include_str,
        include_str_operand,
        exclude_str,
        include_tags,
        include_tags_operand,
        exclude_tags,
    )


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
    return tools.get_linking_notes(settings.zk_dir, path)


@mcp.tool()
def get_tags() -> str:
    return tools.get_tags(settings.zk_dir)


@mcp.tool()
def get_note(path: str) -> str:
    """指定されたパスのノートの内容を読み込んで返す。

    Args:
        path (str): 読み込むノートファイルへのパス

    Returns:
        str: ノートのコンテンツ
    """
    return tools.get_note(settings.zk_dir, path)


@mcp.tool()
def create_note(title: str, directory: str = "") -> str:
    """指定されたタイトルで新しいノートを作成する。

    Args:
        title (str): 作成するノートのタイトル
        directory (str): ノートを作成するディレクトリ（オプション）

    Returns:
        str: 作成されたノートのパス情報を含むJSON文字列
    """
    return tools.create_note(settings.zk_dir, title, directory)


if __name__ == "__main__":
    mcp.run(transport="stdio")
