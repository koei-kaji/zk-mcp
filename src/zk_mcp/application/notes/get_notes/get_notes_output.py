from ..._abc_output import ABCOutput
from ..._common.note import Note
from ..._common.pagination import Pagination


class GetNotesOutput(ABCOutput):
    pagination: Pagination
    notes: list[Note]
