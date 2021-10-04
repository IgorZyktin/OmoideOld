# -*- coding: utf-8 -*-
"""Data transfer objects.
"""
from typing import Optional

from pydantic import BaseModel


class Query(BaseModel):
    """Data transfer object for query.

    Already parsed one, not like that in the application.
    """
    and_: list[str]
    or_: list[str]
    not_: list[str]
    page: int
    items_per_page: int
    themes: Optional[list[str]]

    def __len__(self) -> int:
        """Return total amount of registered items."""
        return len(self.and_) + len(self.or_) + len(self.not_)

    def __repr__(self) -> str:
        """Return textual representation."""
        return f'<{type(self).__name__}, n={len(self)}>'

    def __bool__(self) -> bool:
        """Return True if query has actual words to search."""
        return bool(self.and_ or self.or_ or self.not_)


class SearchResult(BaseModel):
    """All found resources."""
    items: list[dict]
    report: list[str]


class NewDbPath(BaseModel):
    """New database path."""
    db_path: str
