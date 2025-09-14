import abc

from .._if_query_service import IFQueryService
from .get_notes.get_notes_input import GetNotesInput
from .get_notes.get_notes_output import GetNotesOutput


class IFNoteQueryService(IFQueryService):
    @abc.abstractmethod
    def get_notes(self, input: GetNotesInput) -> GetNotesOutput: ...
