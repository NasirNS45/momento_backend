from typing import List, Any, Optional

from django.db.models import QuerySet
from ninja import Schema
from ninja.errors import ValidationError
from ninja.pagination import PaginationBase
from pydantic import Field


class PageNumberPagination(PaginationBase):
    class Input(Schema):
        page: int = Field(1, ge=1)
        page_size: Optional[int] = Field(None, ge=1)

    class Output(Schema):
        page: int
        page_size: int
        total: int
        items: List[Any]

    def paginate_queryset(
        self,
        queryset: QuerySet,
        pagination: Any,
        **params: Any,
    ) -> Any:
        page = pagination.page if pagination.page else 1
        page_size = pagination.page_size if pagination.page_size else 10

        offset = (page - 1) * page_size
        items = queryset[offset : offset + page_size]
        total = queryset.count()
        if page > 1 and items.count() == 0:
            raise ValidationError([{"page": "Invalid page"}])
        return self.Output(
            page=page, page_size=page_size, total=total, items=items
        ).model_dump()
