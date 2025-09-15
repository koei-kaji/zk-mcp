import abc
from pathlib import Path

from .._if_repository import IFRepository
from .note import Note


class IFNoteRepository(IFRepository):
    @abc.abstractmethod
    def find_note_content(self, path: Path) -> Note: ...
