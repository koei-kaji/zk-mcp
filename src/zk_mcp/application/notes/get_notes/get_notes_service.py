from ..._abc_service import ABCService
from ..if_note_query_service import IFNoteQueryService
from .get_notes_input import GetNotesInput
from .get_notes_output import GetNotesOutput


class GetNotesService(ABCService):
    query_service: IFNoteQueryService

    def handle(self, input: GetNotesInput) -> GetNotesOutput:
        return self.query_service.get_notes(input)
