from pathlib import Path

from pydantic import BaseModel


class Note(BaseModel):
    path: Path
    title: str
    tags: list[str]


class GetNotePathsResponse(BaseModel):
    notes: list[Note]


class GetLinkingNotePathsResponse(BaseModel):
    link_to_notes: list[Note]
    linked_by_notes: list[Note]
    related_notes: list[Note]


class GetTags(BaseModel):
    tags: list[str]
