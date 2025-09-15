from pathlib import Path

from ..._abc_input import ABCInput


class GetNoteContentInput(ABCInput):
    path: Path
