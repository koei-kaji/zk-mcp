from ....domain.models.notes.if_note_repository import IFNoteRepository
from ..._abc_service import ABCService
from .get_note_content_input import GetNoteContentInput
from .get_note_content_output import GetNoteContentOutput


class GetNoteContentService(ABCService):
    repository: IFNoteRepository

    def handle(self, input: GetNoteContentInput) -> GetNoteContentOutput:
        note = self.repository.find_note_content(input.path)

        return GetNoteContentOutput(content=note.content)
