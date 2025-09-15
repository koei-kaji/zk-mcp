from pathlib import Path
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from zk_mcp.application.notes.get_note_content.get_note_content_input import (
    GetNoteContentInput,
)
from zk_mcp.application.notes.get_note_content.get_note_content_service import (
    GetNoteContentService,
)
from zk_mcp.application.notes.get_notes.get_notes_input import GetNotesInput
from zk_mcp.application.notes.get_notes.get_notes_service import GetNotesService
from zk_mcp.infrastructure.zk.notes.zk_note_query_service import ZkNoteQueryService
from zk_mcp.infrastructure.zk.notes.zk_note_repository import ZkNoteRepository
from zk_mcp.infrastructure.zk.zk_client import ZkClient
from zk_mcp.settings import Settings

mcp = FastMCP("Zk")
settings = Settings()  # type: ignore[call-arg]
client = ZkClient(cwd=settings.zk_dir)
query_service = ZkNoteQueryService(client=client)
repository = ZkNoteRepository(client=client)


@mcp.tool()
def get_notes(
    page: Annotated[int, Field(description="page")] = 1,
    per_page: Annotated[int, Field(description="per_page")] = 1,
    title_patterns: Annotated[list[str], Field(description="title_patterns")] = [],
    search_patterns: Annotated[list[str], Field(description="search_patterns")] = [],
    match_mode: Annotated[
        Literal["AND", "OR"], Field(description="match_mode")
    ] = "AND",
) -> dict:
    service = GetNotesService(query_service=query_service)

    input = GetNotesInput(title_patterns=[], search_patterns=[])
    output = service.handle(input)

    return output.model_dump()


@mcp.tool()
def get_note_content(path: Annotated[Path, Field(description="path")]) -> str:
    service = GetNoteContentService(repository=repository)

    input = GetNoteContentInput(path=path)
    output = service.handle(input)

    return output.model_dump()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
