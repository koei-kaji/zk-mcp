from pathlib import Path
from typing import Optional

from .._entity import Entity


class Note(Entity):
    title: str
    path: Path
    content: Optional[str] = None
