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
    """Get a list of note paths that match the filter criteria using zk CLI.

    Args:
        include_str (list[str]): Filter notes by strings contained in content or filename
        include_str_operand (Literal['AND', 'OR']): Logical operator applied to multiple include_str filters ('AND' or 'OR')
        exclude_str (list[str]): Exclude notes containing these strings in content or filename
        include_tags (list[str]): Filter to notes with specified tags
        include_tags_operand (Literal['AND', 'OR']): Logical operator applied to multiple include_tags ('AND' or 'OR')
        exclude_tags (list[str]): Exclude notes with specified tags

    Returns:
        str: JSON string containing a list of note file paths and title information matching the filter criteria.
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
    """Get all linking information related to the specified note.

    This tool searches for notes with the following three types of link relationships to a specific note path:
    1. Notes that the specified note links to (link_to)
    2. Notes that link to the specified note (linked_by)
    3. Notes that are related to the specified note (related)

    Args:
        path (str): Path to the note file to get linking information for

    Returns:
        str: JSON string containing linking information. Includes note lists for three different link types
            (link_to_notes, linked_by_notes, related_notes).
    """
    return tools.get_linking_notes(settings.zk_dir, path)


@mcp.tool()
def get_tags() -> str:
    return tools.get_tags(settings.zk_dir)


@mcp.tool()
def get_note(path: str) -> str:
    """Read and return the contents of the note at the specified path.

    Args:
        path (str): Path to the note file to read

    Returns:
        str: The note content
    """
    return tools.get_note(settings.zk_dir, path)


@mcp.tool()
def create_note(title: str, directory: str = "") -> str:
    """Create a new note with the specified title.

    Args:
        title (str): Title of the note to create
        directory (str): Directory to create the note in (optional)

    Returns:
        str: JSON string containing path information for the created note
    """
    return tools.create_note(settings.zk_dir, title, directory)


if __name__ == "__main__":
    mcp.run(transport="stdio")
