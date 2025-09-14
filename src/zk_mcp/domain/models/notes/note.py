from pathlib import Path

from .._entity import Entity


class Note(Entity):
    title: str
    path: Path
