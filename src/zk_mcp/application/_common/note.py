from pathlib import Path

from ..._base_models.base_model import BaseFrozenModel


class Note(BaseFrozenModel):
    title: str
    path: Path
