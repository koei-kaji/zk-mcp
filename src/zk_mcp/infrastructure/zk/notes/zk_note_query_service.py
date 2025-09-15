import math
from pathlib import Path
from typing import TypeVar

from ....application._common.note import Note
from ....application._common.pagination import Pagination
from ....application.notes.get_notes.get_notes_input import GetNotesInput
from ....application.notes.get_notes.get_notes_output import GetNotesOutput
from ....application.notes.if_note_query_service import IFNoteQueryService
from ..zk_client import ZkClient

T = TypeVar("T")


class ZkNoteQueryService(IFNoteQueryService):
    client: ZkClient

    def _paginate(
        self, items: list[T], page: int, per_page: int
    ) -> tuple[list[T], Pagination]:
        total = len(items)
        total_pages = math.ceil(total / per_page) if per_page > 0 else 1

        # ページ番号の正規化
        page = max(1, min(page, total_pages))

        # スライス計算
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_items = items[start_idx:end_idx]

        pagination = Pagination(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return paginated_items, pagination

    def get_notes(self, input: GetNotesInput) -> GetNotesOutput:
        conditions: list[str] = []

        # title の検索条件を追加
        for t in input.title_patterns:
            conditions.append(f"title: {t}")

        # 全文検索の検索条件を追加
        conditions.extend(input.search_patterns)

        results = self.client.get_lists(
            "{{path}}|{{title}}", ["--match", f" {input.match_mode} ".join(conditions)]
        )

        notes: list[Note] = []
        for result in results:
            # パイプ文字を含むタイトルに対応するため、逆方向から分割
            pipe_idx = result.rfind("|")
            if pipe_idx == -1:
                continue  # パイプが見つからない場合はスキップ

            path = result[:pipe_idx]
            title = result[pipe_idx + 1 :]
            note = Note(title=title, path=Path(path))
            notes.append(note)

        paginated_notes, pagination = self._paginate(notes, input.page, input.per_page)

        return GetNotesOutput(pagination=pagination, notes=paginated_notes)
