from pathlib import Path

from zk_mcp.application.notes.get_notes.get_notes_input import GetNotesInput
from zk_mcp.application.notes.get_notes.get_notes_output import GetNotesOutput
from zk_mcp.application.notes.get_notes.get_notes_service import GetNotesService
from zk_mcp.infrastructure.zk.notes.zk_note_query_service import ZkNoteQueryService
from zk_mcp.infrastructure.zk.zk_client import ZkClient


def main() -> None:
    client = ZkClient(cwd=Path("/Users/koei-kaji/src/github.com/koei-kaji/note-zk"))
    query_service = ZkNoteQueryService(client)
    service = GetNotesService(query_service=query_service)

    input = GetNotesInput(title_patterns=[], search_patterns=[])
    output = service.handle(input)

    print(output)


if __name__ == "__main__":
    main()
