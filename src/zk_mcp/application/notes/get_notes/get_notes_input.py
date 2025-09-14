from typing import Literal

from ..._abc_input import ABCInput


class GetNotesInput(ABCInput):
    page: int = 1
    per_page: int = 10
    title_patterns: list[str]
    search_patterns: list[str]
    match_mode: Literal["AND", "OR"] = "AND"
