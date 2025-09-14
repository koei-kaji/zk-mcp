import abc
from typing import Literal

from ..if_repository import IFRepository


class IFNoteRepository(IFRepository):
    @abc.abstractmethod
    def find_notes(
        page: int = 1,
        per_page: int = 20,
        title_patterns: list[str] = [],
        search_patterns: list[str] = [],
        match_mode: Literal["AND", "OR"] = "AND",
    ) -> : ...
