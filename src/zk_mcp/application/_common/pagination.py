from ..._base_models.base_model import BaseFrozenModel


class Pagination(BaseFrozenModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
