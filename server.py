from typing import Literal
from mcp.server.fastmcp import FastMCP
import subprocess

mcp = FastMCP("Zk", debug=True)

@mcp.tool()
def get_note_paths(
    include_str: list[str] = [],
    include_str_operand: Literal['AND', 'OR'] = 'AND',
    exclude_str: list[str] = [],
    include_tags: list[str] = [],
    include_tags_operand: Literal['AND', 'OR'] = 'AND',
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
        list[str]: フィルタ条件に一致するノートへのパス一覧。
    """
    additional_args: list[str] = []

    if len(include_str) > 0:
        if include_str_operand == 'AND':
            delimiter = " "
        else:
            delimiter = " OR "

        con = f"{delimiter}".join(include_str)
        additional_args.extend(["--match", con])

    if len(exclude_str) > 0:
        con = " AND ".join([f"{item}-" for item in exclude_str])
        additional_args.extend(["--match", con])

    if len(include_tags) > 0:
        if include_tags_operand == 'AND':
            delimiter = ", "
        else:
            delimiter = " OR "

        con = f"{delimiter}".join(include_tags)
        additional_args.extend(["--tag", con])

    if len(exclude_tags) > 0:
        con = ", ".join([f"-{item}" for item in exclude_str])
        additional_args.extend(["--tag", con])

    result = subprocess.run([
        "zk",
        "list",
        "--quiet",
        "--sort", "modified-",
        "--limit", "50",
        "--format", "path",
    ] + additional_args, capture_output=True, text=True)

    return result.stdout.strip().splitlines()

@mcp.tool()
def get_note(path: str) -> str:
    """指定されたパスのノートの内容を読み込んで返す。

    Args:
        path (str): 読み込むノートファイルへのパス

    Returns:
        str: ノートのコンテンツ
    """
    with open(path, 'r', encoding='utf-8') as f:
        contents = f.read()

    return contents


if __name__ == "__main__":
    mcp.run(transport="stdio")
