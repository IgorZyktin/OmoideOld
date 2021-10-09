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

    def __str__(self) -> str:
        """Return textual representation."""
        return repr(self)

    def __repr__(self) -> str:
        """Return textual representation."""
        return (f'Query(and_={self.and_!r}, or_={self.or_!r}, '
                f'not_={self.not_!r}, page={self.page}, '
                f'items_per_page={self.items_per_page}, '
                f'themes={self.themes!r})')

    def __bool__(self) -> bool:
        """Return True if query has actual words to search."""
        return bool(self.and_ or self.or_ or self.not_)


class SearchResult(BaseModel):
    """All found resources."""
    items: list[dict]
    report: list[str]
    time: float
    page: int
    total_pages: int
    total_items: int
    announce: str = ''


class NewDbPath(BaseModel):
    """New database path."""
    path: str = ''
