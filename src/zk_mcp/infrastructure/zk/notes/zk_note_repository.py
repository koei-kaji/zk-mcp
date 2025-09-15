from pathlib import Path

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ....domain.models.notes.note import Note
from ..zk_client import ZkClient


class ZkNoteRepository(IFNoteRepository):
    client: ZkClient

    def find_note_content(self, path: Path) -> Note:
        title = self.client.get_title(path)
        content = self.client.get_content(path)

        return Note(title=title, path=path, content=content)
